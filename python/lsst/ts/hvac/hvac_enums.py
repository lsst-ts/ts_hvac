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

__all__ = ["SPANISH_TO_ENGLISH_DICTIONARY", "HvacTopic", "TelemetryItem", "CommandItem"]

from enum import Enum

SPANISH_TO_ENGLISH_DICTIONARY = {
    "ACTIVO": "Active",
    "AGUA": "Water",
    "ALARMA": "Alarm",
    "ALARMADO": "Alarming",
    "AMBIENTE": "Ambient",
    "ANTICONGELANTE": "Anti-freeze",
    "APERTURA": "Opening",
    "BAJA": "Low",
    "BOMBA": "Pump",
    "CALEFACCION": "Heating",
    "CALEFACTOR": "Heater",
    "CARGA": "Loading",
    "CAUDAL": "Yield",
    "CHILLER": "Chiller",
    "CIRCUITOS": "Circuits",
    "COMANDO": "Command",
    "COMPRESOR": "Compressor",
    "CONSIGNA": "Setpoint",
    "COOLING": "Cooling",
    "DAMPER": "Damper",
    "DAY": "Day",
    " DE ": " Of",
    "DESHUMIDIFICADOR": "Dehumidifier",
    "DISPONIBLE": "Available",
    "ENCENDIDO": "Started",
    "ESTADO": "State",
    "ETAPA": "Stage",
    "EVAPORADOR": "Evaparator",
    "EXTERIOR": "Exterior",
    "FALLA": "Error",
    "FILTRO": "Filter",
    "FRIA": "Cold",
    "FRIO": "Cold",
    "FUNCIONAMIENTO": "Working",
    "FUNCIONANDO": "Functioning",
    "GENERAL": "General",
    "HEATING": "Heating",
    "HORAS": "Hours",
    "HUMEDAD": "Humidity",
    "HUMIDIFICADOR": "Humidifier",
    "HUMIFICADOR": "Humidifier",  # typo should be fixed by DATControl
    "IMPULSION": "Impulse",
    "INYECCION": "Injection",
    "LOWER": "Lower",
    "MANEJADRA": "Manager",  # typo should be fixed by DATControl
    "MANEJADORA": "Manager",
    "MAX": "Max",
    "MODO": "Mode",
    "MIN": "Min",
    "NIGHT": "Night",
    "NUMERO": "Number",
    "OPERACION": "Operation",
    "PERC": "Percentage",
    "PISO": "Floor",
    "POTENCIA": "Power",
    "PRESENCIA": "Presense",
    "PRESION": "Pressure",
    "PROMEDIO": "Mean",
    "RESET": "Reset",
    "RETORNO": "Return",
    "REQUERIMIENTO": "Requirement",
    "SALA": "Room",
    "SBLANCA": "White Room",  # Not sure if this is an abbreviation of SALA BLANCA
    "SELECTOR": "Switch",
    "SETPOINT": "Setpoint",
    "SET POINT": "Setpoint",
    "TEMPERATURA": "Temperature",
    "TERMICA": "Thermal",
    "TRABAJO": "Work",
    "UNIDAD": "Unit",
    "VALOR": "Value",
    "VALVULA": "Valve",
    "VENT": "Vent",
    "VENTILADOR": "Fan",
    "VENT ILADOR": "Fan",  # typo should be fixed by DATControl
    "Vent ILADOR": "Fan",  # typo should be fixed by DATControl
    "ZONA": "Zone",
}


class HvacTopic(Enum):
    bombaAguaFriaP01 = "LSST/PISO01/BOMBA_AGUA_FRIA"
    chiller01P01 = "LSST/PISO01/CHILLER_01"
    chiller02P01 = "LSST/PISO01/CHILLER_02"
    chiller03P01 = "LSST/PISO01/CHILLER_03"
    crack01P02 = "LSST/PISO02/CRACK01"
    crack02P02 = "LSST/PISO02/CRACK02"
    fancoil01P02 = "LSST/PISO02/FANCOIL01"
    fancoil02P02 = "LSST/PISO02/FANCOIL02"
    fancoil03P02 = "LSST/PISO02/FANCOIL03"
    fancoil04P02 = "LSST/PISO02/FANCOIL04"
    fancoil05P02 = "LSST/PISO02/FANCOIL05"
    fancoil06P02 = "LSST/PISO02/FANCOIL06"
    fancoil07P02 = "LSST/PISO02/FANCOIL07"
    fancoil08P02 = "LSST/PISO02/FANCOIL08"
    fancoil09P02 = "LSST/PISO02/FANCOIL09"
    fancoil10P02 = "LSST/PISO02/FANCOIL10"
    fancoil11P02 = "LSST/PISO02/FANCOIL11"
    fancoil12P02 = "LSST/PISO02/FANCOIL12"
    generalP01 = "LSST/PISO01/GENERAL"
    manejadoraLower01P05 = "LSST/PISO05/MANEJADORA/LOWER_01"
    manejadoraLower02P05 = "LSST/PISO05/MANEJADORA/LOWER_02"
    manejadoraLower03P05 = "LSST/PISO05/MANEJADORA/LOWER_03"
    manejadoraLower04P05 = "LSST/PISO05/MANEJADORA/LOWER_04"
    manejadoraSblancaP04 = "LSST/PISO04/MANEJADORA/GENERAL/SBLANCA"
    manejadoraSlimpiaP04 = "LSST/PISO04/MANEJADORA/GENERAL/SLIMPIA"
    valvulaP01 = "LSST/PISO01/VALVULA"
    vea01P01 = "LSST/PISO01/VEA_01"
    vea01P05 = "LSST/PISO05/VEA_01"
    vea08P05 = "LSST/PISO05/VEA_08"
    vea09P05 = "LSST/PISO05/VEA_09"
    vea10P05 = "LSST/PISO05/VEA_10"
    vea11P05 = "LSST/PISO05/VEA_11"
    vea12P05 = "LSST/PISO05/VEA_12"
    vea13P05 = "LSST/PISO05/VEA_13"
    vea14P05 = "LSST/PISO05/VEA_14"
    vea15P05 = "LSST/PISO05/VEA_15"
    vea16P05 = "LSST/PISO05/VEA_16"
    vea17P05 = "LSST/PISO05/VEA_17"
    vec01P01 = "LSST/PISO01/VEC_01"
    vin01P01 = "LSST/PISO01/VIN_01"
    vex03LowerP04 = "LSST/PISO04/VEX_03/DAMPER_LOWER/GENERAL"
    vex04CargaP04 = "LSST/PISO04/VEX_04/ZONA_CARGA/GENERAL"


class TelemetryItem(Enum):
    alarmaFiltro = "ALARMA_FILTRO"
    alarmaGeneral = "ALARMA_GENERAL"
    calefaccionEtapa01 = "CALEFACCION_ETAPA_01"
    calefaccionEtapa02 = "CALEFACCION_ETAPA_02"
    caudalVentiladorImpulsion = "CAUDAL_VENTILADOR_IMPULSION"
    comando = "COMANDO"
    comandoEncendido = "COMANDO_ENCENDIDO"
    compresor01Alarmado = "COMPRESOR_01_ALARMADO"
    compresor01Funcionando = "COMPRESOR_01_FUNCIONANDO"
    compresor02Alarmado = "COMPRESOR_02_ALARMADO"
    compresor02Funcionando = "COMPRESOR_02_FUNCIONANDO"
    compresor03Alarmado = "COMPRESOR_03_ALARMADO"
    compresor03Funcionando = "COMPRESOR_03_FUNCIONANDO"
    compresor04Alarmado = "COMPRESOR_04_ALARMADO"
    compresor04Funcionando = "COMPRESOR_04_FUNCIONANDO"
    estadoCalefactor = "ESTADO_CALEFACTOR"
    estadoDamper = "ESTADO_DAMPER"
    estadoFuncionamiento = "ESTADO_FUNCIONAMIENTO"
    estadoOperacion = "ESTADO_OPERACION"
    estadoPresenciaAlarma = "ESTADO_PRESENCIA_ALARMA"
    estadoSelector = "ESTADO_SELECTOR"
    estadoTemperaturaAmbiente = "ESTADO_TEMPERATURA_AMBIENTE"
    estadoTemperaturaAnticongelante = "ESTADO_TEMPERATURA_ANTICONGELANTE"
    estadoTemperaturaExterior = "ESTADO_TEMPERATURA_EXTERIOR"
    estadoUnidad = "ESTADO_UNIDAD"
    estadoValvula = "ESTADO_VALVULA"
    estadoValvula03 = "ESTADO_VALVULA_03"
    estadoValvula04 = "ESTADO_VALVULA_04"
    estadoValvula05 = "ESTADO_VALVULA_05"
    estadoValvula06 = "ESTADO_VALVULA_06"
    estadoValvula12 = "ESTADO_VALVULA_1&2"
    estadoVentilador = "ESTADO_VENTILADOR"
    estadoDeUnidad = "ESTADO_DE_UNIDAD"
    fallaTermica = "FALLA_TERMICA"
    horasCompresor01 = "HORAS_COMPRESOR_01"
    horasCompresor02 = "HORAS_COMPRESOR_02"
    horasCompresor03 = "HORAS_COMPRESOR_03"
    horasCompresor04 = "HORAS_COMPRESOR_04"
    horasCompresorPromedio = "HORAS_COMPRESOR_PROMEDIO"
    modoOperacion = "MODO_OPERACION"
    modoOperacionUnidad = "MODO_OPERACION_UNIDAD"
    numeroCircuitos = "NUMERO_CIRCUITOS"
    percAperturaValvula = "%_APERTURA_VALVULA"
    percAperturaValvulaFrio = "%_APERTURA_VALVULA_FRIO"
    percHumedadSala = "%_HUMEDAD_SALA"
    percPotenciaTrabajo = "%_POTENCIA_TRABAJO"
    potenciaDisponibleChiller = "POTENCIA_DISPONIBLE_CHILLER"
    presionBajaCto1 = "PRESION_BAJA_CTO1"
    presionBajaCto2 = "PRESION_BAJA_CTO2"
    requerimientoHumidificador = "REQUERIMIENTO_HUMIDIFICADOR"
    resetAlarma = "RESET_ALARMA"
    setPointCooling = "SET_POINT_COOLING"
    setPointHeating = "SET_POINT_HEATING"
    setPointVentImpulsion = "SET_POINT_VENT_IMPULSION"
    setpointActivo = "SETPOINT_ACTIVO"
    setpointCoolingDay = "SETPOINT_COOLING_DAY"
    setpointCoolingNight = "SETPOINT_COOLING_NIGHT"
    setpointDeshumidificador = "SETPOINT_DESHUMIDIFICADOR"
    setpointHeatingDay = "SETPOINT_HEATING_DAY"
    setpointHeatingNight = "SETPOINT_HEATING_NIGHT"
    setpointHumidificador = "SETPOINT_HUMIDIFICADOR"
    setpointTrabajo = "SETPOINT_TRABAJO"
    setpointVentiladorMax = "SETPOINT_VENTILADOR_MAX"
    setpointVentiladorMin = "SETPOINT_VENTILADOR_MIN"
    temperaturaAguaImpulsionEvaporador = "TEMPERATURA_AGUA_IMPULSION_EVAPORADOR"
    temperaturaAguaRetornoEvaporador = "TEMPERATURA_AGUA_RETORNO_EVAPORADOR"
    temperaturaAmbiente = "TEMPERATURA_AMBIENTE"
    temperaturaAmbienteExterior = "TEMPERATURA_AMBIENTE&EXTERIOR"
    temperaturaAnticongelante = "TEMPERATURA_ANTICONGELANTE"
    temperaturaInyeccion = "TEMPERATURA_INYECCION"
    temperaturaRetorno = "TEMPERATURA_RETORNO"
    temperaturaSala = "TEMPERATURA_SALA"
    valorConsigna = "VALOR_CONSIGNA"


class CommandItem(Enum):
    comandoEncendido = "COMANDO_ENCENDIDO_LSST"
    percAperturaValvulaFrio = "%_APERTURA_VALVULA_FRIO_LSST"
    setPointCooling = "SET_POINT_COOLING_LSST"
    setPointHeating = "SET_POINT_HEATING_LSST"
    setpointActivo = "SETPOINT_ACTIVO_LSST"
    setpointCoolingDay = "SETPOINT_COOLING_DAY_LSST"
    setpointCoolingNight = "SETPOINT_COOLING_NIGHT_LSST"
    setpointDeshumidificador = "SETPOINT_DESHUMIDIFICADOR_LSST"
    setpointHeatingDay = "SETPOINT_HEATING_DAY_LSST"
    setpointHeatingNight = "SETPOINT_HEATING_NIGHT_LSST"
    setpointHumidificador = "SETPOINT_HUMIDIFICADOR_LSST"
    setpointTrabajo = "SETPOINT_TRABAJO_LSST"
    setpointVentiladorMax = "SETPOINT_VENTILADOR_MAX_LSST"
    setpointVentiladorMin = "SETPOINT_VENTILADOR_MIN_LSST"
    temperaturaAnticongelante = "TEMPERATURA_ANTICONGELANTE_LSST"
    valorConsigna = "VALOR_CONSIGNA_LSST"
