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

__all__ = [
    "MqttInfoReader",
    "DATA_DIR",
]

import json
import pandas
import pathlib
import re

from .enums import (
    CommandItem,
    HvacTopic,
    TelemetryItem,
    TOPICS_ALWAYS_ENABLED,
    TopicType,
)


# The names of the columns in the CSV file in the correct order.
names = [
    "floor",
    "subsystem",
    "variable",
    "topic_and_item",
    "publication",
    "subscription",
    "signal",
    "rw",
    "range",
    "limits",
    "unit",
    "state",
    "observations",
    "notes",
]

# Find the data directory relative to the location of this file.
DATA_DIR = pathlib.Path(__file__).resolve().parents[3] / "data"

INPUT_DIR = DATA_DIR / "input"
dat_control_csv_filename = (
    INPUT_DIR / "Direccionamiento_Lsst_Final_JSON_rev2021_rev4.csv"
)
dat_control_json_filename = INPUT_DIR / "JSON_V7_PUBLICACIONES_SUSCRIPCIONES.json"


class MqttInfoReader:
    def __init__(self):
        # This dict contains the general MQTT topics (one for each sub-system)
        # as keys and a dictionary representing the items as value. The
        # structure is
        # "general_topic" : {
        #     "item": {
        #         "idl_type": idl_type,
        #         "unit": unit,
        #         "topic_type": topic_type,
        #         "limits": (lower_limit, upper_limit),
        #     }
        # }
        self.hvac_topics = {}
        # This dict contains the general ts_xml telemetry topics (retrieved by
        # using the `HvacTopic` enum) as keys and a dictionary representing the
        # ts_xml telemetry items (retrieved by using the `TelemetryItem` enum)
        # as values. The structure is
        # "HvacTopic" : {
        #     "TelemetryItem": {
        #         "idl_type": idl_type,
        #         "unit": unit,
        #     }
        # }
        self.telemetry_topics = {}
        # This dict contains the general ts_xml command topics (retrieved by
        # using the `HvacTopic` enum) as keys and a dictionary representing the
        # ts_xml command items (retrieved by using the `CommandItem` enum) as
        # values. The structure is
        # "HvacTopic" : {
        #     "CommandItem": {
        #         "idl_type": idl_type,
        #         "unit": unit,
        #     }
        # }
        self.command_topics = {}

        self._collect_hvac_topics_and_items_from_json()

    def _determine_unit(self, unit_string):
        """Convert the provided unit string to a string representing the unit.

        Parameters
        ----------
        unit_string: `str`
            The unit as read from the input file.

        Returns
        -------
        unit: `str`
            A string representing the unit.
        """
        return {
            "-": "unitless",
            "": "unitless",
            "°C": "deg_C",
            "bar": "bar",
            "%": "%",
            "hr": "h",
            "%RH": "%",
        }[unit_string]

    def _parse_limits(self, limits_string):
        """Parse the string value of the limits column by comparing it to known
        regular expressions and extracting the minimum and maximum values.

        Parameters
        ----------
        limits_string: `str`
            The string containing the limits to parse.

        Returns
        -------
        lower_limit: `float`
            The lower limit
        upper_limit: `float`
            The upper limit

        Raises
        ------
        ValueError
            In case an unknown string pattern is found in the limits column.

        """
        lower_limit = None
        upper_limit = None

        match = re.match(
            r"^(-?\d+)(/| a |% a |°C a | bar a |%RH a )(-?\d+)(%|°C| bar| hr|%RH)?$",
            limits_string,
        )
        if match:
            lower_limit = float(match.group(1))
            upper_limit = float(match.group(3))
        elif re.match(r"^\d$", limits_string):
            lower_limit = 0
            upper_limit = 100
        elif limits_string == "1,2,3,4,5,6,7,8":
            lower_limit = 1
            upper_limit = 8
        elif limits_string == "1,2,3,4,5,6":
            lower_limit = 1
            upper_limit = 6
        elif limits_string in ["true o false", "-", ""]:
            # ignore because there really are no lower and upper limits
            pass
        else:
            raise ValueError(f"Couldn't match limits_string {limits_string}")

        return lower_limit, upper_limit

    def extract_topic_and_item(self, topic_and_item):
        """Extract the generic topic, representing a HVAC subsystem, and item,
         representing a published value of the subsystem, from a string.

        This method searches for the last occurrence of that forward slash and
        will return the part before the slash as topic and after the slash as
        item.

        Parameters
        ----------
        topic_and_item: `str`
            The string to extract the generic topic and item from.

        Returns
        -------
        topic: `str`
            Defined as the part before the last forward slash.
        item: `str`:
             Defined as the part after the last forward slash.

        Raises
        ------
        ValueError
            In case no forward slash is found.
        """
        # This throws a ValueError in case no forward slash is found.
        topic, item = topic_and_item.rsplit("/", 1)
        return topic, item

    def _generic_collect_topics_and_items(
        self, topic_and_item, topic_type, idl_type, unit, limits, topics, items
    ):
        """Collect XML topics and items from a row read from the CSV or JSON
        file with the Rubin Observatory HVAC system information sent by
        DatControl.

        Parameters
        ----------
        topic_and_item: `str`
            The topic and item to parse, for instance

                "LSST/PISO02/CRACK01/ESTADO_FUNCIONAMIENTO"

            would be the topic "LSST/PISO02/CRACK01" and the item
            "ESTADO_FUNCIONAMIENTO"
        topic_type: `str`
            Indicates whether the topic is a telemetry topic (READ) or a
            command topic (WRITE).
        idl_type: `str`
            The IDL type.
        unit: `str`
            A string representing an astropy unit.
        limits: tuple
            A tuple containing the lower and upper limits.
        topics: `dict`
            The dictionary to which to add the XML topic and item.
        items: enum.Enum
            The Enum that is used to translate the HVAC topics and items to XML
            topics and items.


        Raises
        -------
        ValueError
            In case a HVAC topic or item is not present in the Telemetry, Item
            or Command Enums. This error will only be raised during development
            of the code and serves to ensure that all HVAC topics and items are
            present in the Enums.

        Notes
        -----
        The hvac_topics dictionary gets filled as well by this method.

        """
        topic_found = False
        topic, item = self.extract_topic_and_item(topic_and_item)

        for hvac_topic in HvacTopic:
            if hvac_topic.value in topic:
                if hvac_topic.name not in topics:
                    topics[hvac_topic.name] = {}

                for hvac_item in items:
                    if hvac_item.value == item:
                        topics[hvac_topic.name][hvac_item.name] = {
                            "idl_type": idl_type,
                            "unit": unit,
                        }
                        self.hvac_topics[topic_and_item] = {
                            "idl_type": idl_type,
                            "unit": unit,
                            "topic_type": topic_type,
                            "limits": limits,
                        }
                        break
                else:
                    raise ValueError(
                        f"TelemetryItem '{item}' for {topic} not found in {topic_and_item}"
                    )

                topic_found = True
                break
        if not topic_found:
            raise ValueError(
                f"Topic {topic} in topic_and_item {topic_and_item} not found."
            )

    def _collect_topics_and_items(self, topics):
        for topic_and_item in sorted(topics.keys()):
            idl_type = topics[topic_and_item]["idl_type"]
            topic_type = topics[topic_and_item]["topic_type"]
            unit = topics[topic_and_item]["unit"]
            limits = topics[topic_and_item]["limits"]
            if topic_type == TopicType.READ:
                self._generic_collect_topics_and_items(
                    topic_and_item,
                    topic_type,
                    idl_type,
                    unit,
                    limits,
                    self.telemetry_topics,
                    TelemetryItem,
                )
            if topic_type == TopicType.WRITE:
                self._generic_collect_topics_and_items(
                    topic_and_item,
                    topic_type,
                    idl_type,
                    unit,
                    limits,
                    self.command_topics,
                    CommandItem,
                )

    def collect_hvac_topics_and_items_from_csv(self):
        """Loop over all rows in the CSV file and extracts either telemetry
        topic data or command topic data depending on the contents of the "rw"
        column in the CSV row.

        TODO: DM-29135: This method and all references to CSV will be removed
         once the contents of the CSV and JSON files have been verified against
         the HVAC server.
        """
        csv_hvac_topics = {}
        print(f"Loading CSV file {dat_control_csv_filename}")
        with open(dat_control_csv_filename) as csv_file:
            csv_reader = pandas.read_csv(
                csv_file,
                delimiter=";",
                index_col=False,
                dtype=str,
                names=names,
                keep_default_na=False,
            )
            for index, row in csv_reader.iterrows():
                csv_hvac_topic_and_item = row["topic_and_item"]
                idl_type = "float" if "ANALOG" in row["signal"] else "boolean"
                topic_type = row["rw"].strip()
                if topic_type in [TopicType.READ, TopicType.WRITE]:
                    unit = self._determine_unit(row["unit"])
                    limits = self._parse_limits(row["limits"].strip())
                    csv_hvac_topics[csv_hvac_topic_and_item] = {
                        "idl_type": idl_type,
                        "topic_type": topic_type,
                        "unit": unit,
                        "limits": limits,
                    }
        self._collect_topics_and_items(csv_hvac_topics)

    def _collect_hvac_topics_and_items_from_json(self):
        """Loop over all rows in the JSON file and extracts either telemetry
        topic data or command topic data depending on whether the JSON topic
        name ends in "_WRITE" or not.
        """
        json_hvac_topics = {}
        print(f"Loading JSON file {dat_control_json_filename}")
        with open(dat_control_json_filename) as f:
            all_json_hvac_topics = json.loads(f.read())
            for json_hvac_topic in all_json_hvac_topics["BOUNDQUERYRESULT"]:
                json_hvac_topic_and_item = json_hvac_topic["POINT"]
                # Command topics always end in "_LSST" and telemetry topics
                # never do so that's how the distinction is made in this code.
                topic_type = (
                    TopicType.WRITE
                    if json_hvac_topic_and_item.endswith("_LSST")
                    else TopicType.READ
                )
                idl_type = (
                    "float" if "Numeric" in json_hvac_topic["TYPE"] else "boolean"
                )
                unit = self._determine_unit(json_hvac_topic["UNIT"])
                limits = self._parse_limits(json_hvac_topic["LIMIT"])
                json_hvac_topics[json_hvac_topic_and_item] = {
                    "idl_type": idl_type,
                    "topic_type": topic_type,
                    "unit": unit,
                    "limits": limits,
                }
        self._collect_topics_and_items(json_hvac_topics)

    def get_generic_hvac_topics(self):
        """Convenience method to collect all generic topics, representing the
        HVAC subsystems.

        Returns
        -------
        hvac_topics: `set`
            A set of all generic HVAC topics.

        """
        hvac_topics = set()
        for hvac_topic_and_item in self.hvac_topics:
            topic_type = self.hvac_topics[hvac_topic_and_item]["topic_type"]
            if topic_type == TopicType.WRITE and hvac_topic_and_item.endswith(
                "COMANDO_ENCENDIDO_LSST"
            ):
                topic, item = self.extract_topic_and_item(hvac_topic_and_item)
                hvac_topics.add(topic)
        for topic in TOPICS_ALWAYS_ENABLED:
            hvac_topics.add(topic)

        return hvac_topics

    def get_items_for_hvac_topic(self, topic):
        """Convenience method to get all items for a generic HVAC topic.

        Parameters
        ----------
        topic: `str`
            The generic HVAC topic to get the items for.

        Returns
        -------
        items: `dict`
            A dict containing all items for the generic HVAC topic.

        Notes
        -----
        The structure of the dictionary is exactly the same as for the items in
        `hvac_topics`.

        """
        items = {}
        for hvac_topic in self.hvac_topics:
            tpc, item = self.extract_topic_and_item(hvac_topic)
            if tpc == topic:
                items[item] = self.hvac_topics[hvac_topic]
        return items

    def _get_mqtt_topics_and_items_for_type(self, topic_type):
        mqtt_topics = {}
        for hvac_topic in self.get_generic_hvac_topics():
            items = self.get_items_for_hvac_topic(hvac_topic)
            topic_items = {}
            for item in items:
                # Make sure only topics with the specified type are used.
                if items[item]["topic_type"] == topic_type:
                    topic_items[item] = items[item]
            mqtt_topics[hvac_topic] = topic_items
        return mqtt_topics

    def get_telemetry_mqtt_topics_and_items(self):
        """Convenience method to collect all MQTT topics and their items that
        publish telemetry.

        Returns
        -------
        telemetry_mqtt_topics: `dict`
            A dictionary with the MQTT topics as keys and their items as value.

        Notes
        -----
        The structure of the returned dictionary is exactly the same as for the
        hvac_topics dictionary. The only difference is that the command topics
        (indicated by topic type WRITE) have been filtered out.
        """
        return self._get_mqtt_topics_and_items_for_type(TopicType.READ)

    def get_command_mqtt_topics_and_items(self):
        """Convenience method to collect all MQTT topics and their items that
        accept commands.

        Returns
        -------
        command_mqtt_topics: `dict`
            A dictionary with the MQTT topics as keys and their items as value.

        Notes
        -----
        The structure of the returned dictionary is exactly the same as for the
        hvac_topics dictionary. The only difference is that the telemetry
        topics (indicated by topic type READ) have been filtered out.
        """
        return self._get_mqtt_topics_and_items_for_type(TopicType.WRITE)
