# This file is part of ts_hvac.
#
# Developed for the Vera Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the Vera Rubin Observatory
# Project (https://www.lsst.org).
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

from lsst.ts.hvac.xml import hvac_mqtt_to_SAL_XML as xml


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

        self.start_publish_telemetry_every_second = start_publish_telemetry_every_second
        # Incoming command messages get published or not. Should only be
        # modified by unit tests.
        self.is_published = True

        self.log.info("SimClient constructed")

    async def connect(self):
        """Start publishing telemetry.
        """
        # Make sure that all topics and their items are loaded.
        xml.collect_topics_and_items()
        self.hvac_topics = xml.hvac_topics
        self._collect_topics()

        if self.start_publish_telemetry_every_second:
            self.telemetry_task = asyncio.create_task(
                self._publish_telemetry_every_second()
            )

        self.connected = True
        self.log.info("Connected.")

    async def disconnect(self):
        """Stop publishing telemetry.
        """
        if self.telemetry_task:
            self.telemetry_task.cancel()
        self.connected = False
        self.log.info("Disconnected.")

    def _collect_topics(self):
        """Loop over all topics and initialize them.
        """
        topics = xml.get_topics()
        for topic in topics:
            self.topics_enabled[topic] = False
        for topic in xml.TOPICS_ALWAYS_ENABLED:
            self.topics_enabled[topic] = True

    def publish_mqtt_message(self, topic, payload):
        """Publish the specified payload to the specified topic.

        A topic represents a topic including the command to execute.
        Several commands exist in the real MQTT server but for now only
        COMANDO_ENCENDIDO_LSST is supported in this simulator. This command
        accepts either True or False and enables or disables the topic.

        Parameters
        ----------
        topic: `str`
            The topic to publish to.
        payload: `str`
            The payload to publish.

        Returns
        -------
        is_published: `bool`
            In general True gets returned since the messages always arrive but
            this can be overridden by unit tests.

        Raises
        ------
        ValueError
            In case a topic doesn't exist.
        ValueError
            In case a different command than COMANDO_ENCENDIDO_LSST is
            received.
        """
        self.log.debug(f"Recevied message on topic {topic} with payload {payload}")
        topic, command = xml.extract_topic_and_item(topic)
        if command != "COMANDO_ENCENDIDO_LSST":
            raise ValueError(f"Command {command} not supported on topic {topic}")
        value = json.loads(payload)
        self.topics_enabled[topic] = value
        return self.is_published

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
            topic, variable = xml.extract_topic_and_item(hvac_topic)

            topic_enabled = self.topics_enabled[topic]
            topic_type = self.hvac_topics[hvac_topic]["topic_type"]
            idl_type = self.hvac_topics[hvac_topic]["idl_type"]
            limits = self.hvac_topics[hvac_topic]["limits"]
            if topic_enabled:
                if topic_type == "READ":
                    if idl_type == "boolean":
                        value = True

                        # Making sure that no alarm bells start ringing.
                        if "ALARM" in variable:
                            value = False
                    else:
                        value = random.randint(10 * limits[0], 10 * limits[1]) / 10.0
                    msg = mqtt.MQTTMessage(topic=hvac_topic.encode())
                    msg.payload = json.dumps(value)
                    self.msgs.append(msg)
            else:
                if topic_type == "READ":
                    if idl_type == "boolean":
                        value = False
                        msg = mqtt.MQTTMessage(topic=hvac_topic.encode())
                        msg.payload = json.dumps(value)
                        self.msgs.append(msg)
