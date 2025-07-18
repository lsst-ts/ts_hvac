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

import asyncio
import logging
import threading
import typing

import paho.mqtt.client as mqtt

from .base_mqtt_client import BaseMqttClient

LSST_CLIENT_ID = "LSST"
LSST_GENERAL_TOPIC = "LSST/#"


class MqttClient(BaseMqttClient):
    """Client class to connect to the HVAC MQTT server.

    Parameters
    ----------
    host: `str`
        The hostname of the MQTT server.
    port: `int`
        The port of the MQTT service.
    """

    def __init__(self, host: str, port: int, log: logging.Logger) -> None:
        super().__init__(log)
        self.running_loop = asyncio.get_running_loop()
        self.threading_lock = threading.Lock()
        self.host = host
        self.port = port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.pub_ack_events: dict[int, asyncio.Event] = dict()
        self.log.debug("MqttClient constructed.")

    async def connect(self) -> None:
        """Connect the client to the MQTT server."""
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.connect(self.host, self.port)
        self.client.loop_start()
        self.client.subscribe(LSST_GENERAL_TOPIC)
        self.connected = True
        self.log.debug("Connected.")

    async def disconnect(self) -> None:
        """Disconnect the client from the MQTT server."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        self.log.debug("Disconnected.")

    def on_message(
        self, client: mqtt.Client, userdata: typing.Any, msg: mqtt.MQTTMessage
    ) -> None:
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

    def on_publish(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        mid: int,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties,
    ) -> None:
        """Callback for when an MQTT message is published.

        This function sets the event for the corresponding mid, if one exists.

        Parameters
        ----------
        client: `mqtt.Client`
            The client instance for this callback.
        userdata:
            The private user data as set in Client() or with user_data_set().
        mid: `int`
            The message ID that matches the mid returned from the
            corresponding publish() call. Useful for tracking which
            message was acknowledged.
        reason_code: `mqtt.ReasonCode`
            The reason code returned by the broker.
        properties: `mqtt.Properties`
            MQTT v5.0 properties returned by the broker.
        """
        with self.threading_lock:
            event = self.pub_ack_events.pop(mid, None)
        if reason_code.is_failure:
            self.running_loop.call_soon_threadsafe(
                lambda: self.log.warning(
                    f"MQTT publish failed: {reason_code} ({reason_code.value})"
                )
            )
        if event:
            self.running_loop.call_soon_threadsafe(event.set)

    async def publish_mqtt_message(
        self, topic: str, payload: str, qos: int = 1, timeout: float = 5.0
    ) -> bool:
        """Publishes the specified payload to the specified topic on the MQTT
        server.

        Parameters
        ----------
        topic: `str`
            The topic to publish to.
        payload: `str`
            The payload to publish.
        qos: `int`
            The MQTT QoS parameter to be used in sending the message:
             * 0 = at most once
             * 1 = at least once
             * 2 = exactly once
        timeout: `float`
            Time after which to return a failure, in seconds.

        Returns
        -------
        is_published: `bool`
            True if the message was published successfully.
        """
        self.log.debug(f"Sending message with {topic=!r} and {payload=!r}.")
        event = asyncio.Event()
        with self.threading_lock:
            msg_info = self.client.publish(topic=topic, payload=payload)
            mid = msg_info.mid
            self.pub_ack_events[mid] = event

        try:
            await asyncio.wait_for(event.wait(), timeout)
        except asyncio.TimeoutError:
            self.log.debug(
                f"Timeout while sending message with {topic=!r} and {payload=!r}."
            )
        finally:
            self.pub_ack_events.pop(mid, None)

        return msg_info.is_published()
