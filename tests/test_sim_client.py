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

from lsst.ts.hvac.simulator.sim_client import SimClient

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG)


class SimClientTestCase(asynctest.TestCase):
    async def setUp(self):
        self.log = logging.getLogger("SimClientTestCase")
        self.mqtt_client = SimClient()

    async def test_chiller01P01(self):
        expected_setpoint_activo = 90
        expected_comando_encendido = True
        await self.mqtt_client.chiller01P01(
            setpoint_activo=expected_setpoint_activo, comando_encendido=expected_comando_encendido
        )
        self.assertEqual(expected_setpoint_activo, self.mqtt_client.chiller01_p01.setpointActivo)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.chiller01_p01.comandoEncendido)

        expected_setpoint_activo = 110
        with self.assertRaises(ValueError):
            await self.mqtt_client.chiller01P01(
                setpoint_activo=expected_setpoint_activo, comando_encendido=expected_comando_encendido
            )

        expected_setpoint_activo = -11
        with self.assertRaises(ValueError):
            await self.mqtt_client.chiller01P01(
                setpoint_activo=expected_setpoint_activo, comando_encendido=expected_comando_encendido
            )

    async def test_crack01P02(self):
        expected_setpoint_humidificador = 90
        expected_setpoint_deshumidificador = 80
        expected_set_point_cooling = 70
        expected_set_point_heating = 60
        expected_comando_encendido = True
        await self.mqtt_client.crack01P02(
            setpoint_humidificador=expected_setpoint_humidificador,
            setpoint_deshumidificador=expected_setpoint_deshumidificador,
            set_point_cooling=expected_set_point_cooling,
            set_point_heating=expected_set_point_heating,
            comando_encendido=expected_comando_encendido,
        )
        self.assertEqual(expected_setpoint_humidificador, self.mqtt_client.crack01_p02.setpointHumidificador)
        self.assertEqual(
            expected_setpoint_deshumidificador, self.mqtt_client.crack01_p02.setpointDeshumidificador
        )
        self.assertEqual(expected_set_point_cooling, self.mqtt_client.crack01_p02.setPointCooling)
        self.assertEqual(expected_set_point_heating, self.mqtt_client.crack01_p02.setPointHeating)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.crack01_p02.comandoEncendido)

        expected_setpoint_humidificador = 110
        with self.assertRaises(ValueError):
            await self.mqtt_client.crack01P02(
                setpoint_humidificador=expected_setpoint_humidificador,
                setpoint_deshumidificador=expected_setpoint_deshumidificador,
                set_point_cooling=expected_set_point_cooling,
                set_point_heating=expected_set_point_heating,
                comando_encendido=expected_comando_encendido,
            )

        expected_setpoint_humidificador = -11
        with self.assertRaises(ValueError):
            await self.mqtt_client.crack01P02(
                setpoint_humidificador=expected_setpoint_humidificador,
                setpoint_deshumidificador=expected_setpoint_deshumidificador,
                set_point_cooling=expected_set_point_cooling,
                set_point_heating=expected_set_point_heating,
                comando_encendido=expected_comando_encendido,
            )

    async def test_fancoil01P02(self):
        expected_perc_apertura_valvula_frio = 90
        expected_setpoint_cooling_day = 89
        expected_setpoint_heating_day = 88
        expected_setpoint_cooling_night = 87
        expected_setpoint_heating_night = 86
        expected_setpoint_trabajo = 85
        expected_comando_encendido = True
        await self.mqtt_client.fancoil01P02(
            perc_apertura_valvula_frio=expected_perc_apertura_valvula_frio,
            setpoint_cooling_day=expected_setpoint_cooling_day,
            setpoint_heating_day=expected_setpoint_heating_day,
            setpoint_cooling_night=expected_setpoint_cooling_night,
            setpoint_heating_night=expected_setpoint_heating_night,
            setpoint_trabajo=expected_setpoint_trabajo,
            comando_encendido=expected_comando_encendido,
        )
        self.assertEqual(
            expected_perc_apertura_valvula_frio, self.mqtt_client.fancoil01_p02.aperturaValvulaFrio
        )
        self.assertEqual(expected_setpoint_cooling_day, self.mqtt_client.fancoil01_p02.setpointCoolingDay)
        self.assertEqual(expected_setpoint_heating_day, self.mqtt_client.fancoil01_p02.setpointHeatingDay)
        self.assertEqual(expected_setpoint_cooling_night, self.mqtt_client.fancoil01_p02.setpointCoolingNight)
        self.assertEqual(expected_setpoint_heating_night, self.mqtt_client.fancoil01_p02.setpointHeatingNight)
        self.assertEqual(expected_setpoint_trabajo, self.mqtt_client.fancoil01_p02.setpointTrabajo)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.fancoil01_p02.comandoEncendido)

        expected_setpoint_heating_night = 110
        with self.assertRaises(ValueError):
            await self.mqtt_client.fancoil01P02(
                perc_apertura_valvula_frio=expected_perc_apertura_valvula_frio,
                setpoint_cooling_day=expected_setpoint_cooling_day,
                setpoint_heating_day=expected_setpoint_heating_day,
                setpoint_cooling_night=expected_setpoint_cooling_night,
                setpoint_heating_night=expected_setpoint_heating_night,
                setpoint_trabajo=expected_setpoint_trabajo,
                comando_encendido=expected_comando_encendido,
            )

        expected_setpoint_heating_night = -11
        with self.assertRaises(ValueError):
            await self.mqtt_client.fancoil01P02(
                perc_apertura_valvula_frio=expected_perc_apertura_valvula_frio,
                setpoint_cooling_day=expected_setpoint_cooling_day,
                setpoint_heating_day=expected_setpoint_heating_day,
                setpoint_cooling_night=expected_setpoint_cooling_night,
                setpoint_heating_night=expected_setpoint_heating_night,
                setpoint_trabajo=expected_setpoint_trabajo,
                comando_encendido=expected_comando_encendido,
            )

    async def test_manejadoraLower01P05(self):
        expected_setpoint_trabajo = 90
        expected_setpoint_ventilador_min = 30
        expected_setpoint_ventilador_max = 60
        expected_temperatura_anticongelante = 25
        expected_comando_encendido = True
        await self.mqtt_client.manejadoraLower01P05(
            setpoint_trabajo=expected_setpoint_trabajo,
            setpoint_ventilador_min=expected_setpoint_ventilador_min,
            setpoint_ventilador_max=expected_setpoint_ventilador_max,
            temperatura_anticongelante=expected_temperatura_anticongelante,
            comando_encendido=expected_comando_encendido,
        )
        self.assertEqual(expected_setpoint_trabajo, self.mqtt_client.manejadora_lower01_p05.setpointTrabajo)
        self.assertEqual(
            expected_setpoint_ventilador_min, self.mqtt_client.manejadora_lower01_p05.setpointVentiladorMin
        )
        self.assertEqual(
            expected_setpoint_ventilador_max, self.mqtt_client.manejadora_lower01_p05.setpointVentiladorMax
        )
        self.assertEqual(
            expected_temperatura_anticongelante,
            self.mqtt_client.manejadora_lower01_p05.temperaturaAnticongelante,
        )
        self.assertEqual(expected_comando_encendido, self.mqtt_client.manejadora_lower01_p05.comandoEncendido)

        expected_setpoint_trabajo = 110
        with self.assertRaises(ValueError):
            await self.mqtt_client.manejadoraLower01P05(
                setpoint_trabajo=expected_setpoint_trabajo,
                setpoint_ventilador_min=expected_setpoint_ventilador_min,
                setpoint_ventilador_max=expected_setpoint_ventilador_max,
                temperatura_anticongelante=expected_temperatura_anticongelante,
                comando_encendido=expected_comando_encendido,
            )

        expected_setpoint_trabajo = -11
        with self.assertRaises(ValueError):
            await self.mqtt_client.manejadoraLower01P05(
                setpoint_trabajo=expected_setpoint_trabajo,
                setpoint_ventilador_min=expected_setpoint_ventilador_min,
                setpoint_ventilador_max=expected_setpoint_ventilador_max,
                temperatura_anticongelante=expected_temperatura_anticongelante,
                comando_encendido=expected_comando_encendido,
            )

    async def test_manejadoraSblancaP04(self):
        expected_valor_consigna = 90
        expected_setpoint_ventilador_min = 30
        expected_setpoint_ventilador_max = 60
        expected_comando_encendido = True
        await self.mqtt_client.manejadoraSblancaP04(
            valor_consigna=expected_valor_consigna,
            setpoint_ventilador_min=expected_setpoint_ventilador_min,
            setpoint_ventilador_max=expected_setpoint_ventilador_max,
            comando_encendido=expected_comando_encendido,
        )
        self.assertEqual(expected_valor_consigna, self.mqtt_client.manejadora_sblanca_p04.valorConsigna)
        self.assertEqual(
            expected_setpoint_ventilador_min, self.mqtt_client.manejadora_sblanca_p04.setpointVentiladorMin
        )
        self.assertEqual(
            expected_setpoint_ventilador_max, self.mqtt_client.manejadora_sblanca_p04.setpointVentiladorMax
        )
        self.assertEqual(expected_comando_encendido, self.mqtt_client.manejadora_sblanca_p04.comandoEncendido)

        expected_valor_consigna = 110
        with self.assertRaises(ValueError):
            await self.mqtt_client.manejadoraSblancaP04(
                valor_consigna=expected_valor_consigna,
                setpoint_ventilador_min=expected_setpoint_ventilador_min,
                setpoint_ventilador_max=expected_setpoint_ventilador_max,
                comando_encendido=expected_comando_encendido,
            )

        expected_valor_consigna = -11
        with self.assertRaises(ValueError):
            await self.mqtt_client.manejadoraSblancaP04(
                valor_consigna=expected_valor_consigna,
                setpoint_ventilador_min=expected_setpoint_ventilador_min,
                setpoint_ventilador_max=expected_setpoint_ventilador_max,
                comando_encendido=expected_comando_encendido,
            )

    async def test_vea01P01(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea01P01(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea01_p01.comandoEncendido)

    async def test_vea01P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea01P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea01_p05.comandoEncendido)

    async def test_vea08P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea08P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea08_p05.comandoEncendido)

    async def test_vea09P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea09P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea09_p05.comandoEncendido)

    async def test_vea10P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea10P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea10_p05.comandoEncendido)

    async def test_vea11P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea11P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea11_p05.comandoEncendido)

    async def test_vea12P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea12P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea12_p05.comandoEncendido)

    async def test_vea13P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea13P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea13_p05.comandoEncendido)

    async def test_vea14P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea14P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea14_p05.comandoEncendido)

    async def test_vea15P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea15P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea15_p05.comandoEncendido)

    async def test_vea16P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea16P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea16_p05.comandoEncendido)

    async def test_vea17P05(self):
        expected_comando_encendido = True
        await self.mqtt_client.vea17P05(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vea17_p05.comandoEncendido)

    async def test_vec01P01(self):
        expected_comando_encendido = True
        await self.mqtt_client.vec01P01(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vec01_p01.comandoEncendido)

    async def test_vex03P04(self):
        expected_comando_encendido = True
        await self.mqtt_client.vex03P04(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vex03_p04.comandoEncendido)

    async def test_vex04P04(self):
        expected_comando_encendido = True
        await self.mqtt_client.vex04P04(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vex04_p04.comandoEncendido)

    async def test_vin01P01(self):
        expected_comando_encendido = True
        await self.mqtt_client.vin01P01(comando_encendido=expected_comando_encendido)
        self.assertEqual(expected_comando_encendido, self.mqtt_client.vin01_p01.comandoEncendido)
