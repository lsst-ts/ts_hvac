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
import functools
import json
import re

import numpy as np

from .config_schema import CONFIG_SCHEMA
from . import __version__
from lsst.ts import salobj
from lsst.ts.hvac.hvac_enums import CommandItem, HvacTopic, TelemetryItem
from lsst.ts.hvac.mqtt_client import MqttClient
from lsst.ts.hvac.simulator.sim_client import SimClient
from lsst.ts.hvac.xml.mqtt_info_reader import (
    MqttInfoReader,
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITHOUT_CONFIGURATION,
)

# The number of seconds to collect the state of the HVAC system for before the
# median is reported via SAL telemetry.
HVAC_STATE_TRACK_PERIOD = 5

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
        self._add_sal_commands()
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
        self.xml.collect_hvac_topics_and_items_from_json()
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

    def _compute_statistics_and_send_telemetry(self):
        self.log.info(
            f"{HVAC_STATE_TRACK_PERIOD} seconds have passed since the last "
            f"computation of the medians, so computing now."
        )
        for topic in self.hvac_state:
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

    def _add_sal_commands(self):
        # This adds the do_foo_enable commands.
        for topic in HvacTopic:
            if topic.value not in TOPICS_ALWAYS_ENABLED:
                method_name = f"do_{topic.name}_enable"
                method = functools.partial(self._do_enable, topic=topic)
                setattr(self, method_name, method)

        # This adds the do_foo_config commands.
        for topic in HvacTopic:
            if topic.value not in TOPICS_WITHOUT_CONFIGURATION:
                method_name = f"do_{topic.name}_config"
                method = functools.partial(self._do_config, topic=topic)
                setattr(self, method_name, method)

    def _do_enable(self, data, topic):
        """Send a MQTT message to enable or disable a system.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        topic: `HvacTopic`
            The HvacTopic used to determine what MQTT topic to send the data
            to.
        """
        self.assert_enabled()
        # Publish the data to the MQTT topic and receive confirmation whether
        # the publication was done correctly.
        was_published = self.mqtt_client.publish_mqtt_message(
            topic.value + "/" + CommandItem.comandoEncendido.value,
            json.dumps(data.comandoEncendido),
        )
        # Do some housekeeping if the message was sent correctly.
        if was_published:
            value = data.comandoEncendido
            telemetry_item = TelemetryItem.comandoEncendido.value
            if topic.name in TOPICS_WITHOUT_COMANDO_ENCENDIDO:
                telemetry_item = TelemetryItem.estadoFuncionamiento.value
            self.hvac_state[topic.value][telemetry_item].initial_value = value
        else:
            # TODO: DM-28028
            pass

    def _do_config(self, data, topic):
        """Send a MQTT message to configure a system.

        Parameters
        ----------
        data: Any
            The data to send. This is the data received via SAL.
        topic: `HvacTopic`
            The HvacTopic used to determine what MQTT topic to send the data
            to.
        """
        self.assert_enabled()
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
        # TODO: DM-28028: Handling of was_published will come at a later point.
