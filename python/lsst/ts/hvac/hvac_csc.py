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

__all__ = ["HvacCsc"]

import asyncio
import pathlib

from lsst.ts import salobj
from lsst.ts.hvac.mqtt_client import MqttClient
from lsst.ts.hvac.simulator.sim_client import SimClient


class HvacCsc(salobj.ConfigurableCsc):
    """Commandable SAL Component for the HVAC (Heating, Ventilation and Air
    Conditioning).

    Parameters
    ----------
    config_dir : `string`
        The configuration directory
    initial_state : `salobj.State`
        The initial state of the CSC
    simulation_mode : `int`
        Simulation mode (1) or not (0)
    """

    def __init__(
        self, config_dir=None, initial_state=salobj.State.STANDBY, simulation_mode=0,
    ):
        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "hvac.yaml")
        self.config = None
        self._config_dir = config_dir
        super().__init__(
            name="HVAC",
            index=0,
            schema_path=schema_path,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
        )
        self.mqtt_client = None
        self.telemetry_task = None
        self.log.info("__init__")

    async def connect(self):
        """Start the HVAC MQTT client or start the mock client, if in
        simulation mode.
        """
        self.log.info("Connecting")
        self.log.info(self.config)
        self.log.info(f"self.simulation_mode = {self.simulation_mode}")
        if self.config is None:
            raise RuntimeError("Not yet configured")
        if self.connected:
            raise RuntimeError("Already connected")

        if self.simulation_mode == 1:
            # Connect to the Simulator Client.
            self.log.info("Connecting to SimClient.")
            self.mqtt_client = SimClient()
        else:
            # Connect to the MQTT Client.
            self.log.info("Connecting to MqttClient.")
            self.mqtt_client = MqttClient()

        self.mqtt_client.connect()
        self.telemetry_task = asyncio.create_task(self.get_telemetry())

    async def disconnect(self):
        """Disconnect the HVAQ client, if connected.
        """
        self.log.info("Disconnecting")
        if self.telemetry_task:
            self.telemetry_task.cancel()
        if self.connected:
            self.mqtt_client.disconnect()

    async def handle_summary_state(self):
        """Override of the handle_summary_state function to connect or
        disconnect to the HVAC server (or the mock server) when needed.
        """
        self.log.info(f"handle_summary_state {salobj.State(self.summary_state).name}")
        if self.disabled_or_enabled:
            if not self.connected:
                await self.connect()
        else:
            await self.disconnect()

    async def configure(self, config):
        self.config = config

    async def implement_simulation_mode(self, simulation_mode):
        if simulation_mode not in (0, 1):
            raise salobj.ExpectedError(f"Simulation_mode={simulation_mode} must be 0 or 1")

    async def do_chiller01P01(self, data):
        self.assert_enabled()
        await self.mqtt_client.chiller01P01(
            setpoint_activo=data.setpointActivo, comando_encendido=data.comandoEncendido
        )

    async def do_crack01P02(self, data):
        self.assert_enabled()
        await self.mqtt_client.crack01P02(
            setpoint_humidificador=data.setpointHumidificador,
            setpoint_deshumidificador=data.setpointDeshumidificador,
            set_point_cooling=data.setPointCooling,
            set_point_heating=data.setPointHeating,
            comando_encendido=data.comandoEncendido,
        )

    async def do_fancoil01P02(self, data):
        self.assert_enabled()
        await self.mqtt_client.fancoil01P02(
            perc_apertura_valvula_frio=data.percAperturaValvulaFrio,
            setpoint_cooling_day=data.setpointCoolingDay,
            setpoint_heating_day=data.setpointHeatingDay,
            setpoint_cooling_night=data.setpointCoolingNight,
            setpoint_heating_night=data.setpointHeatingNight,
            setpoint_trabajo=data.setpointTrabajo,
            comando_encendido=data.comandoEncendido,
        )

    async def do_manejadoraLower01P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.manejadoraLower01P05(
            setpoint_trabajo=data.setpointTrabajo,
            setpoint_ventilador_min=data.setpointVentiladorMin,
            setpoint_ventilador_max=data.setpointVentiladorMax,
            temperatura_anticongelante=data.temperaturaAnticongelante,
            comando_encendido=data.comandoEncendido,
        )

    async def do_manejadoraSblancaP04(self, data):
        self.assert_enabled()
        await self.mqtt_client.manejadoraSblancaP04(
            valor_consigna=data.valorConsigna,
            setpoint_ventilador_min=data.setpointVentiladorMin,
            setpoint_ventilador_max=data.setpointVentiladorMax,
            comando_encendido=data.comandoEncendido,
        )

    async def do_vea01P01(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea01P01(comando_encendido=data.comandoEncendido)

    async def do_vea01P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea01P05(comando_encendido=data.comandoEncendido)

    async def do_vea08P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea08P05(comando_encendido=data.comandoEncendido)

    async def do_vea09P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea09P05(comando_encendido=data.comandoEncendido)

    async def do_vea10P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea10P05(comando_encendido=data.comandoEncendido)

    async def do_vea11P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea11P05(comando_encendido=data.comandoEncendido)

    async def do_vea12P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea12P05(comando_encendido=data.comandoEncendido)

    async def do_vea13P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea13P05(comando_encendido=data.comandoEncendido)

    async def do_vea14P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea14P05(comando_encendido=data.comandoEncendido)

    async def do_vea15P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea15P05(comando_encendido=data.comandoEncendido)

    async def do_vea16P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea16P05(comando_encendido=data.comandoEncendido)

    async def do_vea17P05(self, data):
        self.assert_enabled()
        await self.mqtt_client.vea17P05(comando_encendido=data.comandoEncendido)

    async def do_vec01P01(self, data):
        self.assert_enabled()
        await self.mqtt_client.vec01P01(comando_encendido=data.comandoEncendido)

    async def do_vex03P04(self, data):
        self.assert_enabled()
        await self.mqtt_client.vex03P04(comando_encendido=data.comandoEncendido)

    async def do_vex04P04(self, data):
        self.assert_enabled()
        await self.mqtt_client.vex04P04(comando_encendido=data.comandoEncendido)

    async def do_vin01P01(self, data):
        self.assert_enabled()
        await self.mqtt_client.vin01P01(comando_encendido=data.comandoEncendido)

    async def get_telemetry(self):
        try:
            while True:
                await self.mqtt_client.telemetry_available
                self.log.info("Telemetry available!")
                self.tel_BombaAguaFriaP01.set_put(vars(self.mqtt_client.bomba_agua_fria_p01))
                self.tel_Chiller01P01.set_put(vars(self.mqtt_client.chiller01_p01))
                self.tel_Crack01P02.set_put(vars(self.mqtt_client.crack01_p02))
                self.tel_DamperLowerP04.set_put(vars(self.mqtt_client.damper_lower_p04))
                self.tel_Fancoil01P02.set_put(vars(self.mqtt_client.fancoil01_p02))
                self.tel_ManejadoraLower01P05.set_put(vars(self.mqtt_client.manejadora_lower01_p05))
                self.tel_ManejadoraSblancaP04.set_put(vars(self.mqtt_client.manejadora_sblanca_p04))
                self.tel_ManejadraSblancaP04.set_put(vars(self.mqtt_client.manejadra_sblanca_p04))
                self.tel_ManejadoraSlimpiaP04.set_put(vars(self.mqtt_client.manejadora_slimpia_p04))
                self.tel_ManejadoraZzzP04.set_put(vars(self.mqtt_client.manejadora_zzz_p04))
                self.tel_TemperatuaAmbienteP01.set_put(vars(self.mqtt_client.temperatua_ambiente_p01))
                self.tel_ValvulaP01.set_put(vars(self.mqtt_client.valvula_p01))
                self.tel_Vea01P01.set_put(vars(self.mqtt_client.vea01_p01))
                self.tel_Vea01P05.set_put(vars(self.mqtt_client.vea01_p05))
                self.tel_Vea03P04.set_put(vars(self.mqtt_client.vea03_p04))
                self.tel_Vea04P04.set_put(vars(self.mqtt_client.vea04_p04))
                self.tel_Vea08P05.set_put(vars(self.mqtt_client.vea08_p05))
                self.tel_Vea09P05.set_put(vars(self.mqtt_client.vea09_p05))
                self.tel_Vea10P05.set_put(vars(self.mqtt_client.vea10_p05))
                self.tel_Vea11P05.set_put(vars(self.mqtt_client.vea11_p05))
                self.tel_Vea12P05.set_put(vars(self.mqtt_client.vea12_p05))
                self.tel_Vea13P05.set_put(vars(self.mqtt_client.vea13_p05))
                self.tel_Vea14P05.set_put(vars(self.mqtt_client.vea14_p05))
                self.tel_Vea15P05.set_put(vars(self.mqtt_client.vea15_p05))
                self.tel_Vea16P05.set_put(vars(self.mqtt_client.vea16_p05))
                self.tel_Vea17P05.set_put(vars(self.mqtt_client.vea17_p05))
                self.tel_Vec01P01.set_put(vars(self.mqtt_client.vec01_p01))
                self.tel_Vex03P04.set_put(vars(self.mqtt_client.vex03_p04))
                self.tel_Vex04P04.set_put(vars(self.mqtt_client.vex04_p04))
                self.tel_Vin01P01.set_put(vars(self.mqtt_client.vin01_p01))
                self.tel_ZonaCargaP04.set_put(vars(self.mqtt_client.zona_carga_p04))
        except Exception:
            self.log.exception(f"get_telemetry() failed")

    @property
    def connected(self):
        if self.mqtt_client is None:
            return False
        return True

    @staticmethod
    def get_config_pkg():
        return "ts_config_ocs"

    @classmethod
    def add_arguments(cls, parser):
        super(HvacCsc, cls).add_arguments(parser)
        parser.add_argument("-s", "--simulate", action="store_true", help="Run in simuation mode?")

    @classmethod
    def add_kwargs_from_args(cls, args, kwargs):
        super(HvacCsc, cls).add_kwargs_from_args(args, kwargs)
        kwargs["simulation_mode"] = 1 if args.simulate else 0
