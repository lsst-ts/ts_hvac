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

__all__ = ["SimClient"]

import asyncio
from collections import deque
import json
import logging
import random

import paho.mqtt.client as mqtt

from lsst.ts.hvac.hvac_enums import TOPICS_ALWAYS_ENABLED
from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader


class SimClient:
    """Simulator to act as MQTT Client.

    Parameters
    ----------
    start_publish_telemetry_every_second: `bool`
        Start publishing telemetry every second or not. Defaults to True and
        unit tests should set it to False.
    """

    def __init__(self, start_publish_telemetry_every_second=True):
        self.log = logging.getLogger("SimClient")
        self.hvac_topics = {}
        self.telemetry_task = None
        self.connected = False

        # Holds the incoming messages so the CSC can take them from the Queue.
        self.msgs = deque()

        # Holds info on which topics are enabled and which not.
        self.topics_enabled = {}

        # Holds the values received via configuration commands.
        self.configuration_values = {}

        # Helper for reading the HVAC data
        self.xml = MqttInfoReader()

        self.start_publish_telemetry_every_second = start_publish_telemetry_every_second
        # Incoming command messages get published or not. Should only be
        # modified by unit tests.
        self.is_published = True

        self.log.info("SimClient constructed")

    async def connect(self):
        """Start publishing telemetry."""
        # Make sure that all topics and their items are loaded.
        self.xml.collect_hvac_topics_and_items_from_json()
        self.hvac_topics = self.xml.hvac_topics
        self._collect_topics()

        if self.start_publish_telemetry_every_second:
            self.telemetry_task = asyncio.create_task(
                self._publish_telemetry_every_second()
            )

        self.connected = True
        self.log.info("Connected.")

    async def disconnect(self):
        """Stop publishing telemetry."""
        if self.telemetry_task:
            self.telemetry_task.cancel()
        self.connected = False
        self.log.info("Disconnected.")

    def _collect_topics(self):
        """Loop over all topics and initialize them."""
        topics = self.xml.get_generic_hvac_topics()
        for topic in topics:
            self.topics_enabled[topic] = False
        for topic in TOPICS_ALWAYS_ENABLED:
            self.topics_enabled[topic] = True

    def publish_mqtt_message(self, topic, payload):
        """Publish the specified payload to the specified topic.

        A topic represents an MQTT topic including the command to execute.
        Two types of commands exist in the real MQTT server: enable commands
        and configuration commands. The enable commands accept a boolean and
        the configuration commands accept a float.

        Parameters
        ----------
        topic: `str`
            The topic to publish to.
        payload: `str`
            The payload to publish. This corresponds to a boolean for the
            enable commands and a float for the configuration commands.

        Returns
        -------
        is_published: `bool`
            In general True gets returned since the messages always arrive but
            this can be overridden by unit tests.

        Raises
        ------
        ValueError
            In case a topic doesn't exist.
        """
        self.log.debug(f"Recevied message on topic {topic} with payload {payload}")
        topic, command = self.xml.extract_topic_and_item(topic)
        if command == "COMANDO_ENCENDIDO_LSST":
            self._handle_enable_command(topic, json.loads(payload))
        else:
            self._handle_config_command(topic, command, json.loads(payload))
        # For now, always return True. It is unclear if the real MQTT server
        # ever returns False and once that is clear this will be adapted.
        return self.is_published

    def _handle_enable_command(self, topic, payload):
        """Enable or disable the topic based on the payload.

        Parameters
        ----------
        topic: `str`
            The name of the topic to enable or disable.
        payload: `bool`
            Whether the topic should be enabled or disabled.
        """
        self.topics_enabled[topic] = payload

    def _handle_config_command(self, topic, command, payload):
        """Receive the config command for the topic and verify that the
        corresponding telmetry item exists.

        Parameters
        ----------
        topic: `str`
            The name of the topic to configure.
        command: `str`
            The command representing the name of the item to configure.
        payload: `bool` or `float`
            The configuration value of the item.

        Raises
        ------
        ValueError
            In case the item doesn't exist in the topic.
        """
        self.log.info(
            f"Received message [topic={topic!r}, command={command!r}, payload={payload!r}]"
        )
        command_item = command
        # TODO: These command items do not have a telemetry counter point in
        #  the "Lower" components. It is being clarified how to verify them so
        #  they are skipped for now.
        if (
            command_item
            in [
                "SETPOINT_VENTILADOR_MIN_LSST",
                "SETPOINT_VENTILADOR_MAX_LSST",
            ]
            and topic.startswith("LSST/PISO05/MANEJADORA/LOWER")
        ):
            self.log.info(f"topic={topic!r}, command={command!r}, payload={payload!r}")
            return
        if command_item.endswith("_LSST"):
            command_item = command_item[:-5]
        self.configuration_values[f"{topic}/{command_item}"] = payload

    async def _publish_telemetry_every_second(self):
        """Publish telmetry every second to simulate the behaviour of an MQTT
        server.
        """
        try:
            while True:
                self.publish_telemetry()
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            # Normal exit
            pass
        except Exception:
            self.log.exception("publish_telemetry() failed")

    def publish_telemetry(self):
        """Publish telmetry once to simulate the behaviour of an MQTT
        server.
        """
        for hvac_topic in self.hvac_topics:
            topic, variable = self.xml.extract_topic_and_item(hvac_topic)

            topic_enabled = self.topics_enabled[topic]
            topic_type = self.hvac_topics[hvac_topic]["topic_type"]
            idl_type = self.hvac_topics[hvac_topic]["idl_type"]
            limits = self.hvac_topics[hvac_topic]["limits"]
            value = None
            if topic_enabled:
                if hvac_topic in self.configuration_values.keys():
                    value = self.configuration_values[hvac_topic]
                elif topic_type == "READ":
                    if idl_type == "boolean":
                        value = True

                        # Making sure that no alarm bells start ringing.
                        if "ALARM" in variable:
                            value = False
                    else:
                        value = random.randint(10 * limits[0], 10 * limits[1]) / 10.0
            else:
                if topic_type == "READ":
                    if idl_type == "boolean":
                        value = False

            if value is not None:
                msg = mqtt.MQTTMessage(topic=hvac_topic.encode())
                msg.payload = json.dumps(value)
                self.msgs.append(msg)
