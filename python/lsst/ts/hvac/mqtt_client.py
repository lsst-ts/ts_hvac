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

__all__ = ["MqttClient"]

import asyncio
import logging

from lsst.ts import salobj


class MqttClient:
    def __init__(self):
        self.log = logging.getLogger("MqttClient")
        self.log.info("__init__")
        self.telemetry_available = asyncio.Event

    def connect(self):
        # TODO Add code to connect to the MQTT server.
        pass

    def disconnect(self):
        # TODO Add code to disconnect from the MQTT server.
        pass

    async def chiller01P01(self, setpoint_activo, comando_encendido):
        """Command Chiller 01 on the first floor.

        Parameters
        ----------
        setpoint_activo: `float`
            The setpoint for the activity.
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

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
        raise salobj.ExpectedError("Not implemented")

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
        raise salobj.ExpectedError("Not implemented")

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
        raise salobj.ExpectedError("Not implemented")

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
        raise salobj.ExpectedError("Not implemented")

    async def vea01P01(self, comando_encendido):
        """Command VEA 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea01P05(self, comando_encendido):
        """Command VEA 01 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea08P05(self, comando_encendido):
        """Command VEA 08 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea09P05(self, comando_encendido):
        """Command VEA 09 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea10P05(self, comando_encendido):
        """Command VEA 10 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea11P05(self, comando_encendido):
        """Command VEA 11 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea12P05(self, comando_encendido):
        """Command VEA 12 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea13P05(self, comando_encendido):
        """Command VEA 13 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea14P05(self, comando_encendido):
        """Command VEA 14 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea15P05(self, comando_encendido):
        """Command VEA 15 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea16P05(self, comando_encendido):
        """Command VEA 16 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vea17P05(self, comando_encendido):
        """Command VEA 17 on the fifth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vec01P01(self, comando_encendido):
        """Command VEC 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vex03P04(self, comando_encendido):
        """Command VEX 03 on the fourth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vex04P04(self, comando_encendido):
        """Command VEX 04 on the fourth floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")

    async def vin01P01(self, comando_encendido):
        """Command VIN 01 on the first floor.

        Parameters
        ----------
        comando_encendido: `bool`
            Switched on or off.
        """
        raise salobj.ExpectedError("Not implemented")
