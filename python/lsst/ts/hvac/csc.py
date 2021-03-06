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

__all__ = ["HvacCsc", "TOPICS_WITHOUT_COMANDO_ENCENDIDO"]

import asyncio
import json
import re

import numpy as np

from .config_schema import CONFIG_SCHEMA
from . import __version__
from .enums import (
    CommandItem,
    HvacTopic,
    TelemetryItem,
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITHOUT_CONFIGURATION,
)
from .utils import to_camel_case
from .mqtt_client import MqttClient
from .simulator.sim_client import SimClient
from .mqtt_info_reader import MqttInfoReader
from lsst.ts import salobj
from lsst.ts.idl.enums.HVAC import DeviceId, DEVICE_GROUPS

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

    def __init__(self, topic, item, data_type):
        self.topic = topic
        self.item = item
        # A list of float or bool as collected since the last median was
        # computed.
        self.recent_values = []
        # Keeps track of the data type so no medians are being computed for
        # bool values.
        self.data_type = data_type

    def __str__(self):
        return (
            f"InternalItemState["
            f"topic={self.topic}, "
            f"item={self.item}, "
            f"recent_values={self.recent_values}, "
            f"data_type={self.data_type}, "
            f"]"
        )

    @property
    def is_float(self):
        return self.data_type == "float"

    def get_most_recent_value(self):
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
        return recent_values[-1]

    def compute_recent_median(self):
        """Computes the median of the most recently acquired float values.

        Returns
        -------
        recent_median: `float`
            The median of the most recent values.
        """
        recent_values = self._get_and_reset_recent()
        if not recent_values:
            return None
        return np.median(recent_values)

    def _get_and_reset_recent(self):
        recent_values = self.recent_values
        self.recent_values = []
        return recent_values


class HvacCsc(salobj.ConfigurableCsc):
    """Commandable SAL Component for the HVAC (Heating, Ventilation and Air
    Conditioning).

    Parameters
    ----------
    config_dir : `string`
        The configuration directory
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

    valid_simulation_modes = (0, 1)
    version = __version__

    def __init__(
        self,
        config_dir=None,
        initial_state=salobj.State.STANDBY,
        simulation_mode=0,
        start_telemetry_publishing=True,
    ):
        self.config = None
        self._config_dir = config_dir
        self._add_config_commands()
        super().__init__(
            name="HVAC",
            index=0,
            config_schema=CONFIG_SCHEMA,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
        )

        self.mqtt_client = None
        self.start_telemetry_publishing = start_telemetry_publishing
        self.telemetry_task = salobj.make_done_future()

        # Keep track of the internal state of the MQTT topics. This will
        # collect all values for the duration of HVAC_STATE_TRACK_PERIOD before
        # the median is sent via SAL telemetry. The structure is
        # "topic" : {
        #     "item": InternalItemState
        # }
        # and this gets initialized in the connect method.
        self.hvac_state = None

        # Helper for reading the HVAC data
        self.xml = MqttInfoReader()

        # Keep track of the device indices for the device mask
        self.device_id_index = {dev_id: i for i, dev_id in enumerate(DeviceId)}

        self.log.info("HvacCsc constructed")

    async def connect(self):
        """Start the HVAC MQTT client or start the mock client, if in
        simulation mode.
        """
        self.log.info("Connecting.")
        self.log.info(self.config)
        self.log.info(f"self.simulation_mode = {self.simulation_mode}")
        if self.config is None:
            raise RuntimeError("Not yet configured")
        if self.connected:
            raise RuntimeError("Already connected")

        # Initialize interal state track keeping
        self._setup_hvac_state()

        if self.simulation_mode == 1:
            # Use the Simulator Client.
            self.log.info("Connecting to SimClient.")
            self.mqtt_client = SimClient(self.start_telemetry_publishing)
        else:
            # Use the MQTT Client.
            self.log.info("Connecting to MqttClient.")
            self.mqtt_client = MqttClient(host=self.config.host, port=self.config.port)

        await self.mqtt_client.connect()
        if self.start_telemetry_publishing:
            self.telemetry_task = asyncio.create_task(
                self._publish_telemetry_regularly()
            )
        self.log.info("Connected.")

    async def disconnect(self):
        """Disconnect the HVAQ client, if connected."""
        if self.connected:
            self.log.info("Disconnecting")
            self.telemetry_task.cancel()
            await self.mqtt_client.disconnect()

    def _setup_hvac_state(self):
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

    async def handle_summary_state(self):
        """Override of the handle_summary_state function to connect or
        disconnect to the HVAC server (or the mock server) when needed.
        """
        self.log.info(f"handle_summary_state {self.summary_state}")
        if self.disabled_or_enabled:
            if not self.connected:
                await self.connect()
        else:
            await self.disconnect()

    async def configure(self, config):
        self.config = config

    def _get_topic_enabled_state(self, topic):
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

        if topic in TOPICS_ALWAYS_ENABLED:
            enabled = True
        elif hvac_topic.name in TOPICS_WITHOUT_COMANDO_ENCENDIDO:
            enabled = self.hvac_state[topic]["ESTADO_FUNCIONAMIENTO"].recent_values[-1]
        else:
            enabled = self.hvac_state[topic]["COMANDO_ENCENDIDO"].recent_values[-1]

        return deviceId_index, enabled

    def _compute_statistics_and_send_telemetry(self):
        self.log.info(
            f"{HVAC_STATE_TRACK_PERIOD} seconds have passed since the last "
            f"computation of the medians, so computing now."
        )
        enabled_mask = 0b0
        for topic in self.hvac_state:
            deviceId_index, enabled = self._get_topic_enabled_state(topic)
            if enabled:
                enabled_mask += 1 << deviceId_index
            data = {}
            for item in self.hvac_state[topic]:
                info = self.hvac_state[topic][item]
                if info.is_float:
                    value = info.compute_recent_median()
                else:
                    value = info.get_most_recent_value()
                if value is not None:
                    data[TelemetryItem(item).name] = value

            self.log.info(f"{topic}:{data}")
            if data:
                telemetry_method = getattr(self, "tel_" + HvacTopic(topic).name)
                telemetry_method.set_put(**data)
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
                command_group_coro.set_put(**event_data)

        self.evt_deviceEnabled.set_put(device_ids=enabled_mask)

    def _handle_mqtt_messages(self):
        while not len(self.mqtt_client.msgs) == 0:
            msg = self.mqtt_client.msgs.popleft()
            topic_and_item = msg.topic
            payload = msg.payload

            topic, item = self.xml.extract_topic_and_item(topic_and_item)
            topic = re.sub(r"PISO([1-9])", r"PISO0\1", topic)
            if topic == "LSST/PISO04/MANEJADORA/SBLANCA":
                topic = "LSST/PISO04/MANEJADORA/GENERAL/SBLANCA"
            if topic == "LSST/PISO04/MANEJADORA/SLIMPIA":
                topic = "LSST/PISO04/MANEJADORA/GENERAL/SLIMPIA"
            if item == "SET_POINT_COOLING":
                item = "SETPOINT_COOLING"
            if item == "SET_POINT_HEATING":
                item = "SETPOINT_HEATING"
            item_state = self.hvac_state[topic][item]
            value = payload
            if payload not in [
                b"Automatico",
                b"Encendido$20Manual",
                b"Apagado$20Manual",
            ]:
                value = json.loads(payload)

            item_state.recent_values.append(value)

    def publish_telemetry(self):
        self._handle_mqtt_messages()
        self._compute_statistics_and_send_telemetry()

    async def _publish_telemetry_regularly(self):
        try:
            while True:
                self.publish_telemetry()
                await asyncio.sleep(HVAC_STATE_TRACK_PERIOD)
        except asyncio.CancelledError:
            # Normal exit
            pass
        except Exception:
            self.log.exception("get_telemetry() failed")

    @property
    def connected(self):
        if self.mqtt_client is None:
            return False
        return self.mqtt_client.connected

    @staticmethod
    def get_config_pkg():
        return "ts_config_ocs"

    def _add_config_commands(self):
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

    def do_disableDevice(self, data):
        """Disable the specified device.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        """
        self._set_enabled_state(data, False)

    def do_enableDevice(self, data):
        """Enable the specified device.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        """
        self._set_enabled_state(data, True)

    def _set_enabled_state(self, data, enabled):
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

    def _do_config(self, data):
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
