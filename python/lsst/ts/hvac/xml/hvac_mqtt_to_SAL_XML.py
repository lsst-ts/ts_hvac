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
    "extract_topic_and_item",
    "get_topics",
    "get_telemetry_mqtt_topics_and_items",
    "get_items_for_topic",
    "collect_topics_and_items",
    "create_xml",
]

import json
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

# TODO DM-28997: Temporary boolean to make sure that the CSV file is used as
#  input and not the JSON file. As soon as the JSON file has the correct
#  content as verified against the HVAC server, the Excel file will be removed
#  along with this boolean and the code that uses it will be updated
#  accordingly.
use_csv = True

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
# TODO DM-28997: Remove this filename variable as soon as the content of the
#  JSON file is verified against the HVAC server.
dat_control_csv_filename = input_dir.joinpath(
    "Direccionamiento_Lsst_Final_JSON_rev2021_rev4.csv"
)
dat_control_json_filename = input_dir.joinpath(
    "JSON_V7_PUBLICACIONES_SUSCRIPCIONES.json"
)

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
TOPICS_ALWAYS_ENABLED = frozenset(
    ("LSST/PISO01/BOMBA_AGUA_FRIA", "LSST/PISO01/GENERAL", "LSST/PISO01/VALVULA",)
)

TOPICS_WITHOUT_CONFIGURATION = frozenset(
    (
        "LSST/PISO01/BOMBA_AGUA_FRIA",
        "LSST/PISO01/GENERAL",
        "LSST/PISO01/VALVULA",
        "LSST/PISO01/VEA_01",
        "LSST/PISO05/VEA_01",
        "LSST/PISO05/VEA_08",
        "LSST/PISO05/VEA_09",
        "LSST/PISO05/VEA_10",
        "LSST/PISO05/VEA_11",
        "LSST/PISO05/VEA_12",
        "LSST/PISO05/VEA_13",
        "LSST/PISO05/VEA_14",
        "LSST/PISO05/VEA_15",
        "LSST/PISO05/VEA_16",
        "LSST/PISO05/VEA_17",
        "LSST/PISO01/VEC_01",
        "LSST/PISO01/VIN_01",
        "LSST/PISO04/VEX_03/DAMPER_LOWER/GENERAL",
        "LSST/PISO04/VEX_04/ZONA_CARGA/GENERAL",
    )
)


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


def get_command_mqtt_topics_and_items():
    """Convenience method to collect all MQTT topics and their items that
    accept commands.

    Returns
    -------
    command_mqtt_topics: `dict`
        A dictionary with the MQTT topics as keys and their items as value.

    Notes
    -----
    The structure of the returned dictionary is exactly the same as for the
    hvac_topics dictionary. The only difference is that the telemetry topics
    (indicated by topic type READ) have been filtered out.
    """
    command_mqtt_topics = {}
    for hvac_topic in get_topics():
        items = get_items_for_topic(hvac_topic)
        topic_items = {}
        for item in items:
            # Make sure only telemetry topics are used.
            if items[item]["topic_type"] == "WRITE":
                topic_items[item] = items[item]
        command_mqtt_topics[hvac_topic] = topic_items
    return command_mqtt_topics


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


def _determine_unit(unit_string):
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


def _generic_collect_topics_and_items(
    topic_and_item, topic_type, idl_type, unit, limits, topics, items
):
    """Collect XML topics and items from a row read from the CSV file produced
    from the Excel file with the Rubin Observatory HVAC system information
    sent by DatControl.

    The input CSV file can be found in the python/data/input directory and was
    produced by collecting the data in all tabs in the Excel file into one tab
    and exporting that tab to CSV.

    Parameters
    ----------
    topic_and_item: `str`
        The topic and item to parse, for instance

            "LSST/PISO02/CRACK01/ESTADO_FUNCIONAMIENTO"

        would be the topic "LSST/PISO02/CRACK01" and the item
        "ESTADO_FUNCIONAMIENTO"
    topic_type: `str`
        Indicates whether the topic is a telemetry topic (READ) or a command
        topic (WRITE).
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
    topic, item = extract_topic_and_item(topic_and_item)

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
                    hvac_topics[topic_and_item] = {
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
        raise ValueError(f"Topic {topic} in topic_and_item {topic_and_item} not found.")


def collect_topics_and_items():
    """Loop over all rows in the CSV file and extracts either telemetry topic
    data or command topic data depending on the contents of the 8th column in
    the CSV row.
    """
    topics = {}
    # TODO DM-28997: Remove this if statement as soon as the content of the
    #  JSON file is verified against the HVAC server.
    if use_csv:
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
                topic_and_item = row["topic_and_item"]
                idl_type = "float" if "ANALOG" in row["signal"] else "boolean"
                topic_type = row["rw"].strip()
                if topic_type in ["READ", "WRITE"]:
                    unit = _determine_unit(row["unit"])
                    limits = _parse_limits(row["limits"].strip())
                    topics[topic_and_item] = {
                        "idl_type": idl_type,
                        "topic_type": topic_type,
                        "unit": unit,
                        "limits": limits,
                    }
    else:
        print(f"Loading JSON file {dat_control_json_filename}")
        with open(dat_control_json_filename) as f:
            all_topics = json.loads(f.read())
            for topic in all_topics["BOUNDQUERYRESULT"]:
                topic_and_item = topic["POINT"]
                # Command topics always end in "_LSST" and telemetry topics
                # never do so that's how the distinction is made in this code.
                topic_type = "WRITE" if "_LSST" in topic_and_item else "READ"
                idl_type = "float" if "Numeric" in topic["TYPE"] else "boolean"
                unit = _determine_unit(topic["UNIT"])
                limits = _parse_limits(topic["LIMIT"])
                topics[topic_and_item] = {
                    "idl_type": idl_type,
                    "topic_type": topic_type,
                    "unit": unit,
                    "limits": limits,
                }

    for topic_and_item in sorted(topics.keys()):
        idl_type = topics[topic_and_item]["idl_type"]
        topic_type = topics[topic_and_item]["topic_type"]
        unit = topics[topic_and_item]["unit"]
        limits = topics[topic_and_item]["limits"]
        if topic_type == "READ":
            _generic_collect_topics_and_items(
                topic_and_item,
                topic_type,
                idl_type,
                unit,
                limits,
                telemetry_topics,
                TelemetryItem,
            )
        if topic_type == "WRITE":
            _generic_collect_topics_and_items(
                topic_and_item,
                topic_type,
                idl_type,
                unit,
                limits,
                command_topics,
                CommandItem,
            )


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
        efdb_topic.text = f"HVAC_{telemetry_topic}"
        description = etree.SubElement(st, "Description")
        description.text = f"Telemetry for the {telemetry_topic} device."
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
    collect_topics_and_items()
    _create_telemetry_xml()
    _create_command_xml()


if __name__ == "__main__":
    create_xml()
