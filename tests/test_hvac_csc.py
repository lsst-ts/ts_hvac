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

import enum
import math
import random
import re
import typing
import unittest

import hvac_test_utils
from lsst.ts import hvac, salobj
from lsst.ts.hvac.enums import (
    DEVICE_GROUPS_ENGLISH,
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITHOUT_COMANDO_ENCENDIDO_ENGLISH,
    TOPICS_WITHOUT_CONFIGURATION,
    TOPICS_WITHOUT_ESTADO_FUNCIONAMIENTO,
    HvacTopicEnglish,
)
from lsst.ts.hvac.utils import to_camel_case
from lsst.ts.xml.component_info import ComponentInfo
from lsst.ts.xml.enums.HVAC import DeviceId

STD_TIMEOUT = 2  # standard command timeout (sec)

# These topics don't report whether they are switched on or not.
TOPICS_NOT_REPORT_SWITCHED_ON = frozenset(("generalP01", "dynaleneP05"))


class CscTestCase(salobj.BaseCscTestCase, unittest.IsolatedAsyncioTestCase):
    def basic_make_csc(
        self,
        initial_state: salobj.State,
        config_dir: str,
        simulation_mode: int,
        **kwargs: typing.Any,
    ) -> None:
        return hvac.HvacCsc(
            initial_state=initial_state,
            simulation_mode=simulation_mode,
            start_telemetry_publishing=False,
        )

    async def test_standard_state_transitions(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await self.check_standard_state_transitions(
                enabled_commands=(),
                skip_commands=(
                    "configChiller",
                    "configCrac",
                    "configFancoil",
                    "configFan",
                    "configLowerAhu",
                    "configAhu",
                    "disableDevice",
                    "enableDevice",
                    "dynCH1PressRemoteSP",
                    "dynCH2PressRemoteSP",
                    "dynSystOnOff",
                    "dynTaRemoteSP",
                    "dynTmaRemoteSP",
                    "dynExtAirRemoteSP",
                    "dynPierFansOnOff",
                    "dynTelemetryEnable",
                ),
            )

    async def test_version(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await self.assert_next_sample(
                self.remote.evt_softwareVersions,
                cscVersion=hvac.__version__,
                subsystemVersions="",
            )

    async def test_bin_script(self) -> None:
        await self.check_bin_script(name="HVAC", index=None, exe_name="run_hvac")

    async def _verify_evt_deviceEnabled(self, subsystem: int) -> None:
        await self.assert_next_sample(topic=self.remote.evt_deviceEnabled)

    async def _retrieve_all_telemetry(self) -> dict[str, typing.Any]:
        all_telemetry: dict[str, typing.Any] = {}

        for topic in HvacTopicEnglish:  # type: ignore
            telemetry_topic = getattr(self.remote, "tel_" + topic.name)
            all_telemetry[topic.name] = await telemetry_topic.next(flush=False)
        return all_telemetry

    async def _verify_telemetry(self, subsystem: str) -> None:
        # Loop over all telemetry topics and verify the status
        all_telemetry = await self._retrieve_all_telemetry()

        comando_encendido = hvac.TelemetryItemEnglish.switchedOn.name
        valve_name = "valveP01"
        valve_state = "valve12State"
        working_state = hvac.TelemetryItemEnglish.workingState.name

        for name, telemetry in all_telemetry.items():
            topic_value = HvacTopicEnglish[name].value
            if name in TOPICS_NOT_REPORT_SWITCHED_ON:
                continue
            if topic_value in TOPICS_ALWAYS_ENABLED or name == subsystem:
                # This is the one subsystem we have enabled.
                status_to_check = True
            else:
                # The other systems should be disabled.
                status_to_check = False
            if name == valve_name:
                attr = getattr(telemetry, valve_state)
                self.assertEqual(attr, status_to_check)
            elif name == "glycolSensor":
                # No status to check.
                pass
            elif name in TOPICS_WITHOUT_ESTADO_FUNCIONAMIENTO:
                # No status to check.
                pass
            elif name not in TOPICS_WITHOUT_COMANDO_ENCENDIDO_ENGLISH:
                item = getattr(telemetry, comando_encendido)
                self.assertEqual(item, status_to_check)
            else:
                item = getattr(telemetry, working_state)
                self.assertEqual(item, status_to_check)

    async def test_enable_on_all_subsystems_one_by_one(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )
            for topic in HvacTopicEnglish:  # type: ignore
                if topic.value not in TOPICS_ALWAYS_ENABLED:
                    # Retrieve the DeviceId.
                    device_id = DeviceId[topic.name]
                    data = {"device_id": device_id}
                    # Enable the subsystem.
                    await self.remote.cmd_enableDevice.set_start(
                        **data, timeout=STD_TIMEOUT
                    )
                    # Make sure that the SimClient publishes telemetry.
                    self.csc.mqtt_client.publish_telemetry()
                    # Make sure that the CSC publishes the telemetry.
                    await self.csc.publish_telemetry()
                    # Check deviceEnabled event.
                    await self._verify_evt_deviceEnabled(topic.name)
                    # Check all telemetry.
                    await self._verify_telemetry(topic.name)
                    # Check all events.
                    event = getattr(self.remote, "evt_" + topic.name, None)
                    if event:
                        await event.next(flush=False, timeout=STD_TIMEOUT)

                    # Disable the subsystem.
                    await self.remote.cmd_disableDevice.set_start(
                        **data, timeout=STD_TIMEOUT
                    )

    async def _verify_config_telemetry(
        self, subsystem: str, config_data: dict[str, float]
    ) -> None:
        # Loop over all telemetry topics and verify the status
        all_telemetry = await self._retrieve_all_telemetry()

        comando_encendido = hvac.TelemetryItemEnglish.switchedOn.name
        valve_name = "valveP01"
        attr_name = "valve12State"
        topic_enum: enum.EnumType = HvacTopicEnglish
        working_state = hvac.TelemetryItemEnglish.workingState.name

        for name, telemetry in all_telemetry.items():
            topic = topic_enum[name]  # type: ignore
            if name in TOPICS_NOT_REPORT_SWITCHED_ON:
                continue
            if topic.value in TOPICS_ALWAYS_ENABLED or name == subsystem:
                # This is the one subsystem we have enabled.
                status_to_check = True
            else:
                # The other systems should be disabled.
                status_to_check = False
            if name == valve_name:
                attr = getattr(telemetry, attr_name)
                self.assertEqual(attr, status_to_check)
            elif name == "glycolSensor":
                # No status to check.
                pass
            elif name in TOPICS_WITHOUT_ESTADO_FUNCIONAMIENTO:
                # No status to check.
                pass
            elif name not in TOPICS_WITHOUT_COMANDO_ENCENDIDO_ENGLISH:
                item = getattr(telemetry, comando_encendido)
                self.assertEqual(item, status_to_check)
            else:
                item = getattr(telemetry, working_state)
                self.assertEqual(item, status_to_check)

            await self._verify_configurable_items(
                subsystem, config_data, name, telemetry
            )

    async def _verify_configurable_items(
        self,
        subsystem: str,
        config_data: dict[str, float],
        name: str,
        telemetry: typing.Any,
    ) -> None:
        # Check the configurable items and verify that the value is equal
        # to the corresponding value of the configure command.
        if name == subsystem:
            for key in config_data.keys():
                # Skip items that are not reported as telemetry.
                if key in [
                    "device_id",
                    "coolingProportionalBand",
                    "fanOperationType",
                    "heatingProportionalBand",
                    "maxSetpoint",
                    "minSetpoint",
                    "temperatureSetpoint",
                    "selectFanSpeed",
                    "frequency",
                ]:
                    continue

                telemetry_key = key
                if key == "openColdValve":
                    telemetry_key = "coldValveOpening"
                telemetry_item = getattr(telemetry, telemetry_key)
                if math.isnan(config_data[key]):
                    assert not math.isnan(telemetry_item)
                else:
                    self.assertAlmostEqual(telemetry_item, config_data[key], 3)

    async def _verify_config_event(
        self, hvac_topic: HvacTopicEnglish, config_data: dict[str, float]
    ) -> None:

        command_group = [
            k for k, v in DEVICE_GROUPS_ENGLISH.items() if hvac_topic.value in v
        ][0]
        if command_group in ["FANCOIL", "FAN"]:
            return
        command_group_coro = getattr(
            self.remote,
            f"evt_{to_camel_case(command_group, True)}Configuration",
        )
        device_id = DeviceId[hvac_topic.name]
        data = await self.assert_next_sample(
            topic=command_group_coro, device_id=device_id
        )
        command_topics = self.csc.xml.command_topics[hvac_topic.name]
        for command_topic in command_topics:
            # skip topics that are not reported
            if command_topic not in [
                "switchOn",
                "maxFanSetpoint",
                "minFanSetpoint",
            ]:
                command_item = getattr(data, command_topic)
                if math.isnan(config_data[command_topic]):
                    assert not math.isnan(command_item)
                else:
                    self.assertAlmostEqual(command_item, config_data[command_topic], 3)

    async def test_config_using_xml(self) -> None:
        """Test to prove that the command arguments in ts_xml correspond to
        what the CSC expects."""
        ci = ComponentInfo(name="HVAC", topic_subname="")
        config_commands = [
            topic for topic in ci.topics if topic.startswith("cmd_config")
        ]
        device_ids_to_use = {
            "cmd_configAhu": DeviceId.cleanRoomAHU01P05,
            "cmd_configChiller": DeviceId.chiller01P01,
            "cmd_configCrac": DeviceId.crac01P02,
            "cmd_configFancoil": DeviceId.fancoil01P02,
            "cmd_configLowerAhu": DeviceId.lowerAHU01P05,
            "cmd_configFan": DeviceId.lowerDamperFan03P04,
        }
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            simulation_mode=1,
        ):
            for config_command in config_commands:
                config_data = {"device_id": device_ids_to_use[config_command].value}
                config_method = getattr(self.remote, config_command)
                await config_method.set_start(**config_data)

    async def test_config(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )

            random_seed = 12345
            for run_count in range(2):
                random.seed(random_seed)
                for hvac_topic in HvacTopicEnglish:  # type: ignore
                    if hvac_topic.value not in TOPICS_WITHOUT_CONFIGURATION:
                        subsystem = hvac_topic.name
                        # Retrieve the DeviceId.
                        device_id = DeviceId[subsystem]
                        enable_data = {"device_id": device_id}

                        if hvac_topic.value not in TOPICS_ALWAYS_ENABLED:
                            # Enable the subsystem.
                            await self.remote.cmd_enableDevice.set_start(
                                **enable_data, timeout=STD_TIMEOUT
                            )

                        # Retrieve the config command of the subsystem.
                        command_group = re.sub(r"\d{0,2}P\d{2}$", r"", device_id.name)
                        command_group = command_group[0].upper() + command_group[1:]
                        if "AHU" in command_group:
                            command_group = command_group.replace("AHU", "Ahu")
                        if "White" in command_group or "Clean" in command_group:
                            command_group = "Ahu"
                        if (
                            "LowerDamperFan" in command_group
                            or "LoadingBayFan" in command_group
                        ):
                            command_group = "Fan"
                        config_method = getattr(
                            self.remote, f"cmd_config{command_group}"
                        )

                        # Invoke the config command.
                        config_data = hvac_test_utils.get_random_config_data(hvac_topic)
                        config_data["device_id"] = device_id
                        await config_method.set_start(**config_data)
                        # Make sure that the SimClient publishes telemetry.
                        self.csc.mqtt_client.publish_telemetry()
                        # Make sure that the CSC publishes the telemetry.
                        await self.csc.publish_telemetry()
                        if hvac_topic.value not in TOPICS_ALWAYS_ENABLED:
                            # Check deviceEnabled event.
                            await self._verify_evt_deviceEnabled(subsystem)
                        # Check all configuration telemetry.
                        await self._verify_config_telemetry(subsystem, config_data)
                        # Check the config event.
                        if run_count == 0:
                            await self._verify_config_event(hvac_topic, config_data)

                        if hvac_topic.value not in TOPICS_ALWAYS_ENABLED:
                            # Disable the subsystem.
                            await self.remote.cmd_disableDevice.set_start(
                                **enable_data, timeout=STD_TIMEOUT
                            )

    async def test_dynalene_set_chiller1_pressure_setpoint(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )
            value = 5.0
            await self.remote.cmd_dynCH1PressRemoteSP.set_start(
                dynCH1PressRemoteSP=value, timeout=STD_TIMEOUT
            )
            evt = await self.remote.evt_dynCH1PressRemoteSP.next(flush=False)
            assert math.isclose(evt.dynCH1PressRemoteSP, value)

    async def test_config_with_nan(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )

            # Only consider one HVAC device here and assume this also works
            # for all other devices that can be configured.
            hvac_topic = HvacTopicEnglish("LSST/PISO05/MANEJADORA/LOWER_01")
            subsystem = hvac_topic.name

            # Retrieve the DeviceId.
            device_id = DeviceId[subsystem]
            enable_data = {"device_id": device_id}
            # Enable the subsystem.
            await self.remote.cmd_enableDevice.set_start(
                **enable_data, timeout=STD_TIMEOUT
            )

            command_group = "LowerAhu"
            config_method = getattr(self.remote, f"cmd_config{command_group}")

            config_data = hvac_test_utils.get_random_config_data(hvac_topic)
            config_data["device_id"] = device_id

            config_data["maxFanSetpoint"] = math.nan
            config_data["minFanSetpoint"] = math.nan
            config_data["antiFreezeTemperature"] = math.nan

            # Invoke the config command.
            await config_method.set_start(**config_data)

            # Make sure that the SimClient publishes telemetry.
            self.csc.mqtt_client.publish_telemetry()
            # Make sure that the CSC publishes the telemetry.
            await self.csc.publish_telemetry()
            # Check deviceEnabled event.
            await self._verify_evt_deviceEnabled(subsystem)
            # Check all configuration telemetry.
            await self._verify_config_telemetry(subsystem, config_data)
            # Check the config event.
            await self._verify_config_event(hvac_topic, config_data)

            # Disable the subsystem.
            await self.remote.cmd_disableDevice.set_start(
                **enable_data, timeout=STD_TIMEOUT
            )
