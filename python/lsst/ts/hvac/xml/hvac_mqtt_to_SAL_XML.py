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

import enum
import re
import typing

from lsst.ts.hvac.enums import (
    DEVICE_GROUPS,
    EVENT_TOPIC_DICT,
    SPANISH_TO_ENGLISH_DICTIONARY,
    DynaleneDescription,
    HvacTopic,
)
from lsst.ts.hvac.mqtt_info_reader import DATA_DIR, MqttInfoReader
from lsst.ts.hvac.utils import to_camel_case
from lsst.ts.xml.enums.HVAC import DeviceId, DynaleneState, DynaleneTankLevel
from lxml import etree

OUTPUT_DIR = DATA_DIR / "output"
telemetry_filename = OUTPUT_DIR / "HVAC_Telemetry.xml"
command_filename = OUTPUT_DIR / "HVAC_Commands.xml"
events_filename = OUTPUT_DIR / "HVAC_Events.xml"

XML_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSL = "type='text/xsl' "
NSMAP = {"xsi": XML_NAMESPACE}
attr_qname = etree.QName(
    "http://www.w3.org/2001/XMLSchema-instance", "noNamespaceSchemaLocation"
)
telemetry_root = etree.Element(
    "SALTelemetrySet",
    {attr_qname: "http://lsst-sal.tuc.noao.edu/schema/SALTelemetrySet.xsd"},
    nsmap=NSMAP,
)
telemetry_root.addprevious(
    etree.ProcessingInstruction(
        "xml-stylesheet",
        XSL + "href='http://lsst-sal.tuc.noao.edu/schema/SALTelemetrySet.xsl'",
    )
)
command_root = etree.Element(
    "SALCommandSet",
    {attr_qname: "http://lsst-sal.tuc.noao.edu/schema/SALCommandSet.xsd"},
    nsmap=NSMAP,
)
command_root.addprevious(
    etree.ProcessingInstruction(
        "xml-stylesheet",
        XSL + "href='http://lsst-sal.tuc.noao.edu/schema/SALCommandSet.xsl'",
    )
)
events_root = etree.Element(
    "SALEventSet",
    {attr_qname: "http://lsst-sal.tuc.noao.edu/schema/SALEventSet.xsd"},
    nsmap=NSMAP,
)
events_root.addprevious(
    etree.ProcessingInstruction(
        "xml-stylesheet",
        XSL + "href='http://lsst-sal.tuc.noao.edu/schema/SALEventSet.xsl'",
    )
)

xml = MqttInfoReader()


def _translate_item(item: str) -> str:
    """Perform a crude translation of the Spanish words in the given item to
    English.

    Parameters
    ----------
    item: `str`
        A string containing Spanish words to be translated into English.

    Returns
    -------
    translated_item: `str`
        A string containing a crude English translation of the Spanish words.

    """
    if item.startswith("dyn"):
        translated_item = DynaleneDescription[item].value
    else:
        # Perform a crude translation of Spanish into English. This code can be
        # improved.
        translated_item = re.sub(r"([A-Z])", lambda m: " " + m.group(1), item).upper()
        for key in SPANISH_TO_ENGLISH_DICTIONARY.keys():
            translated_item = re.sub(
                rf"{key}", rf"{SPANISH_TO_ENGLISH_DICTIONARY[key]}", translated_item
            )
    return translated_item


def _split_event_description(item: str) -> str:
    """Split a camelCase event description string into its components.

    Parameters
    ----------
    item: `str`
        A camelCase string containing an event description.

    Returns
    -------
    split_item: `str`
        A string containing the event description split into its items.

    """
    splitted_items = re.findall(
        "[A-Z][a-z]+|[0-9A-Z]+(?=[A-Z][a-z])|[0-9A-Z]{2,}|[a-z0-9]{2,}|[a-zA-Z0-9]",
        item,
    )
    splitted_item = " ".join(splitted_items)
    splitted_item = splitted_item[0].upper() + splitted_item[1:]
    return splitted_item


def _create_item_element(
    parent: str,
    topic: str,
    item: str,
    idl_type: str,
    unit: str,
    description_text: str,
    element_count: int,
) -> None:
    """Create an XML element representing an item.

    XML items for telemetry and commands have the same structure so it is easy
    to have a generic method.

    Parameters
    ----------
    parent: etree.SubElement
        The parent element.
    topic: `str`
        The topic
    item: `str`
        The item
    idl_type: `str`
        The IDL type
    unit: `str`
        The unit
    description_text: `str`
        The description of the item
    element_count: `int`
        The number of elements expected.
    """
    it = etree.SubElement(parent, "item")
    efdb_name = etree.SubElement(it, "EFDB_Name")
    efdb_name.text = item
    description = etree.SubElement(it, "Description")
    description.text = description_text
    idl_type_elt = etree.SubElement(it, "IDL_Type")
    idl_type_elt.text = idl_type
    units = etree.SubElement(it, "Units")
    units.text = unit
    count = etree.SubElement(it, "Count")
    count.text = str(element_count)


def _write_tree_to_file(tree: etree.Element, filename: str) -> None:
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir()
    t = etree.ElementTree(tree)
    t_contents = (
        etree.tostring(
            t,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )
        .decode()
        .replace("'", '"')
    )
    f = open(filename, "w")
    f.write(t_contents)
    f.close()


def collect_unique_command_items_per_group(
    command_topics: dict[str, typing.Any],
) -> dict[str, typing.Any]:
    command_items_per_group: dict[str, typing.Any] = {}
    for command_topic in command_topics:
        hvac_topic = HvacTopic[command_topic].value
        command_group = next(
            (group for group, topic in DEVICE_GROUPS.items() if hvac_topic in topic),
            None,
        )
        if not command_group:
            raise ValueError(f"Unknown command topic {command_topic=}")
        if command_group not in command_items_per_group:
            command_items_per_group[command_group] = []
        command_items_per_group[command_group].append(command_topics[command_topic])
    # Filter out the duplicates
    unique_command_items_per_group: dict[str, typing.Any] = {}
    for command_group in command_items_per_group:
        unique_command_items_per_group[command_group] = [
            i
            for n, i in enumerate(command_items_per_group[command_group])
            if i not in command_items_per_group[command_group][n + 1 :]
        ][0]
    # Remove "comandoEncendido" command item
    for command_group in unique_command_items_per_group:
        command_items = unique_command_items_per_group[command_group]
        if "comandoEncendido" in command_items:
            del command_items["comandoEncendido"]
    # Remove empty command_groups
    unique_command_items_per_group = {
        group: items for group, items in unique_command_items_per_group.items() if items
    }
    return unique_command_items_per_group


def _create_telemetry_xml() -> None:
    """Create the Telemetry XML file."""
    # Create a list of topic items that should be events.
    topic_items_that_should_be_events = [
        val["item"].replace("dynalene", "dyn")
        for topic, val in EVENT_TOPIC_DICT.items()
    ]
    for telemetry_topic in xml.telemetry_topics:
        st = etree.SubElement(telemetry_root, "SALTelemetry")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        telemetry_topic_name = telemetry_topic
        efdb_topic.text = f"HVAC_{telemetry_topic}"
        description = etree.SubElement(st, "Description")
        if telemetry_topic == "dynaleneP05":
            telemetry_topic_name = "Dynalene"
        description.text = f"Telemetry for the {telemetry_topic_name} device."
        for telemetry_item in xml.telemetry_topics[telemetry_topic]:
            # Skip if a topic item should be an event.
            if telemetry_item in topic_items_that_should_be_events:
                continue
            _create_item_element(
                st,
                telemetry_topic,
                telemetry_item,
                xml.telemetry_topics[telemetry_topic][telemetry_item]["idl_type"],
                xml.telemetry_topics[telemetry_topic][telemetry_item]["unit"],
                _translate_item(telemetry_item),
                1,
            )
    _write_tree_to_file(telemetry_root, telemetry_filename)


def _create_command_sub_element(
    command_name: str, description_text: str
) -> etree.SubElement:
    st = etree.SubElement(command_root, "SALCommand")
    sub_system = etree.SubElement(st, "Subsystem")
    sub_system.text = "HVAC"
    efdb_topic = etree.SubElement(st, "EFDB_Topic")
    efdb_topic.text = f"HVAC_command_{command_name}"
    description = etree.SubElement(st, "Description")
    description.text = f"{description_text}"
    return st


def _create_command_xml(command_items_per_group: dict[str, typing.Any]) -> None:
    """Create the Command XML file."""

    # Add general enable and disable commands for a single device.
    for command in ["enable", "disable"]:
        description_text = f"{to_camel_case(command)} an HVAC device."
        st = _create_command_sub_element(f"{command}Device", description_text)
        description_text = (
            f"The ID indicating which device needs to be {command}d. The IDs "
            "can be found in the DeviceId enumeration."
        )
        _create_item_element(
            st, f"{command}", "device_id", "long", "unitless", description_text, 1
        )

    # Create configuration commands for the devices grouped by similar
    # functionality
    for command_group in command_items_per_group:
        if command_group == "DYNALENE":
            # Dynalene commands are treated separately below.
            continue
        description_text = f"Configure a {command_group} device."
        st = _create_command_sub_element(
            f"config{to_camel_case(command_group)}s", description_text
        )

        command_items = command_items_per_group[command_group]
        description_text = f"Device ID; one of the DeviceId_{to_camel_case(command_group, True)} enums."
        _create_item_element(
            st, command_group, "device_id", "int", "unitless", description_text, 1
        )
        for command_item in command_items:
            _create_item_element(
                st,
                command_group,
                command_item,
                command_items[command_item]["idl_type"],
                command_items[command_item]["unit"],
                _translate_item(command_item),
                1,
            )

    # Add the Dynalene commands.
    dynalene_group = command_items_per_group["DYNALENE"]
    for dynalene_item in dynalene_group:
        description_text = f"Set Dynalene {dynalene_item}."
        st = _create_command_sub_element(f"{dynalene_item}", description_text)
        _create_item_element(
            st,
            dynalene_item,
            dynalene_item,
            dynalene_group[dynalene_item]["idl_type"],
            dynalene_group[dynalene_item]["unit"],
            _translate_item(dynalene_item),
            1,
        )

    _write_tree_to_file(command_root, command_filename)


def _create_enumeration_element_from_enum(my_enum: enum.Enum) -> None:
    # The "type: ignore" on the next line is to keep MyPy happy. If omitted,
    # it will complain that "Enum" has no attribute "__name__" or "__iter__".
    string = ",\n    ".join(
        f"{my_enum.__name__}_{item.name}={item.value}"  # type: ignore
        for item in my_enum  # type: ignore
    )
    st = etree.SubElement(events_root, "Enumeration")
    st.text = f"\n    {string}\n  "


def _create_events_xml(command_items_per_group: dict[str, typing.Any]) -> None:
    """Create the Events XML file."""
    # Create the Enumerations.
    _create_enumeration_element_from_enum(DeviceId)
    _create_enumeration_element_from_enum(DynaleneState)
    _create_enumeration_element_from_enum(DynaleneTankLevel)

    # Create the events. In order to add events, simply add dictionary
    # elements as follows:
    event_topics = {
        "deviceEnabled": {
            "device_ids": {
                "idl_type": "long long",
                "unit": "unitless",
                "description": "Bitmask indicating which devices currently are "
                "enabled (1) or disabled (0). The order of the bits is determined "
                "by the order of the devices in the DeviceId enumeration",
                "count": str(len(DeviceId)),
            }
        },
    }

    for event_topic in event_topics:
        st = etree.SubElement(events_root, "SALEvent")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = f"HVAC_logevent_{event_topic}"
        description = etree.SubElement(st, "Description")
        description.text = "Report which devices are enabled."
        for events_item in event_topics[event_topic]:
            _create_item_element(
                st,
                event_topic,
                events_item,
                event_topics[event_topic][events_item]["idl_type"],
                event_topics[event_topic][events_item]["unit"],
                event_topics[event_topic][events_item]["description"],
                1,
            )

    for command_group in command_items_per_group:
        if command_group == "DYNALENE":
            # Dynalene events are treated separately below.
            continue
        st = etree.SubElement(events_root, "SALEvent")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = (
            f"HVAC_logevent_{to_camel_case(command_group, True)}Configuration"
        )
        description = etree.SubElement(st, "Description")
        description.text = f"Configuration of a {command_group} device."

        command_items = command_items_per_group[command_group]
        description_text = f"Device ID; one of the DeviceId_{to_camel_case(command_group, True)} enums."
        _create_item_element(
            st, command_group, "device_id", "int", "unitless", description_text, 1
        )
        for command_item in command_items:
            _create_item_element(
                st,
                command_group,
                command_item,
                command_items[command_item]["idl_type"],
                command_items[command_item]["unit"],
                _translate_item(command_item),
                1,
            )

    # Add Dynalene command events.
    dynalene_group = command_items_per_group["DYNALENE"]
    for dynalene_item in dynalene_group:
        st = etree.SubElement(events_root, "SALEvent")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = f"HVAC_logevent_{dynalene_item}"
        description = etree.SubElement(st, "Description")
        description.text = f"Set Dynalene {dynalene_item}."
        _create_item_element(
            st,
            dynalene_item,
            dynalene_item,
            dynalene_group[dynalene_item]["idl_type"],
            dynalene_group[dynalene_item]["unit"],
            _translate_item(dynalene_item),
            1,
        )

    # Add Dynalene State and Dynalene Safety State events.
    for event_topic in EVENT_TOPIC_DICT:
        st = etree.SubElement(events_root, "SALEvent")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = f"HVAC_logevent_{EVENT_TOPIC_DICT[event_topic]['item']}"
        description = etree.SubElement(st, "Description")
        description.text = EVENT_TOPIC_DICT[event_topic]["evt_description"]
        _create_item_element(
            st,
            event_topic,
            "state",
            (
                "int"
                if EVENT_TOPIC_DICT[event_topic]["type"] == "enum"
                else EVENT_TOPIC_DICT[event_topic]["type"]
            ),
            "unitless",
            EVENT_TOPIC_DICT[event_topic]["item_description"],
            1,
        )

    for event_topic in xml.event_topics:
        st = etree.SubElement(events_root, "SALEvent")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = f"HVAC_logevent_{event_topic}"
        description = etree.SubElement(st, "Description")
        description.text = f"{event_topic[0].upper()}"
        for event_item in xml.event_topics[event_topic]:
            _create_item_element(
                st,
                event_topic,
                event_item,
                xml.event_topics[event_topic][event_item]["idl_type"],
                xml.event_topics[event_topic][event_item]["unit"],
                _split_event_description(event_item),
                1,
            )

    _write_tree_to_file(events_root, events_filename)


def create_xml() -> None:
    command_items_per_group = collect_unique_command_items_per_group(xml.command_topics)
    _create_telemetry_xml()
    _create_command_xml(command_items_per_group)
    _create_events_xml(command_items_per_group)


if __name__ == "__main__":
    create_xml()
