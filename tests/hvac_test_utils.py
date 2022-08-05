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

import random

from lsst.ts.hvac.enums import CommandItem, HvacTopic
from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader


def get_random_config_data(topic: HvacTopic) -> dict[str, float]:
    """Generates random values for all command items of the given topic.

    Parameters
    ----------
    topic: `lsst.ts.hvac.enums.HvacTopic`
        The topic to get random values for.

    Returns
    -------
    data: `dict`
        A dictionary of command items and random values.

    """
    data: dict[str, float] = {}
    # Retrieve the config items of the topic.
    xml = MqttInfoReader()
    mqtt_topics_and_items = xml.get_command_mqtt_topics_and_items()
    items = mqtt_topics_and_items[topic.value]
    # Collect random data based on the limits of each item
    for item in items:
        if item not in [
            "COMANDO_ENCENDIDO_LSST",
        ]:
            data_item = CommandItem(item)
            idl_type = items[item]["idl_type"]
            limits = items[item]["limits"]
            if idl_type == "float":
                data[data_item.name] = (
                    random.randint(10 * limits[0], 10 * limits[1]) / 10.0
                )
            else:
                raise Exception(
                    f"Encountered IDL type {idl_type!r} for {topic.value}/{item}"
                )
    return data
