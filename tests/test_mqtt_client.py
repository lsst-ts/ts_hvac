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

        assert mqtt_client.publish_mqtt_message(topic="", payload="")

        await mqtt_client.disconnect()
        assert not mqtt_client.connected
