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

            tel_chiller01P01 = await self.assert_next_sample(topic=self.remote.tel_chiller01P01, flush=True,)
            self.assertTrue(tel_chiller01P01.compresor01Funcionando is False)
            self.assertTrue(tel_chiller01P01.compresor02Funcionando is False)
            self.assertTrue(tel_chiller01P01.compresor03Funcionando is False)
            self.assertTrue(tel_chiller01P01.compresor04Funcionando is False)
            self.assertTrue(tel_chiller01P01.comandoEncendido is False)
            self.assertAlmostEqual(-99.99, tel_chiller01P01.setpointActivo, places=5)

            setpoint_activo = 90
            comando_encendido = True
            await self.remote.cmd_chiller01P01.set_start(
                setpointActivo=setpoint_activo, comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_chiller01P01 = await self.assert_next_sample(topic=self.remote.tel_chiller01P01, flush=True,)
            tel_chiller01P01 = await self.assert_next_sample(topic=self.remote.tel_chiller01P01, flush=True,)
            self.assertTrue(tel_chiller01P01.compresor01Funcionando == comando_encendido)
            self.assertTrue(tel_chiller01P01.compresor02Funcionando == comando_encendido)
            self.assertTrue(tel_chiller01P01.compresor03Funcionando == comando_encendido)
            self.assertTrue(tel_chiller01P01.compresor04Funcionando == comando_encendido)
            self.assertTrue(tel_chiller01P01.comandoEncendido == comando_encendido)
            self.assertAlmostEqual(setpoint_activo, tel_chiller01P01.setpointActivo)

    async def test_do_crack01P02(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_crack01P02 = await self.assert_next_sample(topic=self.remote.tel_crack01P02, flush=True,)
            self.assertTrue(tel_crack01P02.estadoFuncionamiento is False)
            self.assertTrue(tel_crack01P02.estadoPresenciaAlarma is False)
            self.assertTrue(tel_crack01P02.comandoEncendido is False)
            self.assertAlmostEqual(-99.99, tel_crack01P02.setpointHumidificador, places=5)
            self.assertAlmostEqual(-99.99, tel_crack01P02.setpointDeshumidificador, places=5)
            self.assertAlmostEqual(-99.99, tel_crack01P02.setPointCooling, places=5)
            self.assertAlmostEqual(-99.99, tel_crack01P02.setPointHeating, places=5)

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
            tel_crack01P02 = await self.assert_next_sample(topic=self.remote.tel_crack01P02, flush=True,)
            tel_crack01P02 = await self.assert_next_sample(topic=self.remote.tel_crack01P02, flush=True,)
            self.assertTrue(tel_crack01P02.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_crack01P02.estadoPresenciaAlarma is False)
            self.assertTrue(tel_crack01P02.comandoEncendido == comando_encendido)
            self.assertAlmostEqual(setpoint_humidificador, tel_crack01P02.setpointHumidificador, places=5)
            self.assertAlmostEqual(
                setpoint_deshumidificador, tel_crack01P02.setpointDeshumidificador, places=5
            )
            self.assertAlmostEqual(set_point_cooling, tel_crack01P02.setPointCooling, places=5)
            self.assertAlmostEqual(set_point_heating, tel_crack01P02.setPointHeating, places=5)

    async def test_do_fancoil01P02(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_fancoil01P02 = await self.assert_next_sample(topic=self.remote.tel_fancoil01P02, flush=True,)
            self.assertTrue(tel_fancoil01P02.temperaturaSala is False)
            self.assertTrue(tel_fancoil01P02.estadoOperacion is False)
            self.assertTrue(tel_fancoil01P02.estadoCalefactor is False)
            self.assertTrue(tel_fancoil01P02.estadoVentilador is False)
            self.assertTrue(tel_fancoil01P02.comandoEncendido is False)
            self.assertAlmostEqual(-99.99, tel_fancoil01P02.aperturaValvulaFrio, places=5)
            self.assertAlmostEqual(-99.99, tel_fancoil01P02.setpointCoolingDay, places=5)
            self.assertAlmostEqual(-99.99, tel_fancoil01P02.setpointHeatingDay, places=5)
            self.assertAlmostEqual(-99.99, tel_fancoil01P02.setpointCoolingNight, places=5)
            self.assertAlmostEqual(-99.99, tel_fancoil01P02.setpointHeatingNight, places=5)
            self.assertAlmostEqual(-99.99, tel_fancoil01P02.setpointTrabajo, places=5)

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
            tel_fancoil01P02 = await self.assert_next_sample(topic=self.remote.tel_fancoil01P02, flush=True,)
            tel_fancoil01P02 = await self.assert_next_sample(topic=self.remote.tel_fancoil01P02, flush=True,)
            self.assertTrue(tel_fancoil01P02.temperaturaSala == comando_encendido)
            self.assertTrue(tel_fancoil01P02.estadoOperacion == comando_encendido)
            self.assertTrue(tel_fancoil01P02.estadoCalefactor == comando_encendido)
            self.assertTrue(tel_fancoil01P02.estadoVentilador == comando_encendido)
            self.assertTrue(tel_fancoil01P02.comandoEncendido == comando_encendido)
            self.assertAlmostEqual(perc_apertura_valvula_frio, tel_fancoil01P02.aperturaValvulaFrio, places=5)
            self.assertAlmostEqual(setpoint_cooling_day, tel_fancoil01P02.setpointCoolingDay, places=5)
            self.assertAlmostEqual(setpoint_heating_day, tel_fancoil01P02.setpointHeatingDay, places=5)
            self.assertAlmostEqual(setpoint_cooling_night, tel_fancoil01P02.setpointCoolingNight, places=5)
            self.assertAlmostEqual(setpoint_heating_night, tel_fancoil01P02.setpointHeatingNight, places=5)
            self.assertAlmostEqual(setpoint_trabajo, tel_fancoil01P02.setpointTrabajo, places=5)

    async def test_do_manejadoraLower01P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_manejadoraLower01P05 = await self.assert_next_sample(
                topic=self.remote.tel_manejadoraLower01P05, flush=True,
            )
            self.assertTrue(tel_manejadoraLower01P05.estadoFuncionamiento is False)
            self.assertTrue(tel_manejadoraLower01P05.comandoEncendido is False)
            self.assertAlmostEqual(-99.99, tel_manejadoraLower01P05.setpointTrabajo, places=5)
            self.assertAlmostEqual(-99.99, tel_manejadoraLower01P05.setpointVentiladorMin, places=5)
            self.assertAlmostEqual(-99.99, tel_manejadoraLower01P05.setpointVentiladorMax, places=5)
            self.assertAlmostEqual(-99.99, tel_manejadoraLower01P05.temperaturaAnticongelante, places=5)

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
            tel_manejadoraLower01P05 = await self.assert_next_sample(
                topic=self.remote.tel_manejadoraLower01P05, flush=True,
            )
            tel_manejadoraLower01P05 = await self.assert_next_sample(
                topic=self.remote.tel_manejadoraLower01P05, flush=True,
            )
            self.assertTrue(tel_manejadoraLower01P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_manejadoraLower01P05.comandoEncendido == comando_encendido)
            self.assertAlmostEqual(setpoint_trabajo, tel_manejadoraLower01P05.setpointTrabajo, places=5)
            self.assertAlmostEqual(
                setpoint_ventilador_min, tel_manejadoraLower01P05.setpointVentiladorMin, places=5
            )
            self.assertAlmostEqual(
                setpoint_ventilador_max, tel_manejadoraLower01P05.setpointVentiladorMax, places=5
            )
            self.assertAlmostEqual(
                temperatura_anticongelante, tel_manejadoraLower01P05.temperaturaAnticongelante, places=5
            )

    async def test_do_manejadoraSblancaP04(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_manejadoraSblancaP04 = await self.assert_next_sample(
                topic=self.remote.tel_manejadoraSblancaP04, flush=True,
            )
            self.assertTrue(tel_manejadoraSblancaP04.estadoFuncionamiento is False)
            self.assertTrue(tel_manejadoraSblancaP04.comandoEncendido is False)
            self.assertAlmostEqual(-99.99, tel_manejadoraSblancaP04.valorConsigna, places=5)
            self.assertAlmostEqual(-99.99, tel_manejadoraSblancaP04.setpointVentiladorMin, places=5)
            self.assertAlmostEqual(-99.99, tel_manejadoraSblancaP04.setpointVentiladorMax, places=5)

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
            tel_manejadoraSblancaP04 = await self.assert_next_sample(
                topic=self.remote.tel_manejadoraSblancaP04, flush=True,
            )
            tel_manejadoraSblancaP04 = await self.assert_next_sample(
                topic=self.remote.tel_manejadoraSblancaP04, flush=True,
            )
            self.assertTrue(tel_manejadoraSblancaP04.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_manejadoraSblancaP04.comandoEncendido == comando_encendido)
            self.assertAlmostEqual(valor_consigna, tel_manejadoraSblancaP04.valorConsigna, places=5)
            self.assertAlmostEqual(
                setpoint_ventilador_min, tel_manejadoraSblancaP04.setpointVentiladorMin, places=5
            )
            self.assertAlmostEqual(
                setpoint_ventilador_max, tel_manejadoraSblancaP04.setpointVentiladorMax, places=5
            )

    async def test_do_vea01P01(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea01P01 = await self.assert_next_sample(topic=self.remote.tel_vea01P01, flush=True,)
            self.assertTrue(tel_vea01P01.estadoFuncionamiento is False)
            self.assertTrue(tel_vea01P01.estadoSelector is False)
            self.assertTrue(tel_vea01P01.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea01P01.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )

            tel_vea01P01 = await self.assert_next_sample(topic=self.remote.tel_vea01P01, flush=True,)
            tel_vea01P01 = await self.assert_next_sample(topic=self.remote.tel_vea01P01, flush=True,)
            self.assertTrue(tel_vea01P01.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea01P01.estadoSelector == comando_encendido)
            self.assertTrue(tel_vea01P01.comandoEncendido == comando_encendido)

    async def test_do_vea01P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea01P05 = await self.assert_next_sample(topic=self.remote.tel_vea01P05, flush=True,)
            self.assertTrue(tel_vea01P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea01P05.fallaTermica is False)
            self.assertTrue(tel_vea01P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea01P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea01P05 = await self.assert_next_sample(topic=self.remote.tel_vea01P05, flush=True,)
            tel_vea01P05 = await self.assert_next_sample(topic=self.remote.tel_vea01P05, flush=True,)
            self.assertTrue(tel_vea01P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea01P05.fallaTermica is False)
            self.assertTrue(tel_vea01P05.comandoEncendido == comando_encendido)

    async def test_do_vea08P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea08P05 = await self.assert_next_sample(topic=self.remote.tel_vea08P05, flush=True,)
            self.assertTrue(tel_vea08P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea08P05.fallaTermica is False)
            self.assertTrue(tel_vea08P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea08P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea08P05 = await self.assert_next_sample(topic=self.remote.tel_vea08P05, flush=True,)
            tel_vea08P05 = await self.assert_next_sample(topic=self.remote.tel_vea08P05, flush=True,)
            self.assertTrue(tel_vea08P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea08P05.fallaTermica is False)
            self.assertTrue(tel_vea08P05.comandoEncendido == comando_encendido)

    async def test_do_vea09P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea09P05 = await self.assert_next_sample(topic=self.remote.tel_vea09P05, flush=True,)
            self.assertTrue(tel_vea09P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea09P05.fallaTermica is False)
            self.assertTrue(tel_vea09P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea09P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea09P05 = await self.assert_next_sample(topic=self.remote.tel_vea09P05, flush=True,)
            tel_vea09P05 = await self.assert_next_sample(topic=self.remote.tel_vea09P05, flush=True,)
            self.assertTrue(tel_vea09P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea09P05.fallaTermica is False)
            self.assertTrue(tel_vea09P05.comandoEncendido == comando_encendido)

    async def test_do_vea10P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea10P05 = await self.assert_next_sample(topic=self.remote.tel_vea10P05, flush=True,)
            self.assertTrue(tel_vea10P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea10P05.fallaTermica is False)
            self.assertTrue(tel_vea10P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea10P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea10P05 = await self.assert_next_sample(topic=self.remote.tel_vea10P05, flush=True,)
            tel_vea10P05 = await self.assert_next_sample(topic=self.remote.tel_vea10P05, flush=True,)
            self.assertTrue(tel_vea10P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea10P05.fallaTermica is False)
            self.assertTrue(tel_vea10P05.comandoEncendido == comando_encendido)

    async def test_do_vea11P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea11P05 = await self.assert_next_sample(topic=self.remote.tel_vea11P05, flush=True,)
            self.assertTrue(tel_vea11P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea11P05.fallaTermica is False)
            self.assertTrue(tel_vea11P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea11P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea11P05 = await self.assert_next_sample(topic=self.remote.tel_vea11P05, flush=True,)
            tel_vea11P05 = await self.assert_next_sample(topic=self.remote.tel_vea11P05, flush=True,)
            self.assertTrue(tel_vea11P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea11P05.fallaTermica is False)
            self.assertTrue(tel_vea11P05.comandoEncendido == comando_encendido)

    async def test_do_vea12P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea12P05 = await self.assert_next_sample(topic=self.remote.tel_vea12P05, flush=True,)
            self.assertTrue(tel_vea12P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea12P05.fallaTermica is False)
            self.assertTrue(tel_vea12P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea12P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea12P05 = await self.assert_next_sample(topic=self.remote.tel_vea12P05, flush=True,)
            tel_vea12P05 = await self.assert_next_sample(topic=self.remote.tel_vea12P05, flush=True,)
            self.assertTrue(tel_vea12P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea12P05.fallaTermica is False)
            self.assertTrue(tel_vea12P05.comandoEncendido == comando_encendido)

    async def test_do_vea13P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea13P05 = await self.assert_next_sample(topic=self.remote.tel_vea13P05, flush=True,)
            self.assertTrue(tel_vea13P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea13P05.fallaTermica is False)
            self.assertTrue(tel_vea13P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea13P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea13P05 = await self.assert_next_sample(topic=self.remote.tel_vea13P05, flush=True,)
            tel_vea13P05 = await self.assert_next_sample(topic=self.remote.tel_vea13P05, flush=True,)
            self.assertTrue(tel_vea13P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea13P05.fallaTermica is False)
            self.assertTrue(tel_vea13P05.comandoEncendido == comando_encendido)

    async def test_do_vea14P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea14P05 = await self.assert_next_sample(topic=self.remote.tel_vea14P05, flush=True,)
            self.assertTrue(tel_vea14P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea14P05.fallaTermica is False)
            self.assertTrue(tel_vea14P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea14P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea14P05 = await self.assert_next_sample(topic=self.remote.tel_vea14P05, flush=True,)
            tel_vea14P05 = await self.assert_next_sample(topic=self.remote.tel_vea14P05, flush=True,)
            self.assertTrue(tel_vea14P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea14P05.fallaTermica is False)
            self.assertTrue(tel_vea14P05.comandoEncendido == comando_encendido)

    async def test_do_vea15P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea15P05 = await self.assert_next_sample(topic=self.remote.tel_vea15P05, flush=True,)
            self.assertTrue(tel_vea15P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea15P05.fallaTermica is False)
            self.assertTrue(tel_vea15P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea15P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea15P05 = await self.assert_next_sample(topic=self.remote.tel_vea15P05, flush=True,)
            tel_vea15P05 = await self.assert_next_sample(topic=self.remote.tel_vea15P05, flush=True,)
            self.assertTrue(tel_vea15P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea15P05.fallaTermica is False)
            self.assertTrue(tel_vea15P05.comandoEncendido == comando_encendido)

    async def test_do_vea16P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea16P05 = await self.assert_next_sample(topic=self.remote.tel_vea16P05, flush=True,)
            self.assertTrue(tel_vea16P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea16P05.fallaTermica is False)
            self.assertTrue(tel_vea16P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea16P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea16P05 = await self.assert_next_sample(topic=self.remote.tel_vea16P05, flush=True,)
            tel_vea16P05 = await self.assert_next_sample(topic=self.remote.tel_vea16P05, flush=True,)
            self.assertTrue(tel_vea16P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea16P05.fallaTermica is False)
            self.assertTrue(tel_vea16P05.comandoEncendido == comando_encendido)

    async def test_do_vea17P05(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vea17P05 = await self.assert_next_sample(topic=self.remote.tel_vea17P05, flush=True,)
            self.assertTrue(tel_vea17P05.estadoFuncionamiento is False)
            self.assertTrue(tel_vea17P05.fallaTermica is False)
            self.assertTrue(tel_vea17P05.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vea17P05.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vea17P05 = await self.assert_next_sample(topic=self.remote.tel_vea17P05, flush=True,)
            tel_vea17P05 = await self.assert_next_sample(topic=self.remote.tel_vea17P05, flush=True,)
            self.assertTrue(tel_vea17P05.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vea17P05.fallaTermica is False)
            self.assertTrue(tel_vea17P05.comandoEncendido == comando_encendido)

    async def test_do_vec01P01(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vec01P01 = await self.assert_next_sample(topic=self.remote.tel_vec01P01, flush=True,)
            self.assertTrue(tel_vec01P01.estadoFuncionamiento is False)
            self.assertTrue(tel_vec01P01.estadoSelector is False)
            self.assertTrue(tel_vec01P01.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vec01P01.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vec01P01 = await self.assert_next_sample(topic=self.remote.tel_vec01P01, flush=True,)
            tel_vec01P01 = await self.assert_next_sample(topic=self.remote.tel_vec01P01, flush=True,)
            self.assertTrue(tel_vec01P01.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vec01P01.estadoSelector is False)
            self.assertTrue(tel_vec01P01.comandoEncendido == comando_encendido)

    async def test_do_vex03P04(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vex03P04 = await self.assert_next_sample(topic=self.remote.tel_vex03P04, flush=True,)
            self.assertTrue(tel_vex03P04.fallaTermica is False)
            self.assertTrue(tel_vex03P04.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vex03P04.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vex03P04 = await self.assert_next_sample(topic=self.remote.tel_vex03P04, flush=True,)
            tel_vex03P04 = await self.assert_next_sample(topic=self.remote.tel_vex03P04, flush=True,)
            self.assertTrue(tel_vex03P04.fallaTermica is False)
            self.assertTrue(tel_vex03P04.comandoEncendido == comando_encendido)

    async def test_do_vex04P04(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vex04P04 = await self.assert_next_sample(topic=self.remote.tel_vex04P04, flush=True,)
            self.assertTrue(tel_vex04P04.fallaTermica is False)
            self.assertTrue(tel_vex04P04.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vex04P04.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vex04P04 = await self.assert_next_sample(topic=self.remote.tel_vex04P04, flush=True,)
            tel_vex04P04 = await self.assert_next_sample(topic=self.remote.tel_vex04P04, flush=True,)
            self.assertTrue(tel_vex04P04.fallaTermica is False)
            self.assertTrue(tel_vex04P04.comandoEncendido == comando_encendido)

    async def test_do_vin01P01(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, config_dir=None, simulation_mode=1):
            await salobj.set_summary_state(remote=self.remote, state=salobj.State.ENABLED)

            tel_vin01P01 = await self.assert_next_sample(topic=self.remote.tel_vin01P01, flush=True,)
            self.assertTrue(tel_vin01P01.estadoFuncionamiento is False)
            self.assertTrue(tel_vin01P01.estadoSelector is False)
            self.assertTrue(tel_vin01P01.comandoEncendido is False)

            comando_encendido = True
            await self.remote.cmd_vin01P01.set_start(
                comandoEncendido=comando_encendido, timeout=STD_TIMEOUT,
            )
            tel_vin01P01 = await self.assert_next_sample(topic=self.remote.tel_vin01P01, flush=True,)
            tel_vin01P01 = await self.assert_next_sample(topic=self.remote.tel_vin01P01, flush=True,)
            self.assertTrue(tel_vin01P01.estadoFuncionamiento == comando_encendido)
            self.assertTrue(tel_vin01P01.estadoSelector is False)
            self.assertTrue(tel_vin01P01.comandoEncendido == comando_encendido)
