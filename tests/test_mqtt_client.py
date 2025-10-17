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

import asyncio
import logging
import unittest
from unittest import mock

import paho.mqtt.client as mqtt
from lsst.ts.hvac import MqttClient


class MqttClientTestCase(unittest.IsolatedAsyncioTestCase):
    @mock.patch("paho.mqtt.client.Client")
    async def test_mqtt_client(self, mock_client: mock.MagicMock) -> None:
        log = logging.Logger(type(self).__name__)
        mqtt_client = MqttClient(host="127.0.0.1", port=5000, log=log)
        mqtt_client.client = mock.MagicMock()

        await mqtt_client.connect()
        assert mqtt_client.connected

        assert len(mqtt_client.msgs) == 0
        msg = mqtt.MQTTMessage(topic="test")
        mqtt_client.on_message(mqtt_client, "", msg)
        assert len(mqtt_client.msgs) == 1

        assert await mqtt_client.publish_mqtt_message(topic="", payload="")

        await mqtt_client.disconnect()
        assert not mqtt_client.connected

    @mock.patch("paho.mqtt.client.Client")
    async def test_mqtt_client_success(self, mock_client: mock.MagicMock) -> None:
        log = mock.MagicMock()
        mqtt_client = MqttClient(host="127.0.0.1", port=5000, log=log)
        mqtt_client.client = mock.MagicMock()

        msg_info = mock.MagicMock()
        msg_info.mid = 54321
        msg_info.is_published.return_value = True
        mqtt_client.client.publish = mock.MagicMock()
        mqtt_client.client.publish.return_value = msg_info

        publish_task = asyncio.create_task(
            mqtt_client.publish_mqtt_message("some/topic", "payload", timeout=10.0)
        )

        await asyncio.sleep(0.05)
        assert len(mqtt_client.pub_ack_events) == 1
        mqtt_client.on_publish(
            client=mqtt_client.client,
            userdata=None,
            mid=msg_info.mid,
            reason_code=mqtt.ReasonCode(mqtt.PacketTypes.PUBACK),
            properties=mqtt.Properties(mqtt.PacketTypes.PUBACK),
        )

        result = await publish_task
        assert result is True
        assert len(mqtt_client.pub_ack_events) == 0
        assert (
            mock.call("Timeout while sending message with topic='some/topic' and payload='payload'.")
            not in mqtt_client.log.debug.call_args_list
        )

    @mock.patch("paho.mqtt.client.Client")
    async def test_mqtt_client_timeout(self, mock_client: mock.MagicMock) -> None:
        log = mock.MagicMock()
        mqtt_client = MqttClient(host="127.0.0.1", port=5000, log=log)
        mqtt_client.client = mock.MagicMock()

        msg_info = mock.MagicMock()
        msg_info.mid = 12345
        msg_info.is_published.return_value = False
        mqtt_client.client.publish = mock.MagicMock()
        mqtt_client.client.publish.return_value = msg_info

        result = await mqtt_client.publish_mqtt_message("some/topic", "payload", timeout=0.1)
        assert not result
        assert len(mqtt_client.pub_ack_events) == 0
        mqtt_client.log.debug.assert_any_call(
            "Timeout while sending message with topic='some/topic' and payload='payload'."
        )
