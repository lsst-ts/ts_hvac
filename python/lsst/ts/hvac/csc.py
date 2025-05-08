# This file is part of ts_hvac.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["HvacCsc", "run_hvac"]

import asyncio
import enum
import json
import logging
import math
import traceback
import typing
from types import SimpleNamespace

from lsst.ts import salobj, utils
from lsst.ts.xml.enums.HVAC import DeviceId, DynaleneTankLevel

from . import __version__
from .base_mqtt_client import BaseMqttClient
from .enums import (
    DEVICE_GROUPS_ENGLISH,
    DYNALENE_COMMAND_ITEMS_ENGLISH,
    DYNALENE_EVENT_GROUP_DICT,
    EVENT_TOPIC_DICT_ENGLISH,
    STRINGS_THAT_CANNOT_BE_DECODED_BY_JSON,
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITH_DATA_IN_BAR,
    TOPICS_WITH_DATA_IN_PSI,
    TOPICS_WITHOUT_COMANDO_ENCENDIDO_ENGLISH,
    TOPICS_WITHOUT_CONFIGURATION,
    CommandItemEnglish,
    EventItem,
    HvacTopicEnglish,
    TelemetryItemEnglish,
)
from .mqtt_client import MqttClient
from .mqtt_info_reader import MqttInfoReader
from .simulator.sim_client import SimClient
from .utils import bar_to_pa, psi_to_pa, to_camel_case

# The number of seconds to collect the state of the HVAC system for before the
#  telemetry is sent.
HVAC_STATE_TRACK_PERIOD = 1


def run_hvac() -> None:
    asyncio.run(HvacCsc.amain(index=None))


class InternalItemState:
    """Container for the state of the item of a general MQTT topic. A general
    topic represents an MQTT subsystem (chiller, fan, pump, etc) and an item a
    value reported by the subsystem (temperature, pressure, etc).

    Parameters
    ----------
    topic: `str`
        A general MQTT topic, e.g. "LSST/PISO01/CHILLER_01". See
        `HvacTopic`/`HvacTopicEnglish` for possible values.
    item: `str`
        A value reported by the subsystem, e.g. "TEMPERATURA_AMBIENTE". See
        `TelemetryItem`/`TelemetryItemEnglish` for possible values.
    data_type: `str`
        The data type of the item. Can be "float" or "boolean".
    """

    def __init__(self, topic: str, item: str, data_type: str) -> None:
        self.topic = topic
        self.item = item
        # A list of float or bool as collected since the last median was
        # computed.
        self.recent_values: list[float | bool] = []
        # Keeps track of the data type so no medians are being computed for
        # bool values.
        self.data_type = data_type

    def __str__(self) -> str:
        return (
            f"InternalItemState["
            f"topic={self.topic}, "
            f"item={self.item}, "
            f"recent_values={self.recent_values}, "
            f"data_type={self.data_type}, "
            f"]"
        )

    def get_most_recent_value(self) -> None | float | bool:
        """Get the most recent boolean value.
        values.

        Returns
        -------
        recent_value: `bool`
            The most recent value.
        """
        recent_values = self._get_and_reset_recent()
        if not recent_values:
            return None
        most_recent_value = recent_values[-1]
        self.recent_values.append(most_recent_value)
        return most_recent_value

    def _get_and_reset_recent(self) -> list[float | bool]:
        recent_values = self.recent_values
        self.recent_values = []
        return recent_values


class HvacCsc(salobj.BaseCsc):
    """Commandable SAL Component for the HVAC (Heating, Ventilation and Air
    Conditioning).

    Parameters
    ----------
    initial_state : `salobj.State`
        The initial state of the CSC
    simulation_mode : `int`
         Simulation mode. Allowed values:

        * 0: regular operation.
        * 1: simulation: use a mock low level HVAC controller.

    start_telemetry_publishing: `bool`
        Indicate if the simulator should start publishing telemetry or not and
        if the CSC should start a task for publishing telemetry on a regular
        basis. This should be set to False for unit tests and True for all
        other situations.
    """

    enable_cmdline_state = True
    valid_simulation_modes = (0, 1)
    version = __version__

    def __init__(
        self,
        initial_state: salobj.State = salobj.State.STANDBY,
        simulation_mode: int = 0,
        start_telemetry_publishing: bool = True,
    ) -> None:
        # Helper for reading the HVAC data
        self.xml = MqttInfoReader()

        self._add_config_commands()
        self._add_dynalene_commands()
        super().__init__(
            name="HVAC",
            index=0,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
        )

        self.start_telemetry_publishing = start_telemetry_publishing
        self.telemetry_task = utils.make_done_future()
        self.mqtt_client: BaseMqttClient | None = None

        # Keep track of the internal state of the MQTT topics. This will
        # collect all values for the duration of HVAC_STATE_TRACK_PERIOD before
        # the median is sent via SAL telemetry. The structure is
        # "topic" : {
        #     "item": InternalItemState
        # }
        # and this gets initialized in the connect method.
        self.hvac_state: dict[str, typing.Any] = {}

        # The host and port to connect to.
        self.host = "hvac.cp.lsst.org"
        self.port = 1883

        # Keep track of the device indices for the device mask
        self.device_id_index = {dev_id: i for i, dev_id in enumerate(DeviceId)}

        # Keep track of event data to suppress superfluous events.
        self.event_data: dict[str, dict[str, typing.Any]] = {}

    async def connect(self) -> None:
        """Start the HVAC MQTT client or start the mock client, if in
        simulation mode.
        """

        # Initialize interal state track keeping
        self._setup_hvac_state()

        if self.simulation_mode == 1:
            # Use the Simulator Client.
            self.mqtt_client = SimClient(self.log, self.start_telemetry_publishing)
            self.log.info("Connecting SimClient.")
        else:
            # Use the MQTT Client.
            self.log.info(
                f"Connecting MqttClient to host {self.host} and port {self.port}."
            )
            self.mqtt_client = MqttClient(host=self.host, port=self.port, log=self.log)

        try:
            await self.mqtt_client.connect()
        except TimeoutError as e:
            self.log.exception(f"Timeout connecting to host {self.host}")
            raise e
        if self.start_telemetry_publishing:
            self.telemetry_task = asyncio.create_task(
                self._publish_telemetry_regularly()
            )
        self.log.info("Connected.")

    async def disconnect(self) -> None:
        """Disconnect the HVAQ client, if connected."""
        self.log.info("Disconnecting")
        if not self.telemetry_task.done() and not self.telemetry_task.cancelled():
            self.telemetry_task.cancel()
        assert self.mqtt_client is not None
        await self.mqtt_client.disconnect()

    def _setup_hvac_state(self) -> None:
        """Set up internal tracking of the MQTT state."""
        self.hvac_state = {}
        mqtt_topics_and_items = self.xml.get_telemetry_mqtt_topics_and_items()
        for mqtt_topic, items in mqtt_topics_and_items.items():
            topic_state = {}
            for item in items:
                topic_state[item] = InternalItemState(
                    mqtt_topic, item, items[item]["idl_type"]
                )
            self.hvac_state[mqtt_topic] = topic_state

    async def begin_enable(self, id_data: salobj.BaseDdsDataType) -> None:
        """Begin do_enable; called before state changes.

        This method sends a CMD_INPROGRESS signal.

        Parameters
        ----------
        id_data: `CommandIdData`
            Command ID and data
        """
        await super().begin_enable(id_data)
        await self.cmd_enable.ack_in_progress(id_data, timeout=60)

    async def end_enable(self, id_data: salobj.BaseDdsDataType) -> None:
        """End do_enable; called after state changes but before command
        acknowledged.

        This method connects to the HVAC server.

        Parameters
        ----------
        id_data: `CommandIdData`
            Command ID and data
        """
        if not self.connected:
            await self.connect()
        await super().end_enable(id_data)

    async def begin_disable(self, id_data: salobj.BaseDdsDataType) -> None:
        """Begin do_disable; called before state changes.

        This method disconnects from the HVAC server.

        Parameters
        ----------
        id_data: `CommandIdData`
            Command ID and data
        """
        await self.cmd_disable.ack_in_progress(id_data, timeout=60)
        await super().begin_disable(id_data)

    async def end_disable(self, id_data: salobj.BaseDdsDataType) -> None:
        """End do_disable; called after state changes but before command
        acknowledged.

        This method disconnects from the HVAC server.

        Parameters
        ----------
        id_data: `CommandIdData`
            Command ID and data
        """
        await self.disconnect()
        await super().end_disable(id_data)

    def _get_topic_enabled_state(self, topic: str) -> typing.Tuple[int, bool]:
        """Determine whether a device represented by the MQTT topic is enabled
        or not.

        Parameters
        ----------
        topic: `str`
            An MQTT topic representing a device.

        Returns
        -------
        device_id_index: `int`
            The index of the device in the `lsst.ts.idl.enums.HVAC.DeviceId`
            enum.
        enabled: `bool`
            Whether the device is enabled or not.
        """
        enabled = False
        device_id_index = 0
        hvac_topic = HvacTopicEnglish(topic).name
        device_id = DeviceId[hvac_topic]
        device_id_index = self.device_id_index[device_id]

        item = "COMANDO_ENCENDIDO"
        if hvac_topic in TOPICS_WITHOUT_COMANDO_ENCENDIDO_ENGLISH:
            item = "ESTADO_FUNCIONAMIENTO"
        if topic in TOPICS_ALWAYS_ENABLED:
            enabled = True
        else:
            enabled = False
            if len(self.hvac_state[topic][item].recent_values) > 0:
                enabled = self.hvac_state[topic][item].recent_values[-1]

        return device_id_index, enabled

    async def _send_telemetry(self) -> None:
        enabled_mask = 0b0
        for topic in self.hvac_state:
            device_id_index, enabled = self._get_topic_enabled_state(topic)
            if enabled:
                enabled_mask += 1 << device_id_index
            data: dict[str, float | bool] = {}
            for item in self.hvac_state[topic]:
                info = self.hvac_state[topic][item]
                value = info.get_most_recent_value()
                if value is not None:
                    if item == "ESTADO_DE_UNIDAD":
                        item_name = TelemetryItemEnglish("ESTADO_UNIDAD").name
                    elif item == "MODO_OPERACION_UNIDAD":
                        item_name = TelemetryItemEnglish("MODO_OPERACION").name
                    else:
                        item_name = TelemetryItemEnglish(item).name
                    data[item_name] = value

            telemetry_method = getattr(self, "tel_" + HvacTopicEnglish(topic).name)
            hvac_topic_name = HvacTopicEnglish(topic).name
            hvac_topic_value = HvacTopicEnglish(topic).value
            if data:
                await telemetry_method.set_write(**data)
            device_id = DeviceId[hvac_topic_name]
            await self.send_events(
                topic, enabled, hvac_topic_name, hvac_topic_value, device_id, data
            )

        await self.evt_deviceEnabled.set_write(device_ids=enabled_mask)
        self.log.debug("Done.")

    async def send_events(
        self,
        topic: str,
        enabled: bool,
        hvac_topic_name: str,
        hvac_topic_value: str,
        device_id: DeviceId,
        data: dict[str, float | bool],
    ) -> None:
        if topic not in TOPICS_WITHOUT_CONFIGURATION and enabled:
            command_group = [
                k for k, v in DEVICE_GROUPS_ENGLISH.items() if hvac_topic_value in v
            ][0]
            event_name = f"evt_{to_camel_case(command_group, True)}Configuration"
            command_group_coro = getattr(self, event_name)
            event_data = {"device_id": device_id}
            command_topics = self.xml.command_topics[hvac_topic_name]
            for command_topic in command_topics:
                # skip topics that are not reported
                if command_topic not in [
                    "switchOn",
                    "maxFanSetpoint",
                    "minFanSetpoint",
                ]:
                    if command_topic == "openColdValve":
                        data_item = "coldValveOpening"
                    else:
                        data_item = command_topic
                    event_data[command_topic] = data[data_item]
            event_data_key = f"{event_name}:{device_id}"
            cached_event_data = self.event_data.get(event_data_key)
            if event_data != cached_event_data:
                await command_group_coro.set_write(**event_data)
            self.event_data[event_data_key] = event_data

    async def _handle_mqtt_messages(self) -> None:
        self.log.debug("Handling MQTT messages.")
        assert self.mqtt_client is not None
        while len(self.mqtt_client.msgs) != 0:
            msg = self.mqtt_client.msgs.popleft()
            self.log.debug(f"Processing topic={msg.topic!r}, payload={msg.payload!r}.")
            topic_and_item: str = msg.topic
            if msg.payload in STRINGS_THAT_CANNOT_BE_DECODED_BY_JSON:
                payload = msg.payload.decode("utf-8")
            else:
                try:
                    payload = json.loads(msg.payload)
                except json.decoder.JSONDecodeError:
                    self.log.exception(
                        f"Exception decoding topic {msg.topic} "
                        f"payload {msg.payload}. Continuing."
                    )
                    continue

            topic, item = self.xml.extract_topic_and_item(topic_and_item)

            # Prepare the HVAC event if the message applies to one.
            event_items = [
                event_item for event_item in EventItem if event_item.value == item
            ]
            if len(event_items) > 0:
                try:
                    event_item = event_items[0]
                    event_name = f"evt_{HvacTopicEnglish(topic).name}"
                    event = getattr(self, event_name)
                    if event_item.name in event.topic_info.fields:
                        if event_name not in self.event_data:
                            self.event_data[event_name] = {}
                        self.event_data[event_name][event_item.name] = payload
                        continue
                except ValueError:
                    self.log.warning(
                        f"Ignoring unknown {topic=} for {topic_and_item=}."
                    )

            # DM-39103 Workaround for unknown or misspelled topic and item
            # names.
            if topic not in self.hvac_state or item not in self.hvac_state[topic]:
                self.log.warning(
                    f"Ignoring unknown {topic=} and {item=} for {topic_and_item=}."
                )
                continue

            # Some Dynalene event topics need to be grouped together, which is
            # what these next lines do.
            for dyn_event_grp in DYNALENE_EVENT_GROUP_DICT:
                if topic_and_item.endswith(dyn_event_grp):
                    # First set the correct event group. See
                    # EVENT_TOPIC_DICT/EVENT_TOPIC_DICT_ENGLISH for the event
                    # groups.
                    topic_and_item = topic_and_item.replace(
                        dyn_event_grp,
                        DYNALENE_EVENT_GROUP_DICT[dyn_event_grp],
                    )

                    # Then set the correct payload value.
                    # There are two types of events in three groups. In all
                    # cases all MQTT topics in the group are received and each
                    # one is converted to a generic alarm. Only one of these
                    # MQTT topics is received at a time but eventually all MQTT
                    # topics in a group are recevied. In the code only the
                    # cases where the payload needs to be changed are
                    # considered, since the others are evident.

                    # The first type has one MQTT topic that ends in "ON" and
                    # one in "OFF". There are two groups of these events and
                    # for them the following applies:
                    # * If ON==True and OFF==False, the alarm state is True.
                    # * If ON==False and OFF==True, the alarm state is False.
                    # It is not verifed that if one is True, the other is
                    # False.
                    if dyn_event_grp.endswith("OFF") or dyn_event_grp.endswith("ON"):
                        # The net result is negating the payload of the "OFF"
                        # MQTT topic.
                        if dyn_event_grp.endswith("OFF") and payload is False:
                            payload = True
                        elif dyn_event_grp.endswith("OFF") and payload is True:
                            payload = False

                    # The second type has three MQTT topics, one for each alarm
                    # level of OK, Warning and Alarm. At a given time only one
                    # of the three should be True and the other two False. This
                    # is not verified.
                    else:
                        if dyn_event_grp.endswith("OK") and payload is True:
                            payload = DynaleneTankLevel.OK.value
                        elif dyn_event_grp.endswith("Warning") and payload is True:
                            payload = DynaleneTankLevel.Warning.value
                        else:
                            payload = DynaleneTankLevel.Alarm.value
                    break

            # Some Dynalene topics need to be emitted as events rather than as
            # telemetry. This next if statement takes care of that.
            if topic_and_item in EVENT_TOPIC_DICT_ENGLISH:
                event_name = EVENT_TOPIC_DICT_ENGLISH[topic_and_item]["event"]
                event = getattr(self, event_name)
                await event.set_write(state=int(payload))
                continue

            item_state = self.hvac_state[topic][item]
            if payload in [
                "Automatico",
                "Encendido$20Manual",
                "Apagado$20Manual",
            ] or (isinstance(payload, str) and "AUTOMATICO" in payload):
                self.log.debug(f"Translating {payload=!s} to True.")
                payload = True
            if topic_and_item in TOPICS_WITH_DATA_IN_BAR:
                self.log.debug(f"Converting {topic_and_item} from bar to Pa.")
                payload = bar_to_pa(float(payload))
            if topic_and_item in TOPICS_WITH_DATA_IN_PSI:
                self.log.debug(f"Converting {topic_and_item} from PSI to Pa.")
                payload = psi_to_pa(float(payload))

            item_state.recent_values.append(payload)

        for hvac_topic in HvacTopicEnglish:  # type: ignore
            event_name = f"evt_{hvac_topic.name}"
            event = getattr(self, event_name, None)  # type: ignore
            if event:
                if event_name in self.event_data:
                    self.log.debug(
                        f"Writing {event_name=} with data {self.event_data[event_name]}."
                    )
                    await event.set_write(**self.event_data[event_name])
                else:
                    logging.warning(f"No data for {event_name=}.")

        self.log.debug("Done.")

    async def publish_telemetry(self) -> None:
        await self._handle_mqtt_messages()
        await self._send_telemetry()

    async def _publish_telemetry_regularly(self) -> None:
        try:
            while True:
                await self.publish_telemetry()
                await asyncio.sleep(HVAC_STATE_TRACK_PERIOD)
        except asyncio.CancelledError:
            # Normal exit
            pass
        except Exception as e:
            self.log.exception("Exception and this was unexpected.")
            await self.fault(
                -1, "Error publishing telemetry.", traceback.format_exception(e)
            )

    @property
    def connected(self) -> bool:
        if self.mqtt_client is None:
            return False
        return self.mqtt_client.connected

    def _add_config_commands(self) -> None:
        command_groups = set(
            k
            for k, v in DEVICE_GROUPS_ENGLISH.items()
            for i in v
            if i not in TOPICS_WITHOUT_CONFIGURATION
        )
        # This adds the do_configFoos functions.
        for command_group in command_groups:
            if command_group == "DYNALENE":
                continue
            function_name = f"do_config{to_camel_case(command_group)}"
            setattr(self, function_name, self._do_config)

    def _add_dynalene_commands(self) -> None:
        for command in DYNALENE_COMMAND_ITEMS_ENGLISH:
            function_name = f"do_{command}"
            setattr(self, function_name, self._do_dynalene_command)

    async def do_disableDevice(self, data: SimpleNamespace) -> None:
        """Disable the specified device.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        """
        self._set_enabled_state(data, False)

    async def do_enableDevice(self, data: SimpleNamespace) -> None:
        """Enable the specified device.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        """
        self._set_enabled_state(data, True)

    def _set_enabled_state(self, data: SimpleNamespace, enabled: bool) -> None:
        """Send an MQTT message to enable or disable a system.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        enabled: bool
            True for enabled and False for disabled
        """
        self.assert_enabled()
        device_id = DeviceId(data.device_id)

        hvac_topic_name = HvacTopicEnglish[device_id.name].name
        hvac_topic_value = HvacTopicEnglish[device_id.name].value
        command_item = CommandItemEnglish.switchOn.value

        # Publish the data to the MQTT topic and receive confirmation whether
        # the publication was done correctly.
        assert self.mqtt_client is not None
        was_published = self.mqtt_client.publish_mqtt_message(
            hvac_topic_value + "/" + command_item,
            json.dumps(enabled),
        )

        # Do some housekeeping if the message was sent correctly.
        if was_published:
            telemetry_item = TelemetryItemEnglish.switchedOn.value
            if hvac_topic_name in TOPICS_WITHOUT_COMANDO_ENCENDIDO_ENGLISH:
                telemetry_item = TelemetryItemEnglish.workingState.value
            self.hvac_state[hvac_topic_value][telemetry_item].initial_value = enabled
        else:
            # TODO: DM-28028: Handling of was_published == False will come at
            #  a later point.
            pass

    async def _do_config(self, data: SimpleNamespace) -> None:
        """Send an MQTT message to configure a system.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        topic: `HvacTopicEnglish`
            The HvacTopicEnglish used to determine what MQTT topic to send the
            data to.
        """
        self.assert_enabled()
        device_id = DeviceId(data.device_id)

        topic_value = HvacTopicEnglish[device_id.name].value
        command_enum: enum.EnumType = CommandItemEnglish

        # Publish the data to the MQTT topics and receive confirmation whether
        # the publications were done correctly.
        mqtt_topics_and_items = self.xml.get_command_mqtt_topics_and_items()
        items = mqtt_topics_and_items[topic_value]
        was_published = {}
        assert self.mqtt_client is not None
        for item in items:
            if item not in ["COMANDO_ENCENDIDO_LSST"]:
                command_item = command_enum(item)  # type: ignore
                value = getattr(data, command_item.name)
                if isinstance(value, float) and math.isnan(value):
                    continue
                was_published[command_item.name] = (
                    self.mqtt_client.publish_mqtt_message(
                        topic_value + "/" + command_item.value,
                        json.dumps(value),
                    )
                )
                if not was_published:
                    # TODO: DM-28028: Handling of was_published == False will
                    #  come at a later point.
                    pass

    async def _do_dynalene_command(self, data: SimpleNamespace) -> None:
        self.assert_enabled()
        data_dict = data.get_vars() if hasattr(data, "get_vars") else vars(data)

        dci_dict = DYNALENE_COMMAND_ITEMS_ENGLISH
        device_groups = DEVICE_GROUPS_ENGLISH
        command_enum: enum.EnumType = CommandItemEnglish

        command_item = [dci for dci in dci_dict if dci in data_dict][0]
        topic = device_groups["DYNALENE"][0] + "/" + command_enum[command_item].value  # type: ignore
        value = getattr(data, command_item)
        assert self.mqtt_client is not None
        was_published = self.mqtt_client.publish_mqtt_message(
            topic,
            json.dumps(value),
        )

        if was_published:
            log_event = getattr(self, f"evt_{command_item}")
            for data_item in data_dict:
                setattr(log_event.data, data_item, getattr(data, data_item))
            await log_event.set_write()
        else:
            # TODO: DM-28028: Handling of was_published == False will come at
            #  a later point.
            pass
