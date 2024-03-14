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

from lsst.ts.hvac.enums import DEVICE_GROUPS, TOPICS_ALWAYS_ENABLED
from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader
from lsst.ts.hvac.xml import hvac_mqtt_to_SAL_XML
from lsst.ts.xml.enums.HVAC import DeviceId

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)


class MqttToSalTestCase(unittest.TestCase):
    def test_mask(self) -> None:
        mask = 0b10000000110001
        topics_enabled = [
            flag for (index, flag) in enumerate(DeviceId) if (mask & 2**index)
        ]
        print(topics_enabled)
        mask_check = 0
        device_id_index = {dev_id: i for i, dev_id in enumerate(DeviceId)}
        for topic_enabled in topics_enabled:
            mask_check += 1 << device_id_index[topic_enabled]
        self.assertEqual(mask_check, mask)

    def test_hvac_command_groups(self) -> None:
        xml = MqttInfoReader()
        command_topic_counts = {}
        for hvac_topic in xml.get_generic_hvac_topics():
            topic_found = False
            # Skip if the topic cannot be enabled or disabled.
            if hvac_topic in TOPICS_ALWAYS_ENABLED:
                topic_found = True
                continue
            command_group = next(
                (
                    group
                    for group, topic in DEVICE_GROUPS.items()
                    if hvac_topic in topic
                ),
                None,
            )
            if command_group:
                topic_found = True
                if command_group not in command_topic_counts:
                    command_topic_counts[command_group] = 0
                command_topic_counts[command_group] += 1
                continue

            # Fail is a topic is not found.
            if not topic_found:
                self.fail(f"Topic {hvac_topic} not found in COMMAND_TOPICS.")

        # Only pass if the number of commands per group in the JSON file and
        # in the DEVICE_GROUPS dict agree.
        for command_topic in command_topic_counts.keys():
            self.assertEqual(
                command_topic_counts[command_topic],
                len(DEVICE_GROUPS[command_topic]),
                f"{command_topic!r} has {command_topic_counts[command_topic]} command_topic_counts"
                f" and {len(DEVICE_GROUPS[command_topic])} DEVICE_GROUP counts.",
            )

    def test_collect_command_topics(self) -> None:
        xml = MqttInfoReader()
        unique_command_items_per_group = (
            hvac_mqtt_to_SAL_XML.collect_unique_command_items_per_group(
                xml.command_topics
            )
        )

        for command_group in unique_command_items_per_group.keys():
            item_list = unique_command_items_per_group[command_group]
            # Make sure there are no empty dicts
            self.assertTrue(item_list)
            # Make sure that "comandoEncendido" is not present in the dict
            self.assertTrue("comandoEncendido" not in item_list)
