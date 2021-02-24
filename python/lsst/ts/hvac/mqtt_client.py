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

__all__ = ["MqttClient"]

from collections import deque
import logging

import paho.mqtt.client as mqtt

LSST_CLIENT_ID = "LSST"
LSST_GENERAL_TOPIC = "LSST/#"


class MqttClient:
    """Client class to connect to the HVAC MQTT server.

    Parameters
    ----------
    host: `str`
        The hostname of the MQTT server.
    port: `int`
        The port of the MQTT service.
    """

    def __init__(self, host, port):
        self.log = logging.getLogger("MqttClient")
        self.host = host
        self.port = port
        self.client = None
        self.msgs = deque()
        self.log.info("MqttClient constructed")

    async def connect(self):
        """Connect the client to the MQTT server.
        """
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port)
        self.client.loop_start()
        self.client.subscribe(LSST_GENERAL_TOPIC)
        self.log.info("Connected")

    async def disconnect(self):
        """Disconnect the client from the MQTT server.
        """
        self.client.loop_stop()
        self.client.disconnect()
        self.log.info("Disconnected")

    def on_message(self, client, userdata, msg):
        """Callback for when an MQTT message arrives.

        Parameters
        ----------
        client: `mqtt.Client`
            The client instance for this callback.
        userdata:
            The private user data as set in Client() or userdata_set(). May be
            any data type according to the mqtt.Client API doc and is not set
            nor used in this class.
        msg: `mqtt.MQTTMessage`
            The MQTT message that holds the topic and payload.
        """
        self.msgs.append(msg)

    def publish_mqtt_message(self, topic, payload):
        """Publishes the specified payload to the specified topic on the MQTT
        server.

        Parameters
        ----------
        topic: `str`
            The topic to publish to.
        payload: `str`
            The payload to publish.

        Returns
        -------
        is_published: `bool`
            For now False gets returned since this functionality is disabled.
        """
        self.log.error(
            "This functionality is not enabled yet since it is unclear "
            "whether this CSC will be responsible for this or if this will be "
            "done via the HVAC software user interface."
        )
        return False
        # msg_info = self.client.publish(topic=topic, payload=payload)
        # return msg_info.is_published()
