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

__all__ = ["MqttInfoReader", "DATA_DIR"]

import csv
import pathlib
import re
import typing

from .enums import (
    DYNALENE_EVENT_TOPICS,
    EVENT_TOPIC_DICT_ENGLISH,
    EVENT_TOPICS,
    TOPICS_ALWAYS_ENABLED,
    CommandItemEnglish,
    EventItem,
    HvacTopicEnglish,
    SalTopicType,
    TelemetryItemEnglish,
    TopicType,
)
from .utils import determine_unit, parse_limits

# Various regex for CSV row parsing.
COMPAIR_REGEX = re.compile(r"LSST/PISO01/COMPAIR/0\d")
GENERAL_MANEJADORS_REGEX = re.compile(r"LSST/PISO04/MANEJADORA/GENERAL/[A-Z]+")
GENERAL_REGEX = re.compile(r"LSST/PISO0\d/[A-Z_0-9]+")
GLYCOL_SENSOR_REGEX = re.compile(r"LSST/PISO0\d/SENSOR_GLYCOL")
LOWER_MANEJADORS_REGEX = re.compile(r"LSST/PISO05/MANEJADORA/LOWER_\d\d")
VEX_MANEJADORS_REGEX = re.compile(r"LSST/PISO04/VEX_0\d/[A-Z_]+/GENERAL")

# Find the data directory relative to the location of this file.
DATA_DIR = pathlib.Path(__file__).resolve().parents[0] / "data"
INPUT_DIR = DATA_DIR / "input"
DAT_CONTROL_CSV_FILENAME = INPUT_DIR / "Direccionamiento_RubinObservatory.csv"


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

        self._collect_hvac_topics_and_items_from_csv()

    def extract_topic_and_item(
        self, hvac_topic_and_item: str
    ) -> typing.Tuple[str, str, str | None]:
        """Extract the generic topic, representing a HVAC device, and item,
         representing a published value of the device, from a string.

        Parameters
        ----------
        hvac_topic_and_item: `str`
            The string to extract the generic topic and item from.

        Returns
        -------
        device: `str`
            The HVAC device.
        item: `str`:
             The published value of the device.
        original_device : `str` | `None`
            The original device from the MQTT string before corrections for
            use in the HVAC CSC or None if the original device is the same as
            the corrected device.

        Raises
        ------
        ValueError
            In case no known device is found.
        """
        device, original_device = self._extract_device(hvac_topic_and_item)
        device_for_item = original_device if original_device is not None else device
        item = hvac_topic_and_item.replace(f"{device_for_item}/", "")

        # Work around inconsistent telmetry item names.
        if item == "ESTADO_DE_UNIDAD":
            item = "ESTADO_UNIDAD"
        if item == "MODO_OPERACION_UNIDAD":
            item = "MODO_OPERACION"

        return device, item, original_device

    def _collect_hvac_topics_and_items_from_csv(self) -> None:
        contents: list[dict[str, str]] = []
        with open(DAT_CONTROL_CSV_FILENAME) as f:
            f.readline()
            f.readline()
            d = csv.DictReader(f, delimiter=";")
            for row in d:
                contents.append(row)

        mqtt_topic_rows: list[dict[str, str]] = []
        piso = ""
        tablero = ""
        for row in contents:
            m = GENERAL_REGEX.match(row["TOPIC MQTT"])
            if m:
                # Skip undefined Dynalene commands and telemetry.
                if "tbd" in row["TOPIC MQTT"].lower():
                    continue
                if row["PISO"] and row["TABLERO"]:
                    piso = row["PISO"]
                    tablero = row["TABLERO"]
                if not row["PISO"]:
                    row["PISO"] = piso
                if not row["TABLERO"]:
                    row["TABLERO"] = tablero
                mqtt_topic_rows.append(row)

        self._validate_all_rows_contain_know_devices(mqtt_topic_rows)

        read_topic_rows = [
            row
            for row in mqtt_topic_rows
            if row["READ / WRITE"] == "READ "
            and not (
                row["TOPIC MQTT"] in EVENT_TOPICS
                or row["TOPIC MQTT"] in EVENT_TOPIC_DICT_ENGLISH
                or row["TOPIC MQTT"] in DYNALENE_EVENT_TOPICS
            )
        ]
        write_topic_rows = [
            row for row in mqtt_topic_rows if row["READ / WRITE"] == "WRITE"
        ]
        event_topic_rows = [
            row
            for row in mqtt_topic_rows
            if row["TOPIC MQTT"] in EVENT_TOPICS
            and row["TOPIC MQTT"] not in EVENT_TOPIC_DICT_ENGLISH
            and row["TOPIC MQTT"] not in DYNALENE_EVENT_TOPICS
        ]

        self._validate_all_event_topics(event_topic_rows)

        self._collect_devices_and_items(read_topic_rows, SalTopicType.TELEMETRY)
        self._collect_devices_and_items(write_topic_rows, SalTopicType.COMMAND)
        self._collect_devices_and_items(event_topic_rows, SalTopicType.EVENT)

    def _extract_device(self, mqtt_topic: str) -> typing.Tuple[str, str | None]:
        """Extract the device from the mqtt_topic.

        This also returns the original device, if different from the device,
        or None.

        Parameters
        ----------
        mqtt_topic : `str`
            The MQTT topic string to extract the device from.

        Returns
        -------
        typing.Tuple[str, str | None]
            A tuple of the extracted device and either the original device
            from the MQTT string or None if the device and opriginal device
            are the same.
        """
        m = LOWER_MANEJADORS_REGEX.match(mqtt_topic)
        if m:
            return m.group(), None
        m = GENERAL_MANEJADORS_REGEX.match(mqtt_topic)
        if m:
            return m.group(), None
        m = VEX_MANEJADORS_REGEX.match(mqtt_topic)
        if m:
            return m.group(), None
        m = GLYCOL_SENSOR_REGEX.match(mqtt_topic)
        if m:
            return "LSST/PISO01/SENSOR_GLYCOL", m.group()
        m = COMPAIR_REGEX.match(mqtt_topic)
        if m:
            device = m.group().replace("/0", "_0")
            return device, m.group()
        if mqtt_topic.startswith("LSST/PISO02/APERTURA"):
            return HvacTopicEnglish.chillerValve.value, "LSST/PISO02/APERTURA"

        # Handle the default case.
        m = GENERAL_REGEX.match(mqtt_topic)
        if m:
            return m.group(), None
        raise KeyError(f"No known device found in {mqtt_topic}.")

    def _validate_all_rows_contain_know_devices(
        self, mqtt_topic_rows: list[dict[str, str]]
    ) -> None:
        devices: set[str] = set()
        for row in mqtt_topic_rows:
            topic = row["TOPIC MQTT"]
            device, _ = self._extract_device(topic)
            devices.add(device)

        for device in devices:
            HvacTopicEnglish(device)
        for hvac_device in HvacTopicEnglish:
            assert hvac_device.value in devices, f"{hvac_device.value} is missing."

    def _validate_all_event_topics(
        self, event_topic_rows: list[dict[str, str]]
    ) -> None:
        all_event_topic_rows = [row["TOPIC MQTT"] for row in event_topic_rows]
        for event_topic in EVENT_TOPICS:
            assert (
                event_topic in all_event_topic_rows
            ), f"{event_topic} doesn't exist in event_topic_rows."
        for event_topic in all_event_topic_rows:
            assert (
                event_topic in EVENT_TOPICS
            ), f"{event_topic} doesn't exist in EVENT_TOPICS."

    def _collect_devices_and_items(
        self, topic_rows: list[dict[str, str]], sal_topic_type: SalTopicType
    ) -> None:
        for row in topic_rows:
            hvac_topic_and_item = row["TOPIC MQTT"]
            idl_type = "float" if "ANALOG" in row["SIGNAL"] else "boolean"
            topic_type = row["READ / WRITE"].strip()
            if topic_type in [TopicType.READ, TopicType.WRITE]:
                unit = determine_unit(row["UNIT"])
                limits = parse_limits(row["LIMITES"].strip())
            else:
                raise KeyError(f"Found unknown topic type {topic_type}.")

            device, item, _ = self.extract_topic_and_item(hvac_topic_and_item)
            hvac_topic = HvacTopicEnglish(device)
            hvac_item: TelemetryItemEnglish | CommandItemEnglish | EventItem = (
                TelemetryItemEnglish.alarmDevice
            )
            hvac_topics = self.telemetry_topics
            try:
                match sal_topic_type:
                    case SalTopicType.TELEMETRY:
                        hvac_item = TelemetryItemEnglish(item)
                        hvac_topics = self.telemetry_topics
                    case SalTopicType.COMMAND:
                        hvac_item = CommandItemEnglish(item)
                        hvac_topics = self.command_topics
                    case SalTopicType.EVENT:
                        hvac_item = EventItem(item)
                        hvac_topics = self.event_topics
                    case _:
                        raise KeyError(f"Unknown SalTopicType {sal_topic_type}.")
            except ValueError:
                print(f'{sal_topic_type}: {device} / {item} "{hvac_topic_and_item}",')
            if hvac_topic.name not in hvac_topics:
                hvac_topics[hvac_topic.name] = {}
            hvac_topics[hvac_topic.name][hvac_item.name] = {
                "idl_type": idl_type,
                "unit": unit,
            }
            self.hvac_topics[hvac_topic_and_item] = {
                "idl_type": idl_type,
                "unit": unit,
                "topic_type": topic_type,
                "limits": limits,
            }

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
                topic, _, _ = self.extract_topic_and_item(hvac_topic_and_item)

                hvac_topics.add(topic)
        for topic in TOPICS_ALWAYS_ENABLED:
            hvac_topics.add(topic)

        return hvac_topics

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
            tpc, item, _ = self.extract_topic_and_item(hvac_topic)
            if tpc == topic:
                items[item] = self.hvac_topics[hvac_topic]
        return items
