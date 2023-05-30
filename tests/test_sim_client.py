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

import json
import logging
import typing
import unittest

import hvac_test_utils
import lsst.ts.hvac.simulator.sim_client as sim_client
from lsst.ts.hvac.enums import (
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITHOUT_CONFIGURATION,
    CommandItem,
    HvacTopic,
)
from lsst.ts.hvac.mqtt_info_reader import MqttInfoReader

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)

expected_units = frozenset(
    ("deg_C", "unitless", "bar", "%", "h", "m3/h", "l/min", "Pa", "kW")
)


class SimClientTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        """Setup the unit test."""
        self.log = logging.getLogger("SimClientTestCase")
        # Make sure that all topics and their variables are loaded.
        self.xml = MqttInfoReader()
        self.hvac_topics = self.xml.hvac_topics

        # Set up the simulator client.
        self.mqtt_client = sim_client.SimClient(
            start_publish_telemetry_every_second=False
        )
        # Call connect to make sure that the MQTT client is in the correct
        # state for the test.
        await self.mqtt_client.connect()

    async def asyncTearDown(self) -> None:
        """Cleanup after the unit test."""
        if self.mqtt_client:
            await self.mqtt_client.disconnect()

    def collect_mqtt_state(self) -> dict[str, typing.Any]:
        """Convenience method to collect all MQTT topics and their values.

        The structure of the produced dictionary is

            topic1: {
                param1: value1,
                param2: value2,
                ...
            }
            topic2: {
                paramA: valueA,
                paramB: valueB,
                ...
            }
            ...

        Returns
        -------
        mqtt_state: `dict`
            A dict containing the state of each enabled topic.

        """
        # This method needs to be called first to ensure that all MQTT topics
        # publish their values.
        self.mqtt_client.publish_telemetry()
        mqtt_state: dict[str, typing.Any] = {}
        # Next the MQTT messages containing the published values for all topics
        # need to be collected.
        msgs = self.mqtt_client.msgs
        # Finally loop over the messages to fetch the published values of each
        # topic and collect them per topic.
        while not len(msgs) == 0:
            msg = msgs.popleft()
            topic = msg.topic
            data = json.loads(msg.payload)
            topic, variable = self.xml.extract_topic_and_item(topic)
            if topic not in mqtt_state:
                mqtt_state[topic] = {}
            mqtt_state[topic][variable] = data
        return mqtt_state

    def verify_topic_disabled(self, topic: str) -> None:
        """Verifies that the provided topic is disabled by verifying that
        it doesn't publish any values.

        Parameters
        ----------
        topic: `str`
            The name of the topic.
        """
        mqtt_state = self.collect_mqtt_state()
        self.assertTrue(topic in mqtt_state)
        variables = mqtt_state[topic]
        for var in variables:
            data = mqtt_state[topic][var]
            if isinstance(data, bool):
                self.assertFalse(data)
            else:
                self.fail(
                    f"Encountered variable {var} with value {data} in topic {topic}"
                )

    def verify_topic_state(
        self, topic: str, expected_state: dict[str, typing.Any]
    ) -> None:
        """Verifies that the state as reported by the topic is as expected.

        For a description of the expected state dict, see the
        `determine_expected_state` method in this class.

        Parameters
        ----------
        topic: `str`
            The name of the topic.
        expected_state: `dict`
            The expected state of the topic.
        """
        mqtt_state = self.collect_mqtt_state()
        self.assertTrue(topic in mqtt_state)
        variables = mqtt_state[topic]
        for var in variables:
            data = mqtt_state[topic][var]
            expected_data = expected_state[var]
            if isinstance(expected_data, bool):
                self.assertEqual(
                    data,
                    expected_data,
                    f"topic = {topic}, var = {var}, data={data}",
                )
            elif isinstance(expected_data, dict):
                self.assertGreaterEqual(data, expected_data["min"])
                self.assertLessEqual(data, expected_data["max"])
            else:
                self.fail(
                    f"Encountered variable {var} of type {type(data)} with value {data} in topic {topic}"
                )

    def enable_topic(self, topic: str) -> None:
        """Enable the topic by sending True to the enable command.

        Parameters
        ----------
        topic: `str`
            The topic.
        """
        command = topic + "/" + "COMANDO_ENCENDIDO_LSST"
        value = "true"
        self.mqtt_client.publish_mqtt_message(command, value)

    def disable_topic(self, topic: str) -> None:
        """Disable the topic by sending False to the enable command.

        Parameters
        ----------
        topic: `str`
            The topic.
        """
        command = topic + "/" + "COMANDO_ENCENDIDO_LSST"
        value = "false"
        self.mqtt_client.publish_mqtt_message(command, value)

    def determine_expected_state(self, topic: str) -> dict[str, typing.Any]:
        """Determine the expected state of the topic by looping over each
        variable of the topic and setting an expected value.

        In case of a boolean, the expected value is set to True unless the item
        is an ALARM item (the simulator doesn't simulate alarms yet). In case
        of a float, the expected value is set to a dictionary containing a min
        and a max value. The ranges of the min and max values depend on the
        unit and the limits of the variable.

        If any other idl_type is encountered the unit test fails.

        Parameters
        ----------
        topic: `str`
            The topic to determine the expected state for.

        Returns
        -------
        expected_state: `dict`
            The expected state.

        """
        variables = self.xml.get_items_for_hvac_topic(topic)
        expected_state: dict[str, typing.Any] = {}
        for variable in variables:
            var = variables[variable]
            if var["topic_type"] == "READ":
                if var["idl_type"] == "boolean":
                    expected_state[variable] = True
                    if "ALARM" in variable or (
                        variable.startswith("dyn")
                        and (
                            variable.endswith("ON")
                            or variable.endswith("Warning")
                            or variable.endswith("LevelAlarm")
                        )
                    ):
                        expected_state[variable] = False
                elif var["idl_type"] == "float":
                    lower_limit, upper_limit = var["limits"]
                    if var["unit"] in expected_units:
                        expected_state[variable] = {
                            "min": lower_limit,
                            "max": upper_limit,
                        }
                    else:
                        self.fail(
                            f"Found unexpected unit {var['unit']} for variable {variable}"
                        )
                else:
                    self.fail(
                        f"Found unexpected idl_type {var['idl_type']} for variable {variable}"
                    )
        return expected_state

    async def test_topics(self) -> None:
        """Loop over all topics and perform the following operations for
        each topic:

            * Verify that the topic is disabled if not always enabled.
            * Enable the topic if not always enabled.
            * Verify that the topic publishes values that correspond to the
            expected range for each value.
            * Disable the topic if not always enabled.
            * Verify that the topic is disabled if not always enabled.

        """
        topics = self.xml.get_generic_hvac_topics()
        for topic in topics:
            if topic not in TOPICS_ALWAYS_ENABLED:
                self.verify_topic_disabled(topic)
                self.enable_topic(topic)

            expected_state = self.determine_expected_state(topic)
            self.verify_topic_state(topic, expected_state)

            if topic not in TOPICS_ALWAYS_ENABLED:
                self.disable_topic(topic)
                self.verify_topic_disabled(topic)

    async def test_config(self) -> None:
        for topic in HvacTopic:
            if topic.value not in TOPICS_WITHOUT_CONFIGURATION:
                data = hvac_test_utils.get_random_config_data(topic)
                for key in data.keys():
                    command_item = CommandItem[key]
                    self.mqtt_client._handle_config_command(
                        topic.value, command_item.value, data[key]
                    )

                # enable the topic otherwise telemetry doesn't get published
                self.enable_topic(topic.value)
                mqtt_state = self.collect_mqtt_state()
                # verify that the corresponding telemetry items have the
                # values as sent in the configurastion command
                for key in data.keys():
                    command_item = CommandItem[key]
                    self.log.info(f"{topic.value}/{command_item.value[:-5]}")
                    # TODO: These command items do not have a telemetry counter
                    #  point in the "Lower" components. It is being clarified
                    #  how to verify them so they are skipped for now.
                    if command_item.value in [
                        "SETPOINT_VENTILADOR_MIN_LSST",
                        "SETPOINT_VENTILADOR_MAX_LSST",
                    ] and topic.value.startswith("LSST/PISO05/MANEJADORA/LOWER"):
                        continue
                    self.assertEqual(
                        data[key], mqtt_state[topic.value][command_item.value[:-5]]
                    )

                self.log.info(mqtt_state)
                # disable the topic again
                self.disable_topic(topic.value)
