import re
from lsst.ts.hvac.hvac_enums import Escape, dictionary


def convert_mqtt_to_xml(topic):
    """
    Transform an MQTT Topic string into a Topic name XML string.

    Parameters
    ----------
    topic : `str`
        The MQTT Topic string to transform
    """
    # escape special characters
    for k in Escape:
        # escape at the start of the line
        topic = re.sub(rf"^{k.value}", rf"{k.name}_", topic)
        # escape at the end of the line
        topic = re.sub(rf"{k.value}$", rf"_{k.name}", topic)
        # escape the rest
        topic = re.sub(rf"{k.value}", rf"_{k.name}_", topic)
    # convert to lower case so we can camelcase next
    topic = topic.lower()
    # convert words separated by underscores to a single camelcased word
    topic = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), topic)
    return topic


def convert_xml_to_mqtt(xml):
    """
    Transform a Topic name XML string into an MQTT Topic string.

    Parameters
    ----------
    xml : `str`
        The Topic name XML string to transform
    """
    # convert camelcase to lower case prepended with an underscore
    xml = "_" + re.sub(r"([A-Z])", lambda m: m.group(1).lower(), xml)
    # make everything upper case because that is what the MQTT topics should be
    xml = xml.upper()
    # unescape special characters
    for k in Escape:
        # unescape at the start of the line
        xml = re.sub(rf"^{k.name}_", rf"{k.value}", xml)
        # unescape at the end of the line
        xml = re.sub(rf"_{k.name}$", rf"{k.value}", xml)
        # unescape the rest
        xml = re.sub(rf"_{k.name}_", rf"{k.value}", xml)
    return xml


def translate_spanish_to_english(topic):
    topic = re.sub(r"^LSST/", r"", topic)
    topic = re.sub(r"_", r" ", topic)
    topic = re.sub(r"-", r" ", topic)
    topic = re.sub(r"&", r" and ", topic)
    topic = re.sub(r"/", r" - ", topic)
    for key in dictionary.keys():
        topic = re.sub(rf"{key}", rf"{dictionary[key]} ", topic)
    topic = re.sub(r"  ", r" ", topic)
    return topic.strip()
