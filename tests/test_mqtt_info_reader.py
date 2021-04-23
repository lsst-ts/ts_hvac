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
from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)


class MqttInfoReaderTestCase(unittest.TestCase):
    def test_compare_json_and_csv_hvac_topics_and_items(self):
        mir = MqttInfoReader()
        mir.collect_hvac_topics_and_items_from_json()
        json_hvac_topics = mir.hvac_topics.copy()

        mir.hvac_topics = {}

        mir.collect_hvac_topics_and_items_from_csv()
        csv_hvac_topics = mir.hvac_topics.copy()

        json_topics_missing_in_csv = json_hvac_topics.keys() - csv_hvac_topics.keys()
        csv_topics_missing_in_json = csv_hvac_topics.keys() - json_hvac_topics.keys()
        topic_types_differing = []
        idl_types_differing = []
        units_differing = []
        limits_differing = []
        for json_hvac_topic in json_hvac_topics.keys():
            if json_hvac_topic in csv_hvac_topics:
                if (
                    json_hvac_topics[json_hvac_topic]["topic_type"]
                    != csv_hvac_topics[json_hvac_topic]["topic_type"]
                ):
                    topic_types_differing.append(
                        (
                            json_hvac_topic,
                            json_hvac_topics[json_hvac_topic]["topic_type"],
                            csv_hvac_topics[json_hvac_topic]["topic_type"],
                        )
                    )
                if (
                    json_hvac_topics[json_hvac_topic]["idl_type"]
                    != csv_hvac_topics[json_hvac_topic]["idl_type"]
                ):
                    idl_types_differing.append(
                        (
                            json_hvac_topic,
                            self.json_topics[json_hvac_topic]["idl_type"],
                            self.csv_topics[json_hvac_topic]["idl_type"],
                        )
                    )
                if (
                    json_hvac_topics[json_hvac_topic]["unit"]
                    != csv_hvac_topics[json_hvac_topic]["unit"]
                ):
                    units_differing.append(
                        (
                            json_hvac_topic,
                            json_hvac_topics[json_hvac_topic]["unit"],
                            csv_hvac_topics[json_hvac_topic]["unit"],
                        )
                    )
                if (
                    json_hvac_topics[json_hvac_topic]["limits"]
                    != csv_hvac_topics[json_hvac_topic]["limits"]
                ):
                    limits_differing.append(
                        (
                            json_hvac_topic,
                            json_hvac_topics[json_hvac_topic]["limits"],
                            csv_hvac_topics[json_hvac_topic]["limits"],
                        )
                    )

        err_msgs = []
        if json_topics_missing_in_csv:
            err_msgs.append(f"JSON topics missing in CSV: {json_topics_missing_in_csv}")
        if csv_topics_missing_in_json:
            err_msgs.append(f"CSV topics missing in JSON: {csv_topics_missing_in_json}")
        if topic_types_differing:
            err_msgs.append(
                f"Topic Types differing between JSON and CSV: {topic_types_differing}"
            )
        if idl_types_differing:
            err_msgs.append(
                f"IDL Types differing between JSON and CSV: {idl_types_differing}"
            )
        if units_differing:
            err_msgs.append(f"Units differing between JSON and CSV: {units_differing}")
        if limits_differing:
            err_msgs.append(
                f"Limits differing between JSON and CSV: {limits_differing}"
            )
        if err_msgs:
            self.fail("Differences found:\n" + "\n".join(err_msgs))

    def test_extract_topic_and_item(self):
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
            self.assertTrue(e is not None)
