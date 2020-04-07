#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import re
from lsst.ts.hvac.xml import topic_converter
from lxml import etree


data_dir = "data/"
input_dir = data_dir + "input/"
dat_control_filename = input_dir + "Matriz BMS LSST - Cx-PS.csv"
output_dir = data_dir + "output/"
telemetry_filename = output_dir + "HVAC_Telemetry.xml"
command_filename = output_dir + "HVAC_Commands.xml"
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


def create_xml():
    """
    Creates the HVAC SAL XML files to be used in ts_xml.
    """
    with open(dat_control_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        for row in csv_reader:
            if row[9]:
                row_n = next(csv_reader)
                row9 = row[9]
                if re.match(r"PUBLICACION", row_n[7]) and row9:
                    topic = re.sub(r"/#", "", row9)
                    st = etree.SubElement(telemetry_root, "SALTelemetry")
                    sub_system = etree.SubElement(st, "Subsystem")
                    sub_system.text = "HVAC"
                    efdb_topic = etree.SubElement(st, "EFDB_Topic")
                    efdb_topic.text = "HVAC_" + topic_converter.convert_mqtt_to_xml(
                        topic
                    )
                    while True:
                        if re.match(r"PUBLICACION", row_n[7]) and row9:
                            create_child_element(row_n, st, topic, "PUBLICACION")
                        else:
                            break
                        row_n = next(csv_reader)
                if re.match(r"SUSCRIPCION", row_n[7]) and row9:
                    topic = re.sub(r"/#", "", row9)
                    st = etree.SubElement(command_root, "SALCommand")
                    sub_system = etree.SubElement(st, "Subsystem")
                    sub_system.text = "HVAC"
                    prepared_topic_name = topic_converter.convert_mqtt_to_xml(topic)
                    efdb_topic = etree.SubElement(st, "EFDB_Topic")
                    efdb_topic.text = "HVAC_command_" + prepared_topic_name
                    alias = etree.SubElement(st, "Alias")
                    alias.text = prepared_topic_name
                    while True:
                        if re.match(r"SUSCRIPCION", row_n[7]) and row9:
                            create_child_element(row_n, st, topic, "SUSCRIPCION")
                        else:
                            break
                        row_n = next(csv_reader)
        print("Done.")

    t = etree.ElementTree(telemetry_root)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    t.write(
        telemetry_filename, pretty_print=True, xml_declaration=True, encoding="utf-8"
    )
    c = etree.ElementTree(command_root)
    c.write(command_filename, pretty_print=True, xml_declaration=True, encoding="utf-8")

    # print(open(command_filename).read())


def create_child_element(row_n, st, topic, elt_type):
    row8 = re.sub(r"PISO([12345])", r"PISO0\1", row_n[8])
    it = etree.SubElement(st, "item")
    efdb_name = etree.SubElement(it, "EFDB_Name")
    orig_topic = re.sub(rf"{topic}/", "", row8)
    efdb_name.text = topic_converter.convert_mqtt_to_xml(orig_topic)
    description = etree.SubElement(it, "Description")
    description.text = topic_converter.translate_spanish_to_english(orig_topic)
    idl_type = etree.SubElement(it, "IDL_Type")
    if elt_type is "PUBLICACION":
        idl_type.text = "boolean" if re.match(r"BINARY", row_n[5]) else "float"
    elif elt_type is "SUSCRIPCION":
        idl_type.text = "boolean" if re.match(r"^true", row_n[6]) else "float"
    units = etree.SubElement(it, "Units")
    units.text = "unitless"
    count = etree.SubElement(it, "Count")
    count.text = "1"


if __name__ == "__main__":
    create_xml()
