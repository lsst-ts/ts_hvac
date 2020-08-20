# This file is part of ts_hvac.
#
# Developed for the LSST Data Management System.
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

import csv
import os
import re

from lxml import etree

from lsst.ts.hvac.hvac_enums import CommandItem, dictionary, HvacTopic, TelemetryItem

telemetry_topics = {}
command_topics = {}
commands = {}

data_dir = "data/"
input_dir = data_dir + "input/"
dat_control_filename = input_dir + "Matriz BMS LSST - Cx-PS.csv"

output_dir = data_dir + "output/"
telemetry_filename = output_dir + "HVAC_Telemetry.xml"
command_filename = output_dir + "HVAC_Commands.xml"
XML_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
NSMAP = {"xsi": XML_NAMESPACE}
attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "noNamespaceSchemaLocation")
telemetry_root = etree.Element(
    "SALTelemetrySet", {attr_qname: "http://lsst-sal.tuc.noao.edu/schema/SALTelemetrySet.xsd"}, nsmap=NSMAP,
)
telemetry_root.addprevious(
    etree.ProcessingInstruction(
        "xml-stylesheet",
        "type='text/xsl' " + "href='http://lsst-sal.tuc.noao.edu/schema/SALTelemetrySet.xsl'",
    )
)
command_root = etree.Element(
    "SALCommandSet", {attr_qname: "http://lsst-sal.tuc.noao.edu/schema/SALCommandSet.xsd"}, nsmap=NSMAP,
)
command_root.addprevious(
    etree.ProcessingInstruction(
        "xml-stylesheet", "type='text/xsl' " + "href='http://lsst-sal.tuc.noao.edu/schema/SALCommandSet.xsl'",
    )
)


def collect_telemetry_topics_and_items(row):
    global telemetry_topics
    topic_found = False
    topic = row[8]
    for hvac_topic in HvacTopic:
        if hvac_topic.value in topic:
            # Treat topic "LSST/PISO1/TEMPERATURA_AMBIENTE" differently until
            # fixed.
            if hvac_topic == HvacTopic.temperatuaAmbienteP01:
                telemetry_item = TelemetryItem.temperaturaAmbiente
                idl_type = "float"
                telemetry_topics[hvac_topic.name] = {}
                telemetry_topics[hvac_topic.name][telemetry_item.name] = idl_type
                topic_found = True
                break

            item = re.sub(hvac_topic.value, "", topic)
            if hvac_topic.name not in telemetry_topics:
                telemetry_topics[hvac_topic.name] = {}

            item_found = False
            for telemetry_item in TelemetryItem:
                if telemetry_item.value == item:
                    idl_type = "boolean" if re.match(r"BINARY", row[5]) else "float"
                    telemetry_topics[hvac_topic.name][telemetry_item.name] = idl_type
                    item_found = True
                    break
            if not item_found:
                raise ValueError(f"TelemetryItem '{item}' for {topic} not found.")

            topic_found = True
            break
    if not topic_found:
        raise ValueError(f"Topic {topic} not found.")


def collect_command_topics_and_items(row):
    global command_topics
    global commands
    topic_found = False
    topic = row[8]
    for hvac_topic in HvacTopic:
        if hvac_topic.value in topic:
            command = re.sub(hvac_topic.value, "", topic)
            if hvac_topic.name not in command_topics:
                command_topics[hvac_topic.name] = {}

            item_found = False
            for command_item in CommandItem:
                if command_item.value == command:
                    idl_type = "boolean" if re.match(r"^true", row[6]) else "float"
                    command_topics[hvac_topic.name][command_item.name] = idl_type
                    item_found = True
                    break
            if not item_found:
                raise ValueError(f"CommandItem '{command}' for {topic} not found.")

            topic_found = True
            break
    if not topic_found:
        raise ValueError(f"Topic {topic} not found.")


def add_timestamp_to_telemetry_topics():
    global telemetry_topics
    for telemetry_topic in telemetry_topics:
        telemetry_topics[telemetry_topic]["timestamp"] = "double"


def collect_topics_and_items():
    with open(dat_control_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        for row in csv_reader:
            if row[7] == "PUBLICACION":
                collect_telemetry_topics_and_items(row)
            if row[7] == "SUSCRIPCION":
                collect_command_topics_and_items(row)
    add_timestamp_to_telemetry_topics()


def translate_item(item):
    item = re.sub(r"([A-Z])", lambda m: " " + m.group(1), item).upper()
    for key in dictionary.keys():
        item = re.sub(rf"{key}", rf"{dictionary[key]}", item)
    return item


def create_telemetry_xml():
    for telemetry_topic in telemetry_topics:
        st = etree.SubElement(telemetry_root, "SALTelemetry")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = "HVAC_" + telemetry_topic
        for telemetry_item in telemetry_topics[telemetry_topic]:
            if telemetry_item == "timestamp":
                it = etree.SubElement(st, "item")
                efdb_name = etree.SubElement(it, "EFDB_Name")
                efdb_name.text = telemetry_item
                description = etree.SubElement(it, "Description")
                description.text = "Time at which the data was determined (TAI unix seconds)."
                idl_type = etree.SubElement(it, "IDL_Type")
                idl_type.text = telemetry_topics[telemetry_topic][telemetry_item]
                units = etree.SubElement(it, "Units")
                units.text = "second"
                count = etree.SubElement(it, "Count")
                count.text = "1"
            else:
                it = etree.SubElement(st, "item")
                efdb_name = etree.SubElement(it, "EFDB_Name")
                efdb_name.text = telemetry_item
                description = etree.SubElement(it, "Description")
                description.text = translate_item(telemetry_item)
                idl_type = etree.SubElement(it, "IDL_Type")
                idl_type.text = telemetry_topics[telemetry_topic][telemetry_item]
                units = etree.SubElement(it, "Units")
                units.text = "unitless"
                count = etree.SubElement(it, "Count")
                count.text = "1"
    t = etree.ElementTree(telemetry_root)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    t.write(telemetry_filename, pretty_print=True, xml_declaration=True, encoding="utf-8")


def create_command_xml():
    for command_topic in command_topics:
        st = etree.SubElement(command_root, "SALCommand")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = "HVAC_command_" + command_topic
        alias = etree.SubElement(st, "Alias")
        alias.text = command_topic
        for command_item in command_topics[command_topic]:
            it = etree.SubElement(st, "item")
            efdb_name = etree.SubElement(it, "EFDB_Name")
            efdb_name.text = command_item
            description = etree.SubElement(it, "Description")
            description.text = translate_item(command_item)
            idl_type = etree.SubElement(it, "IDL_Type")
            idl_type.text = command_topics[command_topic][command_item]
            units = etree.SubElement(it, "Units")
            units.text = "unitless"
            count = etree.SubElement(it, "Count")
            count.text = "1"
    c = etree.ElementTree(command_root)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    c.write(command_filename, pretty_print=True, xml_declaration=True, encoding="utf-8")


def create_xml():
    create_telemetry_xml()
    create_command_xml()


def main():
    collect_topics_and_items()
    create_xml()


if __name__ == "__main__":
    main()
