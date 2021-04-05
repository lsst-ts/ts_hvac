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

import pathlib
import re

from lxml import etree

from lsst.ts.hvac.hvac_enums import SPANISH_TO_ENGLISH_DICTIONARY
from lsst.ts.hvac.xml.mqtt_info_reader import MqttInfoReader

# Find the data directory relative to the location of this file.
data_dir = pathlib.Path(__file__).resolve().parents[4].joinpath("data")

output_dir = data_dir.joinpath("output/")
telemetry_filename = output_dir.joinpath("HVAC_Telemetry.xml")
command_filename = output_dir.joinpath("HVAC_Commands.xml")

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


def _create_item_element(parent, topic, item, idl_type, unit):
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
    """
    it = etree.SubElement(parent, "item")
    efdb_name = etree.SubElement(it, "EFDB_Name")
    efdb_name.text = item
    description = etree.SubElement(it, "Description")
    description.text = _translate_item(item)
    idl_type_elt = etree.SubElement(it, "IDL_Type")
    idl_type_elt.text = idl_type
    units = etree.SubElement(it, "Units")
    units.text = unit
    count = etree.SubElement(it, "Count")
    count.text = "1"


def _write_tree_to_file(tree, filename):
    if not output_dir.exists():
        output_dir.mkdir()
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
            )
    _write_tree_to_file(telemetry_root, telemetry_filename)


def _separate_enable_and_configuration_commands():
    """Separates the Enable and Configuration commands so that switching
    sub-systems on and off doesn't require providing the configuration as well.
    """
    separated_command_topics = {}
    for command_topic in xml.command_topics:
        items = xml.command_topics[command_topic]
        for item in items:
            if item in ["comandoEncendido"]:
                enable_topc = f"{command_topic}_enable"
                if enable_topc not in separated_command_topics:
                    separated_command_topics[enable_topc] = {}
                separated_command_topics[enable_topc][item] = items[item]
            else:
                config_topc = f"{command_topic}_config"
                if config_topc not in separated_command_topics:
                    separated_command_topics[config_topc] = {}
                separated_command_topics[config_topc][item] = items[item]
    return separated_command_topics


def _create_command_xml():
    """Create the Command XML file."""
    command_topics = _separate_enable_and_configuration_commands()

    for command_topic in command_topics:
        st = etree.SubElement(command_root, "SALCommand")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = "HVAC_command_" + command_topic
        description = etree.SubElement(st, "Description")
        if "_config" in command_topic:
            description_text = f"Configuration command for the {command_topic.replace('_config', '')} device."
        else:
            description_text = (
                f"Enable command for the {command_topic.replace('_enable', '')} device."
            )
        description.text = f"{description_text}"
        for command_item in command_topics[command_topic]:
            _create_item_element(
                st,
                command_topic,
                command_item,
                command_topics[command_topic][command_item]["idl_type"],
                command_topics[command_topic][command_item]["unit"],
            )
    _write_tree_to_file(command_root, command_filename)


def create_xml():
    xml.collect_hvac_topics_and_items_from_json()
    _create_telemetry_xml()
    _create_command_xml()


if __name__ == "__main__":
    create_xml()
