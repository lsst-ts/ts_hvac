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

import re

from lxml import etree

from lsst.ts.hvac.enums import SPANISH_TO_ENGLISH_DICTIONARY, HvacTopic
from lsst.ts.hvac.utils import to_camel_case
from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader, DATA_DIR
from lsst.ts.idl.enums.HVAC import DeviceId, DEVICE_GROUPS

OUTPUT_DIR = DATA_DIR / "output"
telemetry_filename = OUTPUT_DIR / "HVAC_Telemetry.xml"
command_filename = OUTPUT_DIR / "HVAC_Commands.xml"
events_filename = OUTPUT_DIR / "HVAC_Events.xml"

XML_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
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
        "type='text/xsl' "
        + "href='http://lsst-sal.tuc.noao.edu/schema/SALTelemetrySet.xsl'",
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
        "type='text/xsl' "
        + "href='http://lsst-sal.tuc.noao.edu/schema/SALCommandSet.xsl'",
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
        "type='text/xsl' "
        + "href='http://lsst-sal.tuc.noao.edu/schema/SALEventSet.xsl'",
    )
)

xml = MqttInfoReader()


def _translate_item(item):
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
    translated_item = re.sub(r"([A-Z])", lambda m: " " + m.group(1), item).upper()
    for key in SPANISH_TO_ENGLISH_DICTIONARY.keys():
        translated_item = re.sub(
            rf"{key}", rf"{SPANISH_TO_ENGLISH_DICTIONARY[key]}", translated_item
        )
    return translated_item


def _create_item_element(
    parent, topic, item, idl_type, unit, description_text, element_count
):
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


def _write_tree_to_file(tree, filename):
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


def collect_unique_command_items_per_group(command_topics):
    command_items_per_group = {}
    for command_topic in command_topics:
        hvac_topic = HvacTopic[command_topic].value
        command_group = next(
            (group for group, topic in DEVICE_GROUPS.items() if hvac_topic in topic),
            None,
        )
        if not command_group:
            raise ValueError(f"Unknown command topic {command_topic}")
        if command_group not in command_items_per_group:
            command_items_per_group[command_group] = []
        command_items_per_group[command_group].append(command_topics[command_topic])
    # Filter out the duplicates
    unique_command_items_per_group = {}
    for command_group in command_items_per_group:
        unique_command_items_per_group[command_group] = [
            i
            for n, i in enumerate(command_items_per_group[command_group])
            if i not in command_items_per_group[command_group][n + 1 :]
        ][0]
    # Remove "comandoEncendido" command item
    for command_group in unique_command_items_per_group:
        command_items = unique_command_items_per_group[command_group]
        del command_items["comandoEncendido"]
    # Remove empty command_groups
    unique_command_items_per_group = {
        group: items for group, items in unique_command_items_per_group.items() if items
    }
    return unique_command_items_per_group


def _create_telemetry_xml():
    """Create the Telemetry XML file."""
    for telemetry_topic in xml.telemetry_topics:
        st = etree.SubElement(telemetry_root, "SALTelemetry")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = f"HVAC_{telemetry_topic}"
        description = etree.SubElement(st, "Description")
        description.text = f"Telemetry for the {telemetry_topic} device."
        for telemetry_item in xml.telemetry_topics[telemetry_topic]:
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


def _create_command_sub_element(command_name, description_text):
    st = etree.SubElement(command_root, "SALCommand")
    sub_system = etree.SubElement(st, "Subsystem")
    sub_system.text = "HVAC"
    efdb_topic = etree.SubElement(st, "EFDB_Topic")
    efdb_topic.text = f"HVAC_command_{command_name}"
    description = etree.SubElement(st, "Description")
    description.text = f"{description_text}"
    return st


def _create_command_xml(command_items_per_group):
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
    _write_tree_to_file(command_root, command_filename)


def _create_enumeration_element_from_dict(my_dict):
    string = ",\n    ".join(
        f"{my_dict.__name__}_{item.name}={item.value}" for item in my_dict
    )
    st = etree.SubElement(events_root, "Enumeration")
    st.text = f"\n    {string}\n  "


def _create_events_xml(command_items_per_group):
    """Create the Events XML file."""
    # Create the Enumerations.
    _create_enumeration_element_from_dict(DeviceId)

    # Create the events. In order to add events, simply add dictionary
    # elements as follows:
    events_topics = {
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

    for events_topic in events_topics:
        st = etree.SubElement(events_root, "SALEvent")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = f"HVAC_logevent_{events_topic}"
        description = etree.SubElement(st, "Description")
        description.text = "Report which devices are enabled."
        for events_item in events_topics[events_topic]:
            _create_item_element(
                st,
                events_topic,
                events_item,
                events_topics[events_topic][events_item]["idl_type"],
                events_topics[events_topic][events_item]["unit"],
                events_topics[events_topic][events_item]["description"],
                1,
            )

    for command_group in command_items_per_group:
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

    _write_tree_to_file(events_root, events_filename)


def create_xml():
    command_items_per_group = collect_unique_command_items_per_group(xml.command_topics)
    _create_telemetry_xml()
    _create_command_xml(command_items_per_group)
    _create_events_xml(command_items_per_group)


if __name__ == "__main__":
    create_xml()
