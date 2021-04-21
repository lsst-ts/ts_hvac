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

from lsst.ts.hvac.hvac_enums import (
    HvacTopic,
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITHOUT_CONFIGURATION,
)
from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader
from lsst.ts.hvac.xml import hvac_mqtt_to_SAL_XML
from lsst.ts.idl.enums.HVAC import DeviceId, DEVICE_GROUPS, DEVICE_GROUP_IDS

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)


class MqttToSalTestCase(unittest.TestCase):
    def test_mask(self):
        xml = MqttInfoReader()
        xml.collect_hvac_topics_and_items_from_json()

        mask = 0b10000000110001
        topics_enabled = [
            flag for (index, flag) in enumerate(DeviceId) if (mask & 2 ** index)
        ]
        print(topics_enabled)
        mask_check = 0
        device_id_list = list(DeviceId)
        for topic_enabled in topics_enabled:
            mask_check += 2 ** device_id_list.index(topic_enabled)
        self.assertEqual(mask_check, mask)

    def test_hvac_command_groups(self):
        xml = MqttInfoReader()
        xml.collect_hvac_topics_and_items_from_json()
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

    def test_collect_command_topics(self):
        xml = MqttInfoReader()
        xml.collect_hvac_topics_and_items_from_json()
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

    def test_find_device_group(self):
        device_id_num = 101
        device_id = DeviceId(device_id_num)
        topic = HvacTopic[device_id.name]
        print(topic.value)
        command_group = [k for k, v in DEVICE_GROUPS.items() if topic.value in v][0]
        command_group_id = [
            DEVICE_GROUP_IDS[k] for k, v in DEVICE_GROUPS.items() if topic.value in v
        ][0]
        print(command_group)
        print(command_group_id)
        command_groups = set(
            k
            for k, v in DEVICE_GROUPS.items()
            for i in v
            if i not in TOPICS_WITHOUT_CONFIGURATION
        )
        print(command_groups)

    def test_enum(self):
        hvac_topic = HvacTopic.chiller03P01
        device_id = DeviceId[hvac_topic.name]
        deviceId_index = list(DeviceId).index(device_id)
        print(f"{hvac_topic.name} : {hvac_topic.value}, {deviceId_index}")
