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

__all__ = ["HvacCsc", "run_hvac", "TOPICS_WITHOUT_COMANDO_ENCENDIDO"]

import asyncio
import json
import traceback
import typing
from types import SimpleNamespace

import numpy as np
from lsst.ts import salobj, utils
from lsst.ts.idl.enums.HVAC import DEVICE_GROUPS, DeviceId

from . import __version__
from .enums import (
    EVENT_TOPIC_DICT,
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITHOUT_CONFIGURATION,
    CommandItem,
    HvacTopic,
    TelemetryItem,
)
from .mqtt_client import MqttClient
from .mqtt_info_reader import MqttInfoReader
from .simulator.sim_client import SimClient
from .utils import bar_to_pa, psi_to_pa, to_camel_case

# The number of seconds to collect the state of the HVAC system for before the
# median is reported via SAL telemetry.
HVAC_STATE_TRACK_PERIOD = 60

# These subsystems do not report COMANDO_ENCENDIDO but ESTADO_FUNCIONAMIENTO
TOPICS_WITHOUT_COMANDO_ENCENDIDO = frozenset(
    (
        "manejadoraLower01P05",
        "manejadoraLower02P05",
        "manejadoraLower03P05",
        "manejadoraLower04P05",
    )
)

# These strings cannot be decoded by JSON and need to be treated separately.
STRINGS_THAT_CANNOT_BE_DECODED_BY_JSON = {
    b"AUTOMATICO {ok} @ 10",
}

# For these topics, the data are in bar which need to be converted to Pa.
TOPICS_WITH_DATA_IN_BAR = frozenset(
    (
        "LSST/PISO01/CHILLER_01/PRESION_BAJA_CTO1",
        "LSST/PISO01/CHILLER_01/PRESION_BAJA_CTO2",
        "LSST/PISO01/CHILLER_02/PRESION_BAJA_CTO1",
        "LSST/PISO01/CHILLER_02/PRESION_BAJA_CTO2",
        "LSST/PISO01/CHILLER_03/PRESION_BAJA_CTO1",
        "LSST/PISO01/CHILLER_03/PRESION_BAJA_CTO2",
    )
)

# For these topics, the data are in PSI which need to be converted to Pa.
TOPICS_WITH_DATA_IN_PSI = frozenset(
    (
        "LSST/PISO05/DYNALENE/DynTMAsupPS01",
        "LSST/PISO05/DYNALENE/DynTMAretPS02",
        "LSST/PISO05/DYNALENE/DynTAsupPS03",
        "LSST/PISO05/DYNALENE/DynTAretPS04",
        "LSST/PISO05/DYNALENE/DCH01supPS11",
        "LSST/PISO05/DYNALENE/DCH02supPS13",
    )
)


def run_hvac() -> None:
    asyncio.run(HvacCsc.amain(index=None))


class InternalItemState:
    """Container for the state of the item of a general MQTT topic. A general
    topic represents an MQTT subsystem (chiller, fan, pump, etc) and an item a
    value reported by the subsystem (temperature, pressure, etc).

    Parameters
    ----------
    topic: `str`
        A general MQTT topic, e.g. "LSST/PISO01/CHILLER_01". See `HvacTopic`
        for possible values.
    item: `str`
        A value reported by the subsystem, e.g. "TEMPERATURA_AMBIENTE". See
        `TelemetryItem` for possible values.
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

    @property
    def is_float(self) -> bool:
        return self.data_type == "float"

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

    def compute_recent_median(self) -> None | float:
        """Computes the median of the most recently acquired float values.

        Returns
        -------
        recent_median: `float`
            The median of the most recent values.
        """
        recent_values = self._get_and_reset_recent()
        if not recent_values:
            return None
        median = float(np.median(recent_values))  # keep MyPy happy.
        self.recent_values.append(median)
        return median

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
        self._add_config_commands()
        super().__init__(
            name="HVAC",
            index=0,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
        )

        self.start_telemetry_publishing = start_telemetry_publishing
        self.telemetry_task = utils.make_done_future()
        self.mqtt_client: SimClient | MqttClient = SimClient(
            self.start_telemetry_publishing
        )

        # Keep track of the internal state of the MQTT topics. This will
        # collect all values for the duration of HVAC_STATE_TRACK_PERIOD before
        # the median is sent via SAL telemetry. The structure is
        # "topic" : {
        #     "item": InternalItemState
        # }
        # and this gets initialized in the connect method.
        self.hvac_state: dict[str, typing.Any] = {}

        # The host and port to connect to.
        self.host = "hvac01.cp.lsst.org"
        self.port = 1883

        # Helper for reading the HVAC data
        self.xml = MqttInfoReader()

        # Keep track of the device indices for the device mask
        self.device_id_index = {dev_id: i for i, dev_id in enumerate(DeviceId)}

    async def connect(self) -> None:
        """Start the HVAC MQTT client or start the mock client, if in
        simulation mode.
        """

        # Initialize interal state track keeping
        self._setup_hvac_state()

        if self.simulation_mode == 1:
            # Use the Simulator Client.
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
        if self.connected:
            self.log.info("Disconnecting")
            self.telemetry_task.cancel()
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
        if self.connected:
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
        deviceId_index: `int`
            The index of the device in the `lsst.ts.idl.enums.HVAC.DeviceId`
            enum.
        enabled: `bool`
            Whether the device is enabled or not.
        """
        enabled = False
        deviceId_index = 0
        hvac_topic = HvacTopic(topic)
        device_id = DeviceId[hvac_topic.name]
        deviceId_index = self.device_id_index[device_id]

        item = "COMANDO_ENCENDIDO"
        if hvac_topic.name in TOPICS_WITHOUT_COMANDO_ENCENDIDO:
            item = "ESTADO_FUNCIONAMIENTO"
        if topic in TOPICS_ALWAYS_ENABLED:
            enabled = True
        else:
            enabled = False
            if len(self.hvac_state[topic][item].recent_values) > 0:
                enabled = self.hvac_state[topic][item].recent_values[-1]

        return deviceId_index, enabled

    async def _compute_statistics_and_send_telemetry(self) -> None:
        self.log.debug(
            f"{HVAC_STATE_TRACK_PERIOD} seconds have passed since the last "
            f"computation of the medians, so computing now."
        )
        enabled_mask = 0b0
        for topic in self.hvac_state:
            deviceId_index, enabled = self._get_topic_enabled_state(topic)
            if enabled:
                enabled_mask += 1 << deviceId_index
            data: dict[str, float | bool] = {}
            for item in self.hvac_state[topic]:
                info = self.hvac_state[topic][item]
                if info.is_float:
                    value = info.compute_recent_median()
                else:
                    value = info.get_most_recent_value()
                if value is not None:
                    data[TelemetryItem(item).name] = value

            if data:
                telemetry_method = getattr(self, "tel_" + HvacTopic(topic).name)
                await telemetry_method.set_write(**data)
            hvac_topic = HvacTopic(topic)
            device_id = DeviceId[hvac_topic.name]
            if topic not in TOPICS_WITHOUT_CONFIGURATION and enabled:
                command_group = [
                    k for k, v in DEVICE_GROUPS.items() if hvac_topic.value in v
                ][0]
                command_group_coro = getattr(
                    self, f"evt_{to_camel_case(command_group, True)}Configuration"
                )
                event_data = {"device_id": device_id}
                command_topics = self.xml.command_topics[hvac_topic.name]
                for command_topic in command_topics:
                    # skip topics that are not reported
                    if command_topic not in [
                        "comandoEncendido",
                        "setpointVentiladorMax",
                        "setpointVentiladorMin",
                    ]:
                        event_data[command_topic] = data[command_topic]
                await command_group_coro.set_write(**event_data)

        await self.evt_deviceEnabled.set_write(device_ids=enabled_mask)
        self.log.debug("Done.")

    async def _handle_mqtt_messages(self) -> None:
        self.log.debug("Handling MQTT messages.")
        while not len(self.mqtt_client.msgs) == 0:
            msg = self.mqtt_client.msgs.popleft()
            topic_and_item = msg.topic
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

            # DM-39103 Workaround for unknown or misspelled topic and item
            # names.
            if topic not in self.hvac_state or item not in self.hvac_state[topic]:
                self.log.warning(f"Ignoring unknown {topic=} and {item=}.")
                continue

            # Some Dynalene topics need to be emitted as events rather than as
            # telemetry. This next if statement takes care of that.
            if topic_and_item in EVENT_TOPIC_DICT:
                event_name = EVENT_TOPIC_DICT[topic_and_item]["event"]
                event = getattr(self, event_name)
                await event.set_write(state=payload)
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
        self.log.debug("Done.")

    async def publish_telemetry(self) -> None:
        await self._handle_mqtt_messages()
        await self._compute_statistics_and_send_telemetry()

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
        # Find all device groups that can be commanded.
        command_groups = set(
            k
            for k, v in DEVICE_GROUPS.items()
            for i in v
            if i not in TOPICS_WITHOUT_CONFIGURATION
        )
        # This adds the do_configFoos functions.
        for command_group in command_groups:
            function_name = f"do_config{to_camel_case(command_group)}s"
            setattr(self, function_name, self._do_config)

    def do_disableDevice(self, data: SimpleNamespace) -> None:
        """Disable the specified device.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        """
        self._set_enabled_state(data, False)

    def do_enableDevice(self, data: SimpleNamespace) -> None:
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
        hvac_topic = HvacTopic[device_id.name]
        # Publish the data to the MQTT topic and receive confirmation whether
        # the publication was done correctly.
        was_published = self.mqtt_client.publish_mqtt_message(
            hvac_topic.value + "/" + CommandItem.comandoEncendido.value,
            json.dumps(enabled),
        )
        # Do some housekeeping if the message was sent correctly.
        if was_published:
            telemetry_item = TelemetryItem.comandoEncendido.value
            if hvac_topic.name in TOPICS_WITHOUT_COMANDO_ENCENDIDO:
                telemetry_item = TelemetryItem.estadoFuncionamiento.value
            self.hvac_state[hvac_topic.value][telemetry_item].initial_value = enabled
        else:
            # TODO: DM-28028: Handling of was_published == False will come at
            #  a later point.
            pass

    def _do_config(self, data: SimpleNamespace) -> None:
        """Send an MQTT message to configure a system.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        topic: `HvacTopic`
            The HvacTopic used to determine what MQTT topic to send the data
            to.
        """
        self.assert_enabled()
        device_id = DeviceId(data.device_id)
        topic = HvacTopic[device_id.name]
        # Publish the data to the MQTT topics and receive confirmation whether
        # the publications were done correctly.
        mqtt_topics_and_items = self.xml.get_command_mqtt_topics_and_items()
        items = mqtt_topics_and_items[topic.value]
        was_published = {}
        for item in items:
            if item not in ["COMANDO_ENCENDIDO_LSST"]:
                command_item = CommandItem(item)
                was_published[
                    command_item.name
                ] = self.mqtt_client.publish_mqtt_message(
                    topic.value + "/" + command_item.value,
                    json.dumps(getattr(data, command_item.name)),
                )
        else:
            # TODO: DM-28028: Handling of was_published == False will come at
            #  a later point.
            pass
