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

__all__ = ["SimClient"]

import asyncio
import logging

from lsst.ts.hvac.simulator.sim_telemetry import (
    BombaAguaFriaP01,
    Chiller01P01,
    Crack01P02,
    DamperLowerP04,
    Fancoil01P02,
    ManejadoraLower01P05,
    ManejadoraSblancaP04,
    ManejadoraSlimpiaP04,
    ManejadoraZzzP04,
    ManejadraSblancaP04,
    TemperatuaAmbienteP01,
    ValvulaP01,
    Vea01P01,
    Vea01P05,
    Vea03P04,
    Vea04P04,
    Vea08P05,
    Vea09P05,
    Vea10P05,
    Vea11P05,
    Vea12P05,
    Vea13P05,
    Vea14P05,
    Vea15P05,
    Vea16P05,
    Vea17P05,
    Vec01P01,
    Vex03P04,
    Vex04P04,
    Vin01P01,
    ZonaCargaP04,
)


def validate_percentage(percentage):
    """Ensure that the provided percentage has a value in the range [0, 100].

    Parameters
    ----------
    percentage: `float`
        The percentage to validate.
    """
    if percentage < 0 or percentage > 100:
        raise ValueError("Invalid value encountered.")


class SimClient:
    def __init__(self):
        self.log = logging.getLogger("SimClient")
        self.log.info("__init__")
        self.telemetry_task = None
        self.telemetry_available = asyncio.Event

        self.bomba_agua_fria_p01 = BombaAguaFriaP01()
        self.chiller01_p01 = Chiller01P01()
        self.crack01_p02 = Crack01P02()
        self.damper_lower_p04 = DamperLowerP04()
        self.fancoil01_p02 = Fancoil01P02()
        self.manejadora_lower01_p05 = ManejadoraLower01P05()
        self.manejadora_sblanca_p04 = ManejadoraSblancaP04()
        self.manejadora_slimpia_p04 = ManejadoraSlimpiaP04()
        self.manejadora_zzz_p04 = ManejadoraZzzP04()
        self.manejadra_sblanca_p04 = ManejadraSblancaP04()
        self.temperatua_ambiente_p01 = TemperatuaAmbienteP01()
        self.valvula_p01 = ValvulaP01()
        self.vea01_p01 = Vea01P01()
        self.vea01_p05 = Vea01P05()
        self.vea03_p04 = Vea03P04()
        self.vea04_p04 = Vea04P04()
        self.vea08_p05 = Vea08P05()
        self.vea09_p05 = Vea09P05()
        self.vea10_p05 = Vea10P05()
        self.vea11_p05 = Vea11P05()
        self.vea12_p05 = Vea12P05()
        self.vea13_p05 = Vea13P05()
        self.vea14_p05 = Vea14P05()
        self.vea15_p05 = Vea15P05()
        self.vea16_p05 = Vea16P05()
        self.vea17_p05 = Vea17P05()
        self.vec01_p01 = Vec01P01()
        self.vex03_p04 = Vex03P04()
        self.vex04_p04 = Vex04P04()
        self.vin01_p01 = Vin01P01()
        self.zona_carga_p04 = ZonaCargaP04()

    def connect(self):
        """Starts the publishing of telemetry.
        """
        self.telemetry_task = asyncio.create_task(self.publish_telemetry())
        self.log.info("Connected.")

    def disconnect(self):
        """Stops the publishing of telemetry.
        """
        if self.telemetry_task:
            self.telemetry_task.cancel()
        self.log.info("Disconnected.")

    async def chiller01P01(self, setpoint_activo, comando_encendido):
        """Command Chiller 01 on the first floor.

        Parameters
        ----------
        setpoint_activo: `float`
            The setpoint for the activity.
        comando_encendido: `bool`
            Switched on or off.
        """
        validate_percentage(setpoint_activo)
        self.chiller01_p01.setpointActivo = setpoint_activo
        self.chiller01_p01.comandoEncendido = comando_encendido

    async def crack01P02(
        self,
        setpoint_humidificador,
        setpoint_deshumidificador,
        set_point_cooling,
        set_point_heating,
        comando_encendido,
    ):
        """Command Crack 01 on the second floor.

        Parameters
        ----------
        setpoint_humidificador: `float`
            The setpoint for the humidificator.
        setpoint_deshumidificador: `float`
            The setpoint for the deshumificator.
        set_point_cooling: `float`
            The setpoint for the cooling.
        set_point_heating: `float`
            The setpoint for the heating.
        comando_encendido: `bool`
            Switched on or off.
        """
        validate_percentage(setpoint_humidificador)
        validate_percentage(setpoint_deshumidificador)
        validate_percentage(set_point_cooling)
        validate_percentage(set_point_heating)
        self.crack01_p02.setpointHumidificador = setpoint_humidificador
        self.crack01_p02.setpointDeshumidificador = setpoint_deshumidificador
        self.crack01_p02.setPointCooling = set_point_cooling
        self.crack01_p02.setPointHeating = set_point_heating
        self.crack01_p02.comandoEncendido = comando_encendido

    async def fancoil01P02(
        self,
        perc_apertura_valvula_frio,
        setpoint_cooling_day,
        setpoint_heating_day,
        setpoint_cooling_night,
        setpoint_heating_night,
        setpoint_trabajo,
        comando_encendido,
    ):
        """Command the Fancoil 01 on the second floor.

        Parameters
        ----------
        perc_apertura_valvula_frio: `float`
            The percentage of opening of the cold valve.
        setpoint_cooling_day: `float`
            The setpoint for the cooling during the day.
        setpoint_heating_day: `float`
            The setpoint for the heating during the day.
        setpoint_cooling_night: `float`
            The setpoint for the cooling during the night.
        setpoint_heating_night: `float`
            The setpoint for the heating during the night.
        setpoint_trabajo: `float`
            The setpoint for the 'work'.
        comando_encendido: `bool`
            Switched on or off.
        """
        validate_percentage(perc_apertura_valvula_frio)
        validate_percentage(setpoint_cooling_day)
        validate_percentage(setpoint_heating_day)
        validate_percentage(setpoint_cooling_night)
        validate_percentage(setpoint_heating_night)
        validate_percentage(setpoint_trabajo)
        self.fancoil01_p02.aperturaValvulaFrio = perc_apertura_valvula_frio
        self.fancoil01_p02.setpointCoolingDay = setpoint_cooling_day
        self.fancoil01_p02.setpointHeatingDay = setpoint_heating_day
        self.fancoil01_p02.setpointCoolingNight = setpoint_cooling_night
        self.fancoil01_p02.setpointHeatingNight = setpoint_heating_night
        self.fancoil01_p02.setpointTrabajo = setpoint_trabajo
        self.fancoil01_p02.comandoEncendido = comando_encendido

    async def manejadoraLower01P05(
        self,
        setpoint_trabajo,
        setpoint_ventilador_min,
        setpoint_ventilador_max,
        temperatura_anticongelante,
        comando_encendido,
    ):
        """Command the Lower Manejadora 01 on the fifth floor.

        Parameters
        ----------
        setpoint_trabajo: `float`
            The setpoint for the 'work'.
        setpoint_ventilador_min: `float`
            The minimum setpoint for the fan.
        setpoint_ventilador_max: `float`
            The maximum setpoint for the fan.
        temperatura_anticongelante: `float`
            The temperature of the anti-freeze.
        comando_encendido: `bool`
            Switched on or off.
        """
        validate_percentage(setpoint_trabajo)
        validate_percentage(setpoint_ventilador_min)
        validate_percentage(setpoint_ventilador_max)
        self.manejadora_lower01_p05.setpointTrabajo = setpoint_trabajo
        self.manejadora_lower01_p05.setpointVentiladorMin = setpoint_ventilador_min
        self.manejadora_lower01_p05.setpointVentiladorMax = setpoint_ventilador_max
        self.manejadora_lower01_p05.temperaturaAnticongelante = temperatura_anticongelante
        self.manejadora_lower01_p05.comandoEncendido = comando_encendido

    async def manejadoraSblancaP04(
        self, valor_consigna, setpoint_ventilador_min, setpoint_ventilador_max, comando_encendido,
    ):
        """Command the Sala Blanca Manejadora on the fourth floor.

        Parameters
        ----------
        valor_consigna: `float`
            The value of the 'consigna'.
        setpoint_ventilador_min: `float`
            The minimum setpoint for the fan.
        setpoint_ventilador_max: `float`
            The maximum setpoint for the fan.
        comando_encendido: `bool`
            Switched on or off.
        """
        validate_percentage(valor_consigna)
        validate_percentage(setpoint_ventilador_min)
        validate_percentage(setpoint_ventilador_max)
        self.manejadora_sblanca_p04.valorConsigna = valor_consigna
        self.manejadora_sblanca_p04.setpointVentiladorMin = setpoint_ventilador_min
        self.manejadora_sblanca_p04.setpointVentiladorMax = setpoint_ventilador_max
        self.manejadora_sblanca_p04.comandoEncendido = comando_encendido

    async def vea01P01(self, comando_encendido):
        """Command VEA 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea01_p01.comandoEncendido = comando_encendido

    async def vea01P05(self, comando_encendido):
        """Command VEA 01 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea01_p05.comandoEncendido = comando_encendido

    async def vea08P05(self, comando_encendido):
        """Command VEA 08 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea08_p05.comandoEncendido = comando_encendido

    async def vea09P05(self, comando_encendido):
        """Command VEA 09 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea09_p05.comandoEncendido = comando_encendido

    async def vea10P05(self, comando_encendido):
        """Command VEA 10 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea10_p05.comandoEncendido = comando_encendido

    async def vea11P05(self, comando_encendido):
        """Command VEA 11 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea11_p05.comandoEncendido = comando_encendido

    async def vea12P05(self, comando_encendido):
        """Command VEA 12 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea12_p05.comandoEncendido = comando_encendido

    async def vea13P05(self, comando_encendido):
        """Command VEA 13 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea13_p05.comandoEncendido = comando_encendido

    async def vea14P05(self, comando_encendido):
        """Command VEA 14 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea14_p05.comandoEncendido = comando_encendido

    async def vea15P05(self, comando_encendido):
        """Command VEA 15 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea15_p05.comandoEncendido = comando_encendido

    async def vea16P05(self, comando_encendido):
        """Command VEA 16 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea16_p05.comandoEncendido = comando_encendido

    async def vea17P05(self, comando_encendido):
        """Command VEA 17 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vea17_p05.comandoEncendido = comando_encendido

    async def vec01P01(self, comando_encendido):
        """Command VEC 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vec01_p01.comandoEncendido = comando_encendido

    async def vex03P04(self, comando_encendido):
        """Command VEX 03 on the fourth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vex03_p04.comandoEncendido = comando_encendido

    async def vex04P04(self, comando_encendido):
        """Command VEX 04 on the fourth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vex04_p04.comandoEncendido = comando_encendido

    async def vin01P01(self, comando_encendido):
        """Command VIN 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.vin01_p01.comandoEncendido = comando_encendido

    async def publish_telemetry(self):
        """Publishes telmetry every second to simulate the behaviour of an
        MQTT server.
        """
        try:
            while True:
                await self.bomba_agua_fria_p01.update_status()
                await self.chiller01_p01.update_status()
                await self.crack01_p02.update_status()
                await self.damper_lower_p04.update_status()
                await self.fancoil01_p02.update_status()
                await self.manejadora_lower01_p05.update_status()
                await self.manejadora_sblanca_p04.update_status()
                await self.manejadora_slimpia_p04.update_status()
                await self.manejadora_zzz_p04.update_status()
                await self.manejadra_sblanca_p04.update_status()
                await self.temperatua_ambiente_p01.update_status()
                await self.valvula_p01.update_status()
                await self.vea01_p01.update_status()
                await self.vea01_p05.update_status()
                await self.vea03_p04.update_status()
                await self.vea04_p04.update_status()
                await self.vea08_p05.update_status()
                await self.vea09_p05.update_status()
                await self.vea10_p05.update_status()
                await self.vea11_p05.update_status()
                await self.vea12_p05.update_status()
                await self.vea13_p05.update_status()
                await self.vea14_p05.update_status()
                await self.vea15_p05.update_status()
                await self.vea16_p05.update_status()
                await self.vea17_p05.update_status()
                await self.vec01_p01.update_status()
                await self.vex03_p04.update_status()
                await self.vex04_p04.update_status()
                await self.vin01_p01.update_status()
                await self.zona_carga_p04.update_status()

                await asyncio.sleep(1.0)
        except Exception:
            self.log.exception(f"publish_telemetry() failed")
