# This file is part of ts_hvac.
#
# Developed for the Vera Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the Vera Rubin Observatory
# Project (https://www.lsst.org).
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
import logging

import flake8

from lsst.ts import salobj
from lsst.ts.hvac import HvacCsc, TOPICS_WITHOUT_COMANDO_ENCENDIDO
from lsst.ts.hvac.hvac_enums import HvacTopic
from lsst.ts.hvac.xml import hvac_mqtt_to_SAL_XML as xml
import utils

STD_TIMEOUT = 2  # standard command timeout (sec)

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)

# Make sure that flake8 log level is set to logging.INFO
flake8.configure_logging(1)


class CscTestCase(salobj.BaseCscTestCase, asynctest.TestCase):
    def basic_make_csc(self, initial_state, config_dir, simulation_mode, **kwargs):
        return HvacCsc(
            initial_state=initial_state,
            config_dir=config_dir,
            simulation_mode=simulation_mode,
            start_telemetry_publishing=False,
        )

    async def test_standard_state_transitions(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1,
        ):
            await self.check_standard_state_transitions(
                enabled_commands=(),
                skip_commands=(
                    "chiller01P01_enable",
                    "crack01P02_enable",
                    "chiller02P01_enable",
                    "chiller03P01_enable",
                    "crack02P02_enable",
                    "fancoil01P02_enable",
                    "fancoil02P02_enable",
                    "fancoil03P02_enable",
                    "fancoil04P02_enable",
                    "fancoil05P02_enable",
                    "fancoil06P02_enable",
                    "fancoil07P02_enable",
                    "fancoil08P02_enable",
                    "fancoil09P02_enable",
                    "fancoil10P02_enable",
                    "fancoil11P02_enable",
                    "fancoil12P02_enable",
                    "manejadoraLower01P05_enable",
                    "manejadoraLower02P05_enable",
                    "manejadoraLower03P05_enable",
                    "manejadoraLower04P05_enable",
                    "manejadoraSblancaP04_enable",
                    "manejadoraSlimpiaP04_enable",
                    "vea01P01_enable",
                    "vea01P05_enable",
                    "vea08P05_enable",
                    "vea09P05_enable",
                    "vea10P05_enable",
                    "vea11P05_enable",
                    "vea12P05_enable",
                    "vea13P05_enable",
                    "vea14P05_enable",
                    "vea15P05_enable",
                    "vea16P05_enable",
                    "vea17P05_enable",
                    "vec01P01_enable",
                    "vex03LowerP04_enable",
                    "vex04CargaP04_enable",
                    "vin01P01_enable",
                    "chiller01P01_config",
                    "chiller02P01_config",
                    "chiller03P01_config",
                    "crack01P02_config",
                    "crack02P02_config",
                    "fancoil01P02_config",
                    "fancoil02P02_config",
                    "fancoil03P02_config",
                    "fancoil04P02_config",
                    "fancoil05P02_config",
                    "fancoil06P02_config",
                    "fancoil07P02_config",
                    "fancoil08P02_config",
                    "fancoil09P02_config",
                    "fancoil10P02_config",
                    "fancoil11P02_config",
                    "fancoil12P02_config",
                    "manejadoraLower01P05_config",
                    "manejadoraLower02P05_config",
                    "manejadoraLower03P05_config",
                    "manejadoraLower04P05_config",
                    "manejadoraSblancaP04_config",
                    "manejadoraSlimpiaP04_config",
                ),
            )

    async def test_bin_script(self):
        await self.check_bin_script(name="HVAC", index=None, exe_name="run_hvac.py")

    async def _retrieve_all_telemetry(self):
        all_telemetry = {}
        for topic in HvacTopic:
            telemetry_topic = getattr(self.remote, "tel_" + topic.name)
            all_telemetry[topic.name] = await telemetry_topic.next(flush=False)
        return all_telemetry

    async def _verify_telemetry(self, subsystem):
        # Loop over all telemetry topics and verify the status
        all_telemetry = await self._retrieve_all_telemetry()
        for name, telemetry in all_telemetry.items():
            topic = HvacTopic[name]
            # This topic only publishes a temperature so we skip it here.
            if name == "generalP01":
                continue
            if topic.value in xml.TOPICS_ALWAYS_ENABLED or name == subsystem:
                # This is the one subsystem we have enabled.
                status_to_check = True
            else:
                # The other systems should be disabled.
                status_to_check = False
            if name == "valvulaP01":
                self.assertEqual(telemetry.estadoValvula12, status_to_check)
            elif name not in TOPICS_WITHOUT_COMANDO_ENCENDIDO:
                self.assertEqual(telemetry.comandoEncendido, status_to_check)
            else:
                self.assertEqual(telemetry.estadoFuncionamiento, status_to_check)

    async def test_enable_on_all_subsystems_one_by_one(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )
            for topic in HvacTopic:
                if topic.value not in xml.TOPICS_ALWAYS_ENABLED:
                    subsystem = topic.name
                    # Retrieve the method to enable or disable a subsystem.
                    enable_method = getattr(self.remote, "cmd_" + subsystem + "_enable")
                    # Enable the subsystem.
                    await enable_method.set_start(
                        comandoEncendido=True, timeout=STD_TIMEOUT
                    )
                    # Make sure that the SimClient publishes telemetry.
                    self.csc.mqtt_client.publish_telemetry()
                    # Make sure that the CSC publishes the telemetry.
                    self.csc.publish_telemetry()
                    # Check all telemetry.
                    await self._verify_telemetry(subsystem)

                    # Disable the subsystem.
                    await enable_method.set_start(
                        comandoEncendido=False, timeout=STD_TIMEOUT
                    )

    async def _verify_config_telemetry(self, subsystem, data):
        # Loop over all telemetry topics and verify the status
        all_telemetry = await self._retrieve_all_telemetry()
        for name, telemetry in all_telemetry.items():
            topic = HvacTopic[name]
            # This topic only publishes a temperature so we skip it here.
            if name == "generalP01":
                continue
            if topic.value in xml.TOPICS_ALWAYS_ENABLED or name == subsystem:
                # This is the one subsystem we have enabled.
                status_to_check = True
            else:
                # The other systems should be disabled.
                status_to_check = False
            if name == "valvulaP01":
                self.assertEqual(telemetry.estadoValvula12, status_to_check)
            elif name not in TOPICS_WITHOUT_COMANDO_ENCENDIDO:
                self.assertEqual(telemetry.comandoEncendido, status_to_check)
            else:
                self.assertEqual(telemetry.estadoFuncionamiento, status_to_check)

            # Check the configurable items and verify that the value is equal
            # to the corresponding value of the configure command.
            if name == subsystem:
                for key in data.keys():
                    # TODO: These command items do not have a telemetry counter
                    #  point in the "Lower" components. It is being clarified
                    #  how to verify them so they are skipped for now.
                    if "Lower" in name and "setpointVentilador" in key:
                        continue
                    item_name = key
                    telemetry_item = getattr(telemetry, item_name)
                    self.assertAlmostEqual(telemetry_item, data[key], 5)

    async def test_config(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1,
        ):
            await salobj.set_summary_state(
                remote=self.remote, state=salobj.State.ENABLED
            )
            for topic in HvacTopic:
                if topic.value not in xml.TOPICS_WITHOUT_CONFIGURATION:
                    data = utils.get_random_config_data(topic)
                    subsystem = topic.name
                    # Retrieve the method to enable or disable a subsystem.
                    enable_method = getattr(self.remote, "cmd_" + subsystem + "_enable")
                    # Enable the subsystem.
                    await enable_method.set_start(
                        comandoEncendido=True, timeout=STD_TIMEOUT
                    )
                    # Retrieve the config command of the subsystem.
                    config_method = getattr(self.remote, "cmd_" + subsystem + "_config")
                    # Invoke the config command.
                    await config_method.set_start(**data)
                    # Make sure that the SimClient publishes telemetry.
                    self.csc.mqtt_client.publish_telemetry()
                    # Make sure that the CSC publishes the telemetry.
                    self.csc.publish_telemetry()
                    # Check all configuration telemetry.
                    await self._verify_config_telemetry(subsystem, data)
                    # Disable the subsystem.
                    await enable_method.set_start(
                        comandoEncendido=False, timeout=STD_TIMEOUT
                    )
