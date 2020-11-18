# This file is part of ts_hvac.
#
# Developed for the LSST Telescope and Site Systems.
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
    "extract_topic_and_item",
    "get_topics",
    "get_telemetry_mqtt_topics_and_items",
    "get_items_for_topic",
    "collect_topics_and_items",
    "create_xml",
]

import pandas
import pathlib
import re

from lxml import etree

from lsst.ts.hvac.hvac_enums import (
    CommandItem,
    SPANISH_TO_ENGLISH_DICTIONARY,
    HvacTopic,
    TelemetryItem,
)

# This dict contains the general MQTT topics (one for each sub-system) as keys
# and a dictionary representing the items as value. The structure is
# "general_topic" : {
#     "item": {
#         "idl_type": idl_type,
#         "unit": unit,
#         "topic_type": topic_type,
#         "limits": (lower_limit, upper_limit),
#     }
# }
hvac_topics = {}

# This dict contains the general telemetry topics (retrieved by using the
# `HvacTopic` enum) as keys and a dictionary representing the telemetry items
# (retrieved by using the `TelemetryItem` enum) as values. The structure is
# "HvacTopic" : {
#     "TelemetryItem": {
#         "idl_type": idl_type,
#         "unit": unit,
#     }
# }
telemetry_topics = {}

# This dict contains the general command topics (retrieved by using the
# `HvacTopic` enum) as keys and a dictionary representing the command items
# (retrieved by using the `CommandItem` enum) as values. The structure is
# "HvacTopic" : {
#     "CommandItem": {
#         "idl_type": idl_type,
#         "unit": unit,
#     }
# }
command_topics = {}

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
data_dir = pathlib.Path(__file__).resolve().parents[4].joinpath("data")

input_dir = data_dir.joinpath("input/")
dat_control_filename = input_dir.joinpath("Direccionamiento_Lsst_Final_rev0.csv")

output_dir = data_dir.joinpath("output/")
telemetry_filename = output_dir.joinpath("HVAC_Telemetry.xml")
command_filename = output_dir.joinpath("HVAC_Commands.xml")

# Start general XML related items.
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
# End general XML related items.

# These topics are always enabled because there are no MQTT commands to enable
# or disable them.
TOPICS_ALWAYS_ENABLED = [
    "LSST/PISO01/BOMBA_AGUA_FRIA",
    "LSST/PISO01/GENERAL",
    "LSST/PISO01/VALVULA",
]


def extract_topic_and_item(topic_and_item):
    """Extract the generic topic, representing a HVAC subsystem, and item,
     representing a published value of the subsystem, from a string.

    This method searches for the last occurrence of that forward slash and will
    return the part before the slash as topic and after the slash as item.

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


def get_topics():
    """Convenience method to collect all generic topics, representing the HVAC
    subsystems.

    Returns
    -------
    topics: `set`
        A set of all generic topics.

    """
    global hvac_topics
    if not bool(hvac_topics):
        collect_topics_and_items()
    topics = set()
    for topic_and_item in hvac_topics:
        topic_type = hvac_topics[topic_and_item]["topic_type"]
        if topic_type == "WRITE" and topic_and_item.endswith("COMANDO_ENCENDIDO_LSST"):
            topic, item = extract_topic_and_item(topic_and_item)
            topics.add(topic)
    for topic in TOPICS_ALWAYS_ENABLED:
        topics.add(topic)

    return topics


def get_telemetry_mqtt_topics_and_items():
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
    telemetry_mqtt_topics = {}
    for hvac_topic in get_topics():
        items = get_items_for_topic(hvac_topic)
        topic_items = {}
        for item in items:
            # Make sure only telemetry topics are used.
            if items[item]["topic_type"] == "READ":
                topic_items[item] = items[item]
        telemetry_mqtt_topics[hvac_topic] = topic_items
    return telemetry_mqtt_topics


def _parse_limits(limits_string):
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
    match = re.match(r"^(-?\d+)(/| a |% a )(-?\d+)%?$", limits_string)
    if match:
        print(f"{limits_string} = {match.groups()}")
        # lower_limit = float(match.group(1))
        # upper_limit = float(match.group(2))
        lower_limit = 0
        upper_limit = 1
    elif re.match(r"^\d$", limits_string):
        lower_limit = 0
        upper_limit = 100
    else:
        raise ValueError(f"Couldn't match limits_string {limits_string}")

    return lower_limit, upper_limit


def get_items_for_topic(topic):
    """Convenience method to get all items for an generic topic.

    Parameters
    ----------
    topic: `str`
        The generic topic to get the XML items for.

    Returns
    -------
    items: `dict`
        A dict containing all items for the topic.

    Notes
    -----
    The structure of the dictionary is exactly the same as for the items in
    `hvac_topics`.

    """
    global hvac_topics
    if not bool(hvac_topics):
        collect_topics_and_items()
    items = {}
    for hvac_topic in hvac_topics:
        tpc, item = extract_topic_and_item(hvac_topic)
        if tpc == topic:
            items[item] = hvac_topics[hvac_topic]
    return items


def _generic_collect_topics_and_items(row, topics, items):
    """Collect XML topics and items from a row read from the CSV file produced
    from the Excel file with the Rubin Observatory HVAC system information
    sent by DATControl.

    The input CSV file can be found in the python/data/input directory and was
    produced by collecting the data in all tabs in the Excel file into one tab
    and exporting that tab to CSV.

    Parameters
    ----------
    row: `list`
        A row read from the CSV file.
    topics: `dict`
        The dictionary to add the XML topic and item, found in the row, to.
    items: enum.Enum
        The Enum that is used to translate the HVAC topics and items to XML
        topics and items.


    Raises
    -------
    ValueError
        In case a HVAC topic or item is not present in the Telemetry, Item or
        Command Enums. This error will only be raised during development of the
        code and serves to ensure that all HVAC topics and items are present in
        the Enums.

    Notes
    -----
    The hvac_topics dictionary gets filled as well by this method.

    """
    global hvac_topics
    topic_found = False
    topic_and_item = row["topic_and_item"]
    topic, item = extract_topic_and_item(topic_and_item)

    for hvac_topic in HvacTopic:
        if hvac_topic.value in topic:
            if hvac_topic.name not in topics:
                topics[hvac_topic.name] = {}

            item_found = False
            for hvac_item in items:
                if hvac_item.value == item:
                    idl_type = (
                        "boolean" if row["range"] == "TRUE (O) FALSE" else "float"
                    )
                    if row["unit"] == "-":
                        unit = "unitless"
                    elif row["unit"] == "°C":
                        unit = "deg_C"
                    elif row["unit"] == "bar":
                        unit = "bar"
                    elif row["unit"] == "%":
                        unit = "%"
                    else:
                        raise ValueError(f"Unknown unit {row['unit']}")
                    topics[hvac_topic.name][hvac_item.name] = {
                        "idl_type": idl_type,
                        "unit": unit,
                    }
                    hvac_topics[topic_and_item] = {
                        "idl_type": idl_type,
                        "unit": unit.strip(),
                        "topic_type": row["rw"].strip(),
                        "limits": _parse_limits(row["limits"].strip()),
                    }

                    item_found = True
                    break
            if not item_found:
                raise ValueError(f"TelemetryItem '{item}' for {topic} not found.")

            topic_found = True
            break
    if not topic_found:
        raise ValueError(f"Topic {topic} in topic_and_item {topic_and_item} not found.")


def collect_topics_and_items():
    """Loop over all rows in the CSV file and extracts either telemetry topic
    data or command topic data depending on the contents of the 8th column in
    the CSV row.
    """
    with open(dat_control_filename) as csv_file:
        csv_reader = pandas.read_csv(
            csv_file,
            delimiter=";",
            index_col=False,
            dtype=str,
            names=names,
            keep_default_na=False,
        )
        for index, row in csv_reader.iterrows():
            if row["rw"].strip() == "READ":
                _generic_collect_topics_and_items(row, telemetry_topics, TelemetryItem)
            if row["rw"].strip() == "WRITE":
                _generic_collect_topics_and_items(row, command_topics, CommandItem)


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
        etree.tostring(t, pretty_print=True, xml_declaration=True, encoding="utf-8",)
        .decode()
        .replace("'", '"')
    )
    f = open(filename, "w")
    f.write(t_contents)
    f.close()


def _create_telemetry_xml():
    """Create the Telemetry XML file.
    """
    for telemetry_topic in telemetry_topics:
        st = etree.SubElement(telemetry_root, "SALTelemetry")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = "HVAC_" + telemetry_topic
        for telemetry_item in telemetry_topics[telemetry_topic]:
            _create_item_element(
                st,
                telemetry_topic,
                telemetry_item,
                telemetry_topics[telemetry_topic][telemetry_item]["idl_type"],
                telemetry_topics[telemetry_topic][telemetry_item]["unit"],
            )
    _write_tree_to_file(telemetry_root, telemetry_filename)


def _separate_enable_and_configuration_commands():
    """Separates the Enable and Configuration commands so that switching
    sub-systems on and off doesn't require providing the configuration as well.
    """
    global command_topics

    separated_command_topics = {}
    for command_topic in command_topics:
        items = command_topics[command_topic]
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
    command_topics = separated_command_topics


def _create_command_xml():
    """Create the Command XML file.
    """
    _separate_enable_and_configuration_commands()

    for command_topic in command_topics:
        st = etree.SubElement(command_root, "SALCommand")
        sub_system = etree.SubElement(st, "Subsystem")
        sub_system.text = "HVAC"
        efdb_topic = etree.SubElement(st, "EFDB_Topic")
        efdb_topic.text = "HVAC_command_" + command_topic
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
    collect_topics_and_items()
    _create_telemetry_xml()
    _create_command_xml()


if __name__ == "__main__":
    create_xml()
