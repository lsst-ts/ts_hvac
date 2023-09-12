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

import logging
import re
import typing
import unittest

import hvac_test_utils
from lsst.ts import hvac, salobj
from lsst.ts.hvac.enums import (
    DEVICE_GROUPS,
    TOPICS_ALWAYS_ENABLED,
    TOPICS_WITHOUT_CONFIGURATION,
    HvacTopic,
)
from lsst.ts.hvac.utils import to_camel_case
from lsst.ts.idl.enums.HVAC import DeviceId

STD_TIMEOUT = 2  # standard command timeout (sec)

# These topics don't report whether they are switched on or not.
TOPICS_NOT_REPORT_SWITCHED_ON = frozenset(("generalP01", "dynaleneP05"))

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)


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
                    "configChillers",
                    "configCracks",
                    "configFancoils",
                    "configManejadoraLowers",
                    "configManejadoras",
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
        # Default mask indicating that the three devices that always are
        # enabled, are enabled.
        device_mask = 0b1111
        device_id = DeviceId[subsystem]
        deviceId_index = self.csc.device_id_index[device_id]
        device_mask += 2**deviceId_index
        await self.assert_next_sample(
            topic=self.remote.evt_deviceEnabled, device_ids=device_mask
        )

    async def _retrieve_all_telemetry(self) -> dict[str, typing.Any]:
        all_telemetry: dict[str, typing.Any] = {}
        for topic in HvacTopic:
            telemetry_topic = getattr(self.remote, "tel_" + topic.name)
            all_telemetry[topic.name] = await telemetry_topic.next(flush=False)
        return all_telemetry

    async def _verify_telemetry(self, subsystem: str) -> None:
        # Loop over all telemetry topics and verify the status
        all_telemetry = await self._retrieve_all_telemetry()
        for name, telemetry in all_telemetry.items():
            topic = HvacTopic[name]
            if name in TOPICS_NOT_REPORT_SWITCHED_ON:
                continue
            if topic.value in TOPICS_ALWAYS_ENABLED or name == subsystem:
                # This is the one subsystem we have enabled.
                status_to_check = True
            else:
                # The other systems should be disabled.
                status_to_check = False
            if name == "valvulaP01":
                self.assertEqual(telemetry.estadoValvula12, status_to_check)
            elif name not in hvac.TOPICS_WITHOUT_COMANDO_ENCENDIDO:
                self.assertEqual(telemetry.comandoEncendido, status_to_check)
            else:
                self.assertEqual(telemetry.estadoFuncionamiento, status_to_check)

    async def _verify_event(self, subsystem: HvacTopic) -> None:
        """Verify that an event has been sent for the specified HvacTopic.

        No validation of the data in the event is done. If no event has been
        emitted, this will timeout and it shouldn't for those subsystems for
        which HVAC events exist.
        """
        event = getattr(self.remote, "evt_" + subsystem.name, None)
        if event:
            await event.next(flush=False, timeout=STD_TIMEOUT)

    async def test_enable_on_all_subsystems_one_by_one(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )
            for topic in HvacTopic:
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
                    await self._verify_event(topic)

                    # Disable the subsystem.
                    await self.remote.cmd_disableDevice.set_start(
                        **data, timeout=STD_TIMEOUT
                    )

    async def _verify_config_telemetry(
        self, subsystem: str, config_data: dict[str, float]
    ) -> None:
        # Loop over all telemetry topics and verify the status
        all_telemetry = await self._retrieve_all_telemetry()
        for name, telemetry in all_telemetry.items():
            topic = HvacTopic[name]
            if name in TOPICS_NOT_REPORT_SWITCHED_ON:
                continue
            if topic.value in TOPICS_ALWAYS_ENABLED or name == subsystem:
                # This is the one subsystem we have enabled.
                status_to_check = True
            else:
                # The other systems should be disabled.
                status_to_check = False
            if name == "valvulaP01":
                self.assertEqual(telemetry.estadoValvula12, status_to_check)
            elif name not in hvac.TOPICS_WITHOUT_COMANDO_ENCENDIDO:
                self.assertEqual(telemetry.comandoEncendido, status_to_check)
            else:
                self.assertEqual(telemetry.estadoFuncionamiento, status_to_check)

            # Check the configurable items and verify that the value is equal
            # to the corresponding value of the configure command.
            if name == subsystem:
                for key in config_data.keys():
                    # TODO: These command items do not have a telemetry counter
                    #  point in the "Lower" components. It is being clarified
                    #  how to verify them so they are skipped for now.
                    if "Lower" in name and "setpointVentilador" in key:
                        continue
                    if key == "device_id":
                        continue
                    telemetry_item = getattr(telemetry, key)
                    self.assertAlmostEqual(telemetry_item, config_data[key], 3)

    async def _verify_config_event(
        self, hvac_topic: HvacTopic, config_data: dict[str, float]
    ) -> None:
        command_group = [k for k, v in DEVICE_GROUPS.items() if hvac_topic.value in v][
            0
        ]
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
                "comandoEncendido",
                "setpointVentiladorMax",
                "setpointVentiladorMin",
            ]:
                command_item = getattr(data, command_topic)
                self.assertAlmostEqual(command_item, config_data[command_topic], 3)

    async def test_config(self) -> None:
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )

            for hvac_topic in HvacTopic:
                if hvac_topic.value not in TOPICS_WITHOUT_CONFIGURATION:
                    subsystem = hvac_topic.name
                    # Retrieve the DeviceId.
                    device_id = DeviceId[subsystem]
                    enable_data = {"device_id": device_id}
                    # Enable the subsystem.
                    await self.remote.cmd_enableDevice.set_start(
                        **enable_data, timeout=STD_TIMEOUT
                    )
                    # Retrieve the config command of the subsystem.
                    command_group = re.sub(r"\d{0,2}P\d{2}$", r"", device_id.name)
                    command_group = command_group[0].upper() + command_group[1:]
                    if "Sblanca" in command_group or "Slimpia" in command_group:
                        command_group = "Manejadora"
                    config_method = getattr(self.remote, f"cmd_config{command_group}s")
                    # Invoke the config command.
                    config_data = hvac_test_utils.get_random_config_data(hvac_topic)
                    config_data["device_id"] = device_id
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
            assert evt.dynCH1PressRemoteSP == value
