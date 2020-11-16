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

import asynctest
import json
import logging

import flake8

import lsst.ts.hvac.simulator.sim_client as sim_client
from lsst.ts.hvac.xml import hvac_mqtt_to_SAL_XML as xml

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)

# Make sure that flake8 log level is set to logging.INFO
flake8.configure_logging(1)


class SimClientTestCase(asynctest.TestCase):
    async def setUp(self):
        """Setup the unit test.
        """
        self.log = logging.getLogger("SimClientTestCase")
        # Make sure that all topics and their variables are loaded.
        xml.collect_topics_and_items()
        self.hvac_topics = xml.hvac_topics

        # Set up the simulator client.
        self.mqtt_client = sim_client.SimClient(
            start_publish_telemetry_every_second=False
        )
        # Call connect to make sure that the MQTT client is in the correct
        # state for the test.
        await self.mqtt_client.connect()

    async def tearDown(self):
        """Cleanup after the unit test.
        """
        if self.mqtt_client:
            await self.mqtt_client.disconnect()

    def collect_mqtt_state(self):
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
        mqtt_state = {}
        # Next the MQTT messages containing the published values for all topics
        # need to be collected.
        msgs = self.mqtt_client.msgs
        # Finally loop over the messages to fetch the published values of each
        # topic and collect them per topic.
        while not len(msgs) == 0:
            msg = msgs.popleft()
            topic = msg.topic
            payload = msg.payload
            topic, variable = xml.extract_topic_and_item(topic)
            data = json.loads(payload)
            if topic not in mqtt_state:
                mqtt_state[topic] = {}
            mqtt_state[topic][variable] = data
        return mqtt_state

    def verify_topic_disabled(self, topic):
        """Verifies that the provided topic is disabled by verifying that
        it doesn't publish any values.

        Parameters
        ----------
        topic: `str`
            The name of the topic.
        """
        mqtt_state = self.collect_mqtt_state()
        self.assertFalse(topic in mqtt_state)

    def verify_topic_state(self, topic, expected_state):
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
            if isinstance(var, bool):
                self.assertEqual(mqtt_state[topic][var], expected_state[var])
            elif isinstance(var, dict):
                self.assertGreaterEqual(
                    mqtt_state[topic][var], expected_state[var]["min"]
                )
                self.assertLessEqual(mqtt_state[topic][var], expected_state[var]["max"])

    def enable_topic(self, topic):
        """Enable the topic by sending True to the enable command.
        """
        command = topic + "/" + "COMANDO_ENCENDIDO_LSST"
        value = "true"
        self.mqtt_client.publish_mqtt_message(command, value)

    def disable_topic(self, topic):
        """Disable the topic by sending False to the enable command.
        """
        command = topic + "/" + "COMANDO_ENCENDIDO_LSST"
        value = "false"
        self.mqtt_client.publish_mqtt_message(command, value)

    def determine_expected_state(self, topic):
        """Determine the expected state of the topic by looping over each
        variable of the topic and setting an expected value.

        The expected values either is set to False (in case of a boolean) or to
        a dictionary containing a min and a max value (in case of a float). If
        any other idl_type is encountered the unit test fails.
        The ranges of the min and max values depend on the unit and the limits
        of the variable.

        Parameters
        ----------
        topic: `str`
            The topic to determine the expected state for.

        Returns
        -------
        expected_state: `dict`
            The expected state.

        """
        variables = xml.get_items_for_topic(topic)
        expected_state = {}
        for variable in variables:
            var = variables[variable]
            if var["topic_type"] == "READ":
                if var["idl_type"] == "boolean":
                    expected_state[variable] = False
                elif var["idl_type"] == "float":
                    lower_limit, upper_limit = var["limits"]
                    if var["unit"] in ["deg_C", "unitless", "bar", "%"]:
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

    async def test_topics(self):
        """Loop over all topics and perform the following operations for
        each topic:

            * Verify that the topic is disabled if not always enabled.
            * Enable the topic if not always enabled.
            * Verify that the topic publishes values that correspond to the
            expected range for each value.
            * Disable the topic if not always enabled.
            * Verify that the topic is disabled if not always enabled.

        """
        topics = xml.get_topics()
        for topic in topics:
            expected_state = self.determine_expected_state(topic)
            if topic not in xml.TOPICS_ALWAYS_ENABLED:
                self.verify_topic_disabled(topic)
                self.enable_topic(topic)
            self.verify_topic_state(topic, expected_state)
            if topic not in xml.TOPICS_ALWAYS_ENABLED:
                self.disable_topic(topic)
                self.verify_topic_disabled(topic)
