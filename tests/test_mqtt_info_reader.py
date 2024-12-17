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

import unittest

from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader


class MqttInfoReaderTestCase(unittest.TestCase):
    def test_extract_topic_and_item(self) -> None:
        mir = MqttInfoReader()
        topic_and_item = "LSST/PISO01/CHILLER_01/TEMPERATURA_AGUA_RETORNO_EVAPORADOR"
        topic, item = mir.extract_topic_and_item(topic_and_item)
        self.assertEqual("LSST/PISO01/CHILLER_01", topic)
        self.assertEqual("TEMPERATURA_AGUA_RETORNO_EVAPORADOR", item)

        topic_and_item = "STRING_WITHOUT_FORWARD_SLASH"
        try:
            topic, item = mir.extract_topic_and_item(topic_and_item)
            self.fail("A ValueError was expected here.")
        except ValueError as e:
            self.assertIsNot(e, None)
