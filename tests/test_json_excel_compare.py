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

import asynctest
import logging
from lsst.ts.hvac.xml import hvac_mqtt_to_SAL_XML as xml

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)


class JsonExcelCompareTestCase(asynctest.TestCase):
    async def setUp(self):
        """Setup the unit test.
        """
        self.log = logging.getLogger("JsonExcelCompareTestCase")
        self.csv_topics = {}
        self.json_topics = {}

    def load_csv(self):
        xml.use_csv = True
        xml.collect_topics_and_items()
        self.csv_topics = xml.hvac_topics.copy()

    def load_json(self):
        xml.use_csv = False
        xml.collect_topics_and_items()
        self.json_topics = xml.hvac_topics.copy()

    async def test_compare_csv_and_json(self):
        self.load_csv()
        self.load_json()
        topic_types_differing = []
        idl_types_differing = []
        units_differing = []
        limits_differing = []

        json_topic_names = self.json_topics.keys()
        csv_topic_names = self.csv_topics.keys()
        json_topics_missing_in_csv = json_topic_names - csv_topic_names
        csv_topics_missing_in_json = csv_topic_names - json_topic_names

        for json_topic in self.json_topics.keys():
            if json_topic in self.csv_topics:
                if (
                    self.json_topics[json_topic]["topic_type"]
                    != self.csv_topics[json_topic]["topic_type"]
                ):
                    topic_types_differing.append(
                        (
                            json_topic,
                            self.json_topics[json_topic]["topic_type"],
                            self.csv_topics[json_topic]["topic_type"],
                        )
                    )
                if (
                    self.json_topics[json_topic]["idl_type"]
                    != self.csv_topics[json_topic]["idl_type"]
                ):
                    idl_types_differing.append(
                        (
                            json_topic,
                            self.json_topics[json_topic]["idl_type"],
                            self.csv_topics[json_topic]["idl_type"],
                        )
                    )
                if (
                    self.json_topics[json_topic]["unit"]
                    != self.csv_topics[json_topic]["unit"]
                ):
                    units_differing.append(
                        (
                            json_topic,
                            self.json_topics[json_topic]["unit"],
                            self.csv_topics[json_topic]["unit"],
                        )
                    )
                if (
                    self.json_topics[json_topic]["limits"]
                    != self.csv_topics[json_topic]["limits"]
                ):
                    limits_differing.append(
                        (
                            json_topic,
                            self.json_topics[json_topic]["limits"],
                            self.csv_topics[json_topic]["limits"],
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
