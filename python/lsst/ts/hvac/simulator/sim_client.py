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

from lsst.ts.hvac.simulator import telemetry


def validate_percentage(percentage):
    """Ensure that the provided percentage has a value in the range [0, 100].

    Parameters
    ----------
    percentage: `float`
        The percentage to validate.

    Raises
    ------
    ValueError
        If the percentage is out of range.
    """
    if percentage < 0 or percentage > 100:
        raise ValueError(f"Invalid percentage {percentage} encountered.")


class SimClient:
    def __init__(self):
        self.log = logging.getLogger("SimClient")
        self.telemetry_task = None
        self.telemetry_available = asyncio.Event()
        self.connected = False

        self.tel_bomba_agua_fria_p01 = telemetry.BombaAguaFriaP01()
        self.tel_chiller01_p01 = telemetry.Chiller01P01()
        self.tel_crack01_p02 = telemetry.Crack01P02()
        self.tel_damper_lower_p04 = telemetry.DamperLowerP04()
        self.tel_fancoil01_p02 = telemetry.Fancoil01P02()
        self.tel_manejadora_lower01_p05 = telemetry.ManejadoraLower01P05()
        self.tel_manejadora_sblanca_p04 = telemetry.ManejadoraSblancaP04()
        self.tel_manejadora_slimpia_p04 = telemetry.ManejadoraSlimpiaP04()
        self.tel_manejadora_zzz_p04 = telemetry.ManejadoraZzzP04()
        self.tel_manejadra_sblanca_p04 = telemetry.ManejadraSblancaP04()
        self.tel_temperatua_ambiente_p01 = telemetry.TemperatuaAmbienteP01()
        self.tel_valvula_p01 = telemetry.ValvulaP01()
        self.tel_vea01_p01 = telemetry.Vea01P01()
        self.tel_vea01_p05 = telemetry.Vea01P05()
        self.tel_vea03_p04 = telemetry.Vea03P04()
        self.tel_vea04_p04 = telemetry.Vea04P04()
        self.tel_vea08_p05 = telemetry.Vea08P05()
        self.tel_vea09_p05 = telemetry.Vea09P05()
        self.tel_vea10_p05 = telemetry.Vea10P05()
        self.tel_vea11_p05 = telemetry.Vea11P05()
        self.tel_vea12_p05 = telemetry.Vea12P05()
        self.tel_vea13_p05 = telemetry.Vea13P05()
        self.tel_vea14_p05 = telemetry.Vea14P05()
        self.tel_vea15_p05 = telemetry.Vea15P05()
        self.tel_vea16_p05 = telemetry.Vea16P05()
        self.tel_vea17_p05 = telemetry.Vea17P05()
        self.tel_vec01_p01 = telemetry.Vec01P01()
        self.tel_vex03_p04 = telemetry.Vex03P04()
        self.tel_vex04_p04 = telemetry.Vex04P04()
        self.tel_vin01_p01 = telemetry.Vin01P01()
        self.tel_zona_carga_p04 = telemetry.ZonaCargaP04()

        self.log.info("SimClient constructed")

    def connect(self):
        """Starts the publishing of telemetry.
        """
        self.telemetry_task = asyncio.create_task(self.publish_telemetry())
        self.connected = True
        self.log.info("Connected.")

    def disconnect(self):
        """Stops the publishing of telemetry.
        """
        if self.telemetry_task:
            self.telemetry_task.cancel()
        self.connected = False
        self.log.info("Disconnected.")

    async def do_chiller01P01(self, setpoint_activo, comando_encendido):
        """Command Chiller 01 on the first floor.

        Parameters
        ----------
        setpoint_activo: `float`
            The setpoint for the activity.
        comando_encendido: `bool`
            Switched on or off.
        """
        validate_percentage(setpoint_activo)
        self.tel_chiller01_p01.setpointActivo = setpoint_activo
        self.tel_chiller01_p01.comandoEncendido = comando_encendido

    async def do_crack01P02(
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
        self.tel_crack01_p02.setpointHumidificador = setpoint_humidificador
        self.tel_crack01_p02.setpointDeshumidificador = setpoint_deshumidificador
        self.tel_crack01_p02.setPointCooling = set_point_cooling
        self.tel_crack01_p02.setPointHeating = set_point_heating
        self.tel_crack01_p02.comandoEncendido = comando_encendido

    async def do_fancoil01P02(
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
        self.tel_fancoil01_p02.aperturaValvulaFrio = perc_apertura_valvula_frio
        self.tel_fancoil01_p02.setpointCoolingDay = setpoint_cooling_day
        self.tel_fancoil01_p02.setpointHeatingDay = setpoint_heating_day
        self.tel_fancoil01_p02.setpointCoolingNight = setpoint_cooling_night
        self.tel_fancoil01_p02.setpointHeatingNight = setpoint_heating_night
        self.tel_fancoil01_p02.setpointTrabajo = setpoint_trabajo
        self.tel_fancoil01_p02.comandoEncendido = comando_encendido

    async def do_manejadoraLower01P05(
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
        self.tel_manejadora_lower01_p05.setpointTrabajo = setpoint_trabajo
        self.tel_manejadora_lower01_p05.setpointVentiladorMin = setpoint_ventilador_min
        self.tel_manejadora_lower01_p05.setpointVentiladorMax = setpoint_ventilador_max
        self.tel_manejadora_lower01_p05.temperaturaAnticongelante = temperatura_anticongelante
        self.tel_manejadora_lower01_p05.comandoEncendido = comando_encendido

    async def do_manejadoraSblancaP04(
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
        self.tel_manejadora_sblanca_p04.valorConsigna = valor_consigna
        self.tel_manejadora_sblanca_p04.setpointVentiladorMin = setpoint_ventilador_min
        self.tel_manejadora_sblanca_p04.setpointVentiladorMax = setpoint_ventilador_max
        self.tel_manejadora_sblanca_p04.comandoEncendido = comando_encendido

    async def do_vea01P01(self, comando_encendido):
        """Command VEA 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea01_p01.comandoEncendido = comando_encendido

    async def do_vea01P05(self, comando_encendido):
        """Command VEA 01 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea01_p05.comandoEncendido = comando_encendido

    async def do_vea08P05(self, comando_encendido):
        """Command VEA 08 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea08_p05.comandoEncendido = comando_encendido

    async def do_vea09P05(self, comando_encendido):
        """Command VEA 09 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea09_p05.comandoEncendido = comando_encendido

    async def do_vea10P05(self, comando_encendido):
        """Command VEA 10 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea10_p05.comandoEncendido = comando_encendido

    async def do_vea11P05(self, comando_encendido):
        """Command VEA 11 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea11_p05.comandoEncendido = comando_encendido

    async def do_vea12P05(self, comando_encendido):
        """Command VEA 12 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea12_p05.comandoEncendido = comando_encendido

    async def do_vea13P05(self, comando_encendido):
        """Command VEA 13 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea13_p05.comandoEncendido = comando_encendido

    async def do_vea14P05(self, comando_encendido):
        """Command VEA 14 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea14_p05.comandoEncendido = comando_encendido

    async def do_vea15P05(self, comando_encendido):
        """Command VEA 15 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea15_p05.comandoEncendido = comando_encendido

    async def do_vea16P05(self, comando_encendido):
        """Command VEA 16 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea16_p05.comandoEncendido = comando_encendido

    async def do_vea17P05(self, comando_encendido):
        """Command VEA 17 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vea17_p05.comandoEncendido = comando_encendido

    async def do_vec01P01(self, comando_encendido):
        """Command VEC 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vec01_p01.comandoEncendido = comando_encendido

    async def do_vex03P04(self, comando_encendido):
        """Command VEX 03 on the fourth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vex03_p04.comandoEncendido = comando_encendido

    async def do_vex04P04(self, comando_encendido):
        """Command VEX 04 on the fourth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vex04_p04.comandoEncendido = comando_encendido

    async def do_vin01P01(self, comando_encendido):
        """Command VIN 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        self.tel_vin01_p01.comandoEncendido = comando_encendido

    async def publish_telemetry(self):
        """Publishes telmetry every second to simulate the behaviour of an
        MQTT server.
        """
        try:
            while True:
                self.log.info("self.telemetry_available.is_set() " f"= {self.telemetry_available.is_set()}")
                await asyncio.sleep(0.1)
                if not self.telemetry_available.is_set():
                    self.log.info("Publishing telemetry.")
                    await self.tel_bomba_agua_fria_p01.update_status()
                    await self.tel_chiller01_p01.update_status()
                    await self.tel_crack01_p02.update_status()
                    await self.tel_damper_lower_p04.update_status()
                    await self.tel_fancoil01_p02.update_status()
                    await self.tel_manejadora_lower01_p05.update_status()
                    await self.tel_manejadora_sblanca_p04.update_status()
                    await self.tel_manejadora_slimpia_p04.update_status()
                    await self.tel_manejadora_zzz_p04.update_status()
                    await self.tel_manejadra_sblanca_p04.update_status()
                    await self.tel_temperatua_ambiente_p01.update_status()
                    await self.tel_valvula_p01.update_status()
                    await self.tel_vea01_p01.update_status()
                    await self.tel_vea01_p05.update_status()
                    await self.tel_vea03_p04.update_status()
                    await self.tel_vea04_p04.update_status()
                    await self.tel_vea08_p05.update_status()
                    await self.tel_vea09_p05.update_status()
                    await self.tel_vea10_p05.update_status()
                    await self.tel_vea11_p05.update_status()
                    await self.tel_vea12_p05.update_status()
                    await self.tel_vea13_p05.update_status()
                    await self.tel_vea14_p05.update_status()
                    await self.tel_vea15_p05.update_status()
                    await self.tel_vea16_p05.update_status()
                    await self.tel_vea17_p05.update_status()
                    await self.tel_vec01_p01.update_status()
                    await self.tel_vex03_p04.update_status()
                    await self.tel_vex04_p04.update_status()
                    await self.tel_vin01_p01.update_status()
                    await self.tel_zona_carga_p04.update_status()

                    await asyncio.sleep(1.0)
                    self.telemetry_available.set()
        except asyncio.CancelledError:
            # Normal exit
            pass
        except Exception:
            self.log.exception(f"publish_telemetry() failed")
