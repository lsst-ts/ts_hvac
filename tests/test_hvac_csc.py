# This file is part of ts_hvac.
#
# Developed for the LSST Data Management System.
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
import logging

from lsst.ts import salobj
from lsst.ts import hvac

STD_TIMEOUT = 2  # standard command timeout (sec)

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG)


class CscTestCase(salobj.BaseCscTestCase, asynctest.TestCase):
    def basic_make_csc(self, initial_state, config_dir, simulation_mode, **kwargs):
        return hvac.HvacCsc(
            initial_state=initial_state, config_dir=config_dir, simulation_mode=simulation_mode,
        )

    async def test_standard_state_transitions(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await self.check_standard_state_transitions(
                enabled_commands=(
                    "chiller01P01",
                    "crack01P02",
                    "fancoil01P02",
                    "manejadoraLower01P05",
                    "manejadoraSblancaP04",
                    "vea01P01",
                    "vea01P05",
                    "vea08P05",
                    "vea09P05",
                    "vea10P05",
                    "vea11P05",
                    "vea12P05",
                    "vea13P05",
                    "vea14P05",
                    "vea15P05",
                    "vea16P05",
                    "vea17P05",
                    "vec01P01",
                    "vex03P04",
                    "vex04P04",
                    "vin01P01",
                ),
            )

    async def test_bin_script(self):
        await self.check_bin_script(name="HVAC", index=None, exe_name="run_hvac.py")

    async def test_do_chiller01P01(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            setpoint_activo = 90
            comando_encendido = True
            await self.remote.cmd_chiller01P01.set_start(
                setpointActivo=setpoint_activo, comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_crack01P02(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            setpoint_humidificador = 90
            setpoint_deshumidificador = 90
            set_point_cooling = 90
            set_point_heating = 90
            comando_encendido = True
            await self.remote.cmd_crack01P02.set_start(
                setpointHumidificador=setpoint_humidificador,
                setpointDeshumidificador=setpoint_deshumidificador,
                setPointCooling=set_point_cooling,
                setPointHeating=set_point_heating,
                comandoEncendido=comando_encendido,
                timeout=STD_TIMEOUT,
            )

    async def test_do_fancoil01P02(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            perc_apertura_valvula_frio = 90
            setpoint_cooling_day = 80
            setpoint_heating_day = 70
            setpoint_cooling_night = 60
            setpoint_heating_night = 50
            setpoint_trabajo = 40
            comando_encendido = True
            await self.remote.cmd_fancoil01P02.set_start(
                percAperturaValvulaFrio=perc_apertura_valvula_frio,
                setpointCoolingDay=setpoint_cooling_day,
                setpointHeatingDay=setpoint_heating_day,
                setpointCoolingNight=setpoint_cooling_night,
                setpointHeatingNight=setpoint_heating_night,
                setpointTrabajo=setpoint_trabajo,
                comandoEncendido=comando_encendido,
                timeout=STD_TIMEOUT,
            )

    async def test_do_manejadoraLower01P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            setpoint_trabajo = 90
            setpoint_ventilador_min = 89
            setpoint_ventilador_max = 88
            temperatura_anticongelante = 87
            comando_encendido = True
            await self.remote.cmd_manejadoraLower01P05.set_start(
                setpointTrabajo=setpoint_trabajo,
                setpointVentiladorMin=setpoint_ventilador_min,
                setpointVentiladorMax=setpoint_ventilador_max,
                temperaturaAnticongelante=temperatura_anticongelante,
                comandoEncendido=comando_encendido,
                timeout=STD_TIMEOUT,
            )

    async def test_do_manejadoraSblancaP04(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            valor_consigna = 90
            setpoint_ventilador_min = 30
            setpoint_ventilador_max = 60
            comando_encendido = True
            await self.remote.cmd_manejadoraSblancaP04.set_start(
                valorConsigna=valor_consigna,
                setpointVentiladorMin=setpoint_ventilador_min,
                setpointVentiladorMax=setpoint_ventilador_max,
                comandoEncendido=comando_encendido,
                timeout=STD_TIMEOUT,
            )

    async def test_do_vea01P01(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea01P01.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea01P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea01P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea08P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea08P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea09P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea09P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea10P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea10P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea11P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea11P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea12P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea12P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea13P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea13P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea14P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea14P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea15P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea15P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea16P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea16P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vea17P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vea17P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vec01P01(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vec01P01.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vex03P04(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vex03P04.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vex04P04(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vex04P04.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

    async def test_do_vin01P01(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)
            comando_encendido = True
            await self.remote.cmd_vin01P01.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
