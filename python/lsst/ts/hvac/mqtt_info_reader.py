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

import enum
import pathlib
import re
import typing

import pandas
from lsst.ts.xml.component_info import ComponentInfo

from .enums import (
    DYNALENE_EVENT_GROUP_DICT,
    EVENT_TOPICS,
    TOPICS_ALWAYS_ENABLED,
    CommandItem,
    CommandItemEnglish,
    EventItem,
    HvacTopic,
    HvacTopicEnglish,
    Language,
    TelemetryItem,
    TelemetryItemEnglish,
    TopicType,
)
from .utils import bar_to_pa, psi_to_pa

# The default lower limit
DEFAULT_LOWER_LIMIT = -9999

# The default upper limit
DEFAULT_UPPER_LIMIT = 9999

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
DATA_DIR = pathlib.Path(__file__).resolve().parents[0] / "data"

INPUT_DIR = DATA_DIR / "input"
dat_control_csv_filename = INPUT_DIR / "Direccionamiento_RubinObservatory.csv"


class MqttInfoReader:
    def __init__(self) -> None:
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
        self.hvac_topics: dict[str, typing.Any] = {}
        # This dict contains the general ts_xml telemetry topics (retrieved by
        # using the `HvacTopicEnglish` enum) as keys and a dictionary
        # representing the ts_xml telemetry items (retrieved by using the
        # `TelemetryItem` enum) as values. The structure is
        # "HvacTopicEnglish" : {
        #     "TelemetryItem": {
        #         "idl_type": idl_type,
        #         "unit": unit,
        #     }
        # }
        self.telemetry_topics: dict[str, typing.Any] = {}
        # This dict contains the general ts_xml command topics (retrieved by
        # using the `HvacTopicEnglish` enum) as keys and a dictionary
        # representing the ts_xml command items (retrieved by using the
        # `CommandItemEnglish` enum) as values. The structure is
        # "HvacTopicEnglish" : {
        #     "CommandItemEnglish": {
        #         "idl_type": idl_type,
        #         "unit": unit,
        #     }
        # }
        self.command_topics: dict[str, typing.Any] = {}
        # This dict contains the general ts_xml event topics (retrieved by
        # using the `HvacTopicEnglish` enum) as keys and a dictionary
        # representing the ts_xml command items (retrieved by using the
        # `eventItem` enum) as values. The structure is
        # "HvacTopicEnglish" : {
        #     "EventItem": {
        #         "idl_type": idl_type,
        #         "unit": unit,
        #     }
        # }
        self.event_topics: dict[str, typing.Any] = {}

        # TODO DM-46835 Remove backward compatibility with XML 22.1.
        component_info = ComponentInfo(name="HVAC", topic_subname="")
        if "tel_coldWaterPump01" in component_info.topics:
            self.xml_language = Language.ENGLISH
        else:
            self.xml_language = Language.SPANISH

        self._collect_hvac_topics_and_items_from_csv()

    def _determine_unit(self, unit_string: str) -> str:
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
            "bar": "Pa",
            "%": "%",
            "hr": "h",
            "%RH": "%",
            "m3/h": "m3/h",
            "LPM": "l/min",
            "l/m": "l/min",
            "PSI": "Pa",
            "KW": "kW",
        }[unit_string.strip()]

    def _parse_limits(
        self, limits_string: str
    ) -> typing.Tuple[int | float, int | float]:
        """Parse the string value of the limits column by comparing it to known
        regular expressions and extracting the minimum and maximum values.

        Parameters
        ----------
        limits_string: `str`
            The string containing the limits to parse.

        Returns
        -------
        lower_limit: `int` or `float`
            The lower limit
        upper_limit: `int` or `float`
            The upper limit

        Raises
        ------
        ValueError
            In case an unknown string pattern is found in the limits column.

        """
        lower_limit: int | float = DEFAULT_LOWER_LIMIT
        upper_limit: int | float = DEFAULT_UPPER_LIMIT

        match = re.match(
            r"^(-?\d+)(/| a | ?% a |°C a | bar a |%RH a | LPM a | PSI a | KW a )(-?\d+)"
            r"( ?%| ?°C| bar| hr|%RH| LPM| PSI| KW)?$",
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
        elif limits_string in ["true o false", "-", "-1", ""]:
            # ignore because there really are no lower and upper limits
            pass
        else:
            raise ValueError(f"Couldn't match limits_string {limits_string}")

        # Convert non-standard units to standard ones.
        if "bar" in limits_string:
            lower_limit = round(bar_to_pa(lower_limit), 1)
            upper_limit = round(bar_to_pa(upper_limit), 1)
        if "PSI" in limits_string:
            lower_limit = round(psi_to_pa(lower_limit), 1)
            upper_limit = round(psi_to_pa(upper_limit), 1)

        return lower_limit, upper_limit

    def extract_topic_and_item(self, topic_and_item: str) -> typing.Tuple[str, str]:
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
        # Treat the Dynelane Safety and Status topics in a special way.
        if (
            topic == "LSST/PISO05/DYNALENE/Safeties"
            or topic == "LSST/PISO05/DYNALENE/Status"
            or topic == "LSST/PISO05/DYNALENE/DynaleneState"
        ):
            topic = "LSST/PISO05/DYNALENE"
        # Some Dynalene event items need to be grouped together.
        if item in DYNALENE_EVENT_GROUP_DICT:
            item = DYNALENE_EVENT_GROUP_DICT[item]
        return topic, item

    def _generic_collect_topics_and_items(
        self,
        topic_and_item: str,
        topic_type: str,
        idl_type: str,
        unit: str,
        limits: typing.Tuple[int | float, int | float],
        topics: dict[str, typing.Any],
        items: enum.EnumType,
    ) -> None:
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
        topic, item = self.extract_topic_and_item(topic_and_item)

        # TODO DM-46835 Remove backward compatibility with XML 22.1.
        # Work around inconsistent telmetry item names.
        if self.xml_language == Language.ENGLISH:
            if item == "ESTADO_DE_UNIDAD":
                item = "ESTADO_UNIDAD"
            if item == "MODO_OPERACION_UNIDAD":
                item = "MODO_OPERACION"

            topic_enum: enum.EnumType = HvacTopicEnglish
        else:
            topic_enum = HvacTopic
        # End TODO

        for hvac_topic in topic_enum:  # type: ignore
            if hvac_topic.value in topic:
                if hvac_topic.name not in topics:
                    topics[hvac_topic.name] = {}

                # Cannot use type hints in for loops.
                for hvac_item in items:  # type: ignore
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
                    print(
                        f"TelemetryItem '{item}' for {topic} not found in {topic_and_item}"
                    )

    def _collect_topics_and_items(self, topics: dict[str, typing.Any]) -> None:
        # TODO DM-46835 Remove backward compatibility with XML 22.1.
        if self.xml_language == Language.ENGLISH:
            command_enum: enum.EnumType = CommandItemEnglish
            telemetry_enum: enum.EnumType = TelemetryItemEnglish
        else:
            command_enum = CommandItem
            telemetry_enum = TelemetryItem
        # End TODO

        for topic_and_item in sorted(topics.keys()):
            if topic_and_item in EVENT_TOPICS:
                continue
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
                    telemetry_enum,
                )
            if topic_type == TopicType.WRITE:
                self._generic_collect_topics_and_items(
                    topic_and_item,
                    topic_type,
                    idl_type,
                    unit,
                    limits,
                    self.command_topics,
                    command_enum,
                )
        for topic_and_item in EVENT_TOPICS:
            idl_type = topics[topic_and_item]["idl_type"]
            topic_type = topics[topic_and_item]["topic_type"]
            unit = topics[topic_and_item]["unit"]
            limits = topics[topic_and_item]["limits"]
            self._generic_collect_topics_and_items(
                topic_and_item,
                topic_type,
                idl_type,
                unit,
                limits,
                self.event_topics,
                EventItem,
            )

    def _collect_hvac_topics_and_items_from_csv(self) -> None:
        """Loop over all rows in the CSV file and extracts either telemetry
        topic data or command topic data depending on the contents of the "rw"
        column in the CSV row.
        """
        csv_hvac_topics = {}
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

    def get_generic_hvac_topics(self) -> set[str]:
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
                topic, _ = self.extract_topic_and_item(hvac_topic_and_item)
                hvac_topics.add(topic)
        for topic in TOPICS_ALWAYS_ENABLED:
            hvac_topics.add(topic)

        return hvac_topics

    def get_items_for_hvac_topic(self, topic: str) -> dict[str, typing.Any]:
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
        items: dict[str, typing.Any] = {}
        for hvac_topic in self.hvac_topics:
            tpc, item = self.extract_topic_and_item(hvac_topic)
            if tpc == topic:
                items[item] = self.hvac_topics[hvac_topic]
        return items

    def _get_mqtt_topics_and_items_for_type(
        self, topic_type: str
    ) -> dict[str, typing.Any]:
        mqtt_topics: dict[str, typing.Any] = {}
        for hvac_topic in self.get_generic_hvac_topics():
            items = self.get_items_for_hvac_topic(hvac_topic)
            topic_items = {}
            for item in items:
                # Make sure only topics with the specified type are used.
                if items[item]["topic_type"] == topic_type:
                    topic_items[item] = items[item]
            mqtt_topics[hvac_topic] = topic_items
        return mqtt_topics

    def get_telemetry_mqtt_topics_and_items(self) -> dict[str, typing.Any]:
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

    def get_command_mqtt_topics_and_items(self) -> dict[str, typing.Any]:
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
