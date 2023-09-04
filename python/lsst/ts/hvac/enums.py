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

__all__ = [
    "DEVICE_GROUPS",
    "DEVICE_GROUP_IDS",
    "DYNALENE_EVENT_GROUP_DICT",
    "EVENT_TOPIC_DICT",
    "SPANISH_TO_ENGLISH_DICTIONARY",
    "TOPICS_ALWAYS_ENABLED",
    "TOPICS_WITHOUT_CONFIGURATION",
    "CommandItem",
    "DeviceIndex",
    "DynaleneDescription",
    "HvacTopic",
    "TelemetryItem",
    "TopicType",
]

from enum import Enum

from lsst.ts.idl.enums.HVAC import DeviceId, DynaleneState, DynaleneTankLevel

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
    "IMPULSION": "Impulse",
    "INYECCION": "Injection",
    "LOWER": "Lower",
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
    "SBLANCA": "White Room",
    "SELECTOR": "Switch",
    "SETPOINT": "Setpoint",
    "SET POINT": "Setpoint",
    "TEMPERATURA": "Temperature",
    "TERMICA": "Thermal",
    "TRABAJO": "Work",
    "UNIDAD": "Unit",
    "VALOR": "Value",
    "VALVULA": "Valve",
    "VENTILADOR": "Fan",
    "VENT": "Vent",
    "ZONA": "Zone",
}


# These topics are always enabled because there are no MQTT commands to enable
# or disable them.
TOPICS_ALWAYS_ENABLED = frozenset(
    (
        "LSST/PISO01/BOMBA_AGUA_FRIA",
        "LSST/PISO01/GENERAL",
        "LSST/PISO01/VALVULA",
        "LSST/PISO05/DYNALENE",
    )
)

# These topics don't have configuration items.
TOPICS_WITHOUT_CONFIGURATION = frozenset(
    (
        "LSST/PISO01/BOMBA_AGUA_FRIA",
        "LSST/PISO01/GENERAL",
        "LSST/PISO01/VALVULA",
        "LSST/PISO01/VEA_01",
        "LSST/PISO05/DYNALENE",
        "LSST/PISO05/VEA_01",
        "LSST/PISO05/VEA_08",
        "LSST/PISO05/VEA_09",
        "LSST/PISO05/VEA_10",
        "LSST/PISO05/VEA_11",
        "LSST/PISO05/VEA_12",
        "LSST/PISO05/VEA_13",
        "LSST/PISO05/VEA_14",
        "LSST/PISO05/VEA_15",
        "LSST/PISO05/VEA_16",
        "LSST/PISO05/VEA_17",
        "LSST/PISO01/VEC_01",
        "LSST/PISO01/VIN_01",
        "LSST/PISO04/VEX_03/DAMPER_LOWER/GENERAL",
        "LSST/PISO04/VEX_04/ZONA_CARGA/GENERAL",
    )
)


class HvacTopic(Enum):
    bombaAguaFriaP01 = "LSST/PISO01/BOMBA_AGUA_FRIA"
    chiller01P01 = "LSST/PISO01/CHILLER_01"
    chiller02P01 = "LSST/PISO01/CHILLER_02"
    chiller03P01 = "LSST/PISO01/CHILLER_03"
    crack01P02 = "LSST/PISO02/CRACK01"
    crack02P02 = "LSST/PISO02/CRACK02"
    dynaleneP05 = "LSST/PISO05/DYNALENE"
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
    aperturaValvula = "%_APERTURA_VALVULA"
    aperturaValvulaFrio = "%_APERTURA_VALVULA_FRIO"
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
    dynCH01LS01 = "DCH01LS01"
    dynCH01supFS01 = "DCH01supFS01"
    dynCH01supPS11 = "DCH01supPS11"
    dynCH01supTS05 = "DCH01supTS05"
    dynCH02LS02 = "DCH02LS02"
    dynCH02supFS02 = "DCH02supFS02"
    dynCH02supPS13 = "DCH02supPS13"
    dynCH02supTS07 = "DCH02supTS07"
    dynMainGridAlarm = "DynMainGridAlarm"
    dynMainGridAlarmCMD = "DynMainGridAlarmCMD"
    dynMainGridFailureFlag = "DynMainGridFailureFlag"
    dynSafeties = "Safeties"
    dynSafetyResetFlag = "DynSafetyResetFlag"
    dynState = "DynaleneState"
    dynTAalarm = "DynTAalarm"
    dynTAalarmCMD = "DynTAalarmCMD"
    dynTAalarmMonitor = "DynTAalarmMonitor"
    dynTankLevel = "DynTankLevel"
    dynTankLevelAlarmCMD = "DynTankLevelAlarmCMD"
    dynTMAalarm = "DynTMAalarm"
    dynTMAalarmCMD = "DynTMAalarmCMD"
    dynTMAalarmMonitor = "DynTMAalarmMonitor"
    dynTAretPS04 = "DynTAretPS04"
    dynTAretTS04 = "DynTAretTS04"
    dynTAsupFS04 = "DynTAsupFS04"
    dynTAsupPS03 = "DynTAsupPS03"
    dynTAsupTS03 = "DynTAsupTS03"
    dynTAtpd = "DynTAtpd"
    dynTMAtpd = "DynTMAtpd"
    dynTMAretPS02 = "DynTMAretPS02"
    dynTMAretTS02 = "DynTMAretTS02"
    dynTMAsupFS03 = "DynTMAsupFS03"
    dynTMAsupPS01 = "DynTMAsupPS01"
    dynTMAsupTS01 = "DynTMAsupTS01"
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
    horometro = "HOROMETRO"
    humedadSala = "%_HUMEDAD_SALA"
    modoOperacion = "MODO_OPERACION"
    modoOperacionUnidad = "MODO_OPERACION_UNIDAD"
    numeroCircuitos = "NUMERO_CIRCUITOS"
    potenciaDisponibleChiller = "POTENCIA_DISPONIBLE_CHILLER"
    potenciaTrabajo = "%_POTENCIA_TRABAJO"
    presionBajaCto1 = "PRESION_BAJA_CTO1"
    presionBajaCto2 = "PRESION_BAJA_CTO2"
    requerimientoHumidificador = "REQUERIMIENTO_HUMIDIFICADOR"
    resetAlarma = "RESET_ALARMA"
    setpointActivo = "SETPOINT_ACTIVO"
    setpointCooling = "SETPOINT_COOLING"
    setpointCoolingDay = "SETPOINT_COOLING_DAY"
    setpointCoolingNight = "SETPOINT_COOLING_NIGHT"
    setpointDeshumidificador = "SETPOINT_DESHUMIDIFICADOR"
    setpointHeating = "SETPOINT_HEATING"
    setpointHeatingDay = "SETPOINT_HEATING_DAY"
    setpointHeatingNight = "SETPOINT_HEATING_NIGHT"
    setpointHumidificador = "SETPOINT_HUMIDIFICADOR"
    setpointTrabajo = "SETPOINT_TRABAJO"
    setpointVentImpulsion = "SETPOINT_VENT_IMPULSION"
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
    dynCH01retCGLYpres = "DynCH01retCGLYpres"
    dynCH01retCGLYtemp = "DynCH01retCGLYtemp"
    dynCH01supCGLYpres = "DynCH01supCGLYpres"
    dynCH01supCGLYtemp = "DynCH01supCGLYtemp"
    dynCH02retGPGLYpres = "DynCH02retGPGLYpres"
    dynCH02retGPGLYtemp = "DynCH02retGPGLYtemp"
    dynCH02supGPGLYpres = "DynCH02supGPGLYpres"
    dynCH02supGPGLYtemp = "DynCH02supGPGLYtemp"
    dynCH1CGLYtpd = "DynCH1CGLYtpd"
    dynCH1supCGLYflow = "DynCH1supCGLYflow"
    dynCH2GPGLYtpd = "DynCH2GPGLYtpd"
    dynCH2supGPGLYflow = "DynCH2supGPGLYflow"
    dynTMAcmv01pos = "DynTMAcmv01pos"
    dynTMAcmv02pos = "DynTMAcmv02pos"
    dynSysFault = "DynSysFault"
    dynSysOK = "DynSysOK"
    dynSysWarning = "DynSysWarning"
    dynAmbientDeltaModeStatus = "DynAmbientDeltaModeStatus"
    dynExhaustAirBackupModeStatus = "DynExhaustAirBackupModeStatus"
    dynRemoteLocalModeStatus = "DynRemoteLocalModeStatus"
    exhAirAvrgTemp = "ExhAirAvrgTemp"


class DynaleneDescription(Enum):
    """Descriptions for the Dynalene telemetry items."""

    dynCH01LS01 = "Dynalene Tank Level on Chiller 01."
    dynCH01supFS01 = "Dynalene Chiller 01 supply flowrate."
    dynCH01supPS11 = "Dynalene Chiller 01 supply pressure."
    dynCH01supTS05 = "Dynalene Chiller 01 supply temperature."
    dynCH02LS02 = "Dynalene Tank Level on Chiller 02."
    dynCH02supFS02 = "Dynalene Chiller 02 supply flowrate ."
    dynCH02supPS13 = "Dynalene Chiller 02 supply pressure."
    dynCH02supTS07 = "Dynalene Chiller 02 supply temperature."
    # This next value is available in XML 16 but not before or after.
    dynSafeties = "Dynalene Safety State."

    # These next values are available from XML 17 on.
    dynMainGridAlarm = "Dynalene Main Grid Alarm State."
    dynMainGridAlarmCMD = "Dynalene Main Grid Alarm Command State."
    dynMainGridFailureFlag = "Dynalene Main Grid Failure Flag State."
    dynSafetyResetFlag = "Dynalene Safety Reset Flag State."
    dynTAalarm = "Dynalene TA Alarm State."
    dynTAalarmCMD = "Dynalene TA Alarm Command State."
    dynTAalarmMonitor = "Dynalene TA Alarm Monitor State."
    dynTankLevel = "Dynalene Tank Level Alarm State."
    dynTankLevelAlarmCMD = "Dynalene Tank Level Alarm Command State."
    dynTMAalarm = "Dynalene TMA Alarm State."
    dynTMAalarmCMD = "Dynalene TMA Alarm Command State."
    dynTMAalarmMonitor = "Dynalene TMA Alarm Monitor State."

    dynState = "Dynalene State."
    dynTAretPS04 = "Test Area Dynalene manifold supply pressure."
    dynTAretTS04 = "Test Area Dynalene manifold return temperature."
    dynTAsupFS04 = "Test Area Dynalene flowrate to L3 Manifold."
    dynTAsupPS03 = "Test Area Dynalene manifold supply pressure."
    dynTAsupTS03 = "Test Area Dynalene manifold supply temperature."
    dynTAtpd = "Thermal Power Dissipation on L3 Manifold."
    dynTMAtpd = "Thermal Power Dissipation on L6 Manifold."
    dynTMAretPS02 = "TMA Dynalene manifold supply pressure."
    dynTMAretTS02 = "TMA Dynalene manifold return temperature."
    dynTMAsupFS03 = "TMA Dynalene flowrate to L6 Manifold."
    dynTMAsupPS01 = "TMA Dynalene manifold supply pressure."
    dynTMAsupTS01 = "TMA Dynalene manifold supply temperature."
    dynCH01retCGLYpres = "Dynalene return glycol channel 1 pressure."
    dynCH01retCGLYtemp = "Dynalene return glycol channel 1 temperature."
    dynCH01supCGLYpres = "Dynalene supplied glycol channel 1 pressure."
    dynCH01supCGLYtemp = "Dynalene supplied glycol channel 1 temperature."
    dynCH02retGPGLYpres = "Dynalene return glycol channel 2 pressure."
    dynCH02retGPGLYtemp = "Dynalene return glycol channel 2 temperature."
    dynCH02supGPGLYpres = "Dynalene supplied glycol channel 2 pressure."
    dynCH02supGPGLYtemp = "Dynalene supplied glycol channel 2 temperature."
    dynCH1CGLYtpd = "Dynalene glycol channel 1 tpd."
    dynCH1supCGLYflow = "Dynalene supplied glycol channel 1 flow."
    dynCH2GPGLYtpd = "Dynalene glycol channel 2 tpd."
    dynCH2supGPGLYflow = "Dynalene supplied glycol channel 2 flow."
    dynTMAcmv01pos = "TMA Dynalene cmv01 position."
    dynTMAcmv02pos = "TMA Dynalene cmv02 position."
    dynSysFault = "Dynalene System Fault."
    dynSysOK = "Dynalene System OK."
    dynSysWarning = "Dynalene System Warning."
    dynAmbientDeltaModeStatus = "Dynalene Ambient Delta Mode Status."
    dynExhaustAirBackupModeStatus = "Dynalene Exhaust Air Backup Mode Status."
    dynRemoteLocalModeStatus = "Dynalene Remote Local Mode Status."
    exhAirAvrgTemp = "Exhaust Air Average Temp."

    # Dynalene commands.
    dynTmaRemoteSP = "TMA setpoint."
    dynTaRemoteSP = "TA setpoint."
    dynExtAirRemoteSP = "Exit air setpoint."
    dynCH1PressRemoteSP = "Chiller 1 pressure setpoint."
    dynCH2PressRemoteSP = "Chiller 2 pressure setpoint."
    dynSystOnOff = "Switch dynalene system on or off."
    dynTelemetryEnable = "Enable telemetry."
    dynPierFansOnOff = "Switch the pier fans on or off."


DYNALENE_EVENT_GROUP_DICT = {
    "DynTAalarmMonitorOFF": "DynTAalarmMonitor",
    "DynTAalarmMonitorON": "DynTAalarmMonitor",
    "DynTMAalarmMonitorOFF": "DynTMAalarmMonitor",
    "DynTMAalarmMonitorON": "DynTMAalarmMonitor",
    "DynTankLevelAlarm": "DynTankLevel",
    "DynTankLevelWarning": "DynTankLevel",
    "DynTankLevelOK": "DynTankLevel",
}


class CommandItem(Enum):
    comandoEncendido = "COMANDO_ENCENDIDO_LSST"
    aperturaValvulaFrio = "%_APERTURA_VALVULA_FRIO_LSST"
    dynCH1PressRemoteSP = "CH1PressRemoteSP"
    dynCH2PressRemoteSP = "CH2PressRemoteSP"
    dynSystOnOff = "DynSystOnOff"
    dynTaRemoteSP = "DynTaRemoteSP"
    dynTmaRemoteSP = "DynTmaRemoteSP"
    dynExtAirRemoteSP = "ExtAirRemoteSP"
    dynPierFansOnOff = "PierFansOnOff"
    dynTelemetryEnable = "TelemetryEnable"
    setpointActivo = "SETPOINT_ACTIVO_LSST"
    setpointCooling = "SETPOINT_COOLING_LSST"
    setpointCoolingDay = "SETPOINT_COOLING_DAY_LSST"
    setpointCoolingNight = "SETPOINT_COOLING_NIGHT_LSST"
    setpointDeshumidificador = "SETPOINT_DESHUMIDIFICADOR_LSST"
    setpointHeating = "SETPOINT_HEATING_LSST"
    setpointHeatingDay = "SETPOINT_HEATING_DAY_LSST"
    setpointHeatingNight = "SETPOINT_HEATING_NIGHT_LSST"
    setpointHumidificador = "SETPOINT_HUMIDIFICADOR_LSST"
    setpointTrabajo = "SETPOINT_TRABAJO_LSST"
    setpointVentiladorMax = "SETPOINT_VENTILADOR_MAX_LSST"
    setpointVentiladorMin = "SETPOINT_VENTILADOR_MIN_LSST"
    temperaturaAnticongelante = "TEMPERATURA_ANTICONGELANTE_LSST"
    valorConsigna = "VALOR_CONSIGNA_LSST"


class TopicType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"


# These topics cannot be distinguished from telemetry topics in the CSV file,
# so they get marked here to be emitted as events instead.
EVENT_TOPIC_DICT = (
    {
        "LSST/PISO05/DYNALENE/DynaleneState": {
            "topic": HvacTopic.dynaleneP05.name,
            "item": DynaleneDescription.dynState.name.replace("dyn", "dynalene"),
            "event": f"evt_{DynaleneDescription.dynState.name.replace('dyn', 'dynalene')}",
            "type": "enum",
            "enum": DynaleneState,
            "item_description": f"{DynaleneDescription.dynState.value.replace(' State.', ' state;')} "
            f"a DynaleneState enum.",
            "evt_description": f"{DynaleneDescription.dynState.value}",
        },
        "LSST/PISO05/DYNALENE/Safeties/DynTankLevel": {
            "topic": HvacTopic.dynaleneP05.name,
            "item": DynaleneDescription.dynTankLevel.name.replace("dyn", "dynalene"),
            "event": f"evt_{DynaleneDescription.dynTankLevel.name.replace('dyn', 'dynalene')}",
            "type": "enum",
            "enum": DynaleneTankLevel,
            "item_description": f"{DynaleneDescription.dynTankLevel.value.replace(' State.', ' state;')} "
            f"a DynaleneTankLevel enum.",
            "evt_description": f"{DynaleneDescription.dynTankLevel.value}",
        },
    }
    | {
        f"LSST/PISO05/DYNALENE/Safeties/{dyn_enum.name.replace('dyn', 'Dyn')}": {
            "topic": HvacTopic.dynaleneP05.name,
            "item": dyn_enum.name,
            "event": f"evt_{dyn_enum.name}",
            "type": "boolean",
            "item_description": f"{dyn_enum.value.replace(' State.', ' state;')} On (true) or Off (false).",
            "evt_description": f"{dyn_enum.value}",
        }
        for dyn_enum in [
            DynaleneDescription.dynTMAalarm,
            DynaleneDescription.dynTMAalarmCMD,
            DynaleneDescription.dynTMAalarmMonitor,
            DynaleneDescription.dynTAalarm,
            DynaleneDescription.dynTAalarmCMD,
            DynaleneDescription.dynTAalarmMonitor,
            DynaleneDescription.dynMainGridAlarm,
            DynaleneDescription.dynMainGridAlarmCMD,
            DynaleneDescription.dynMainGridFailureFlag,
            DynaleneDescription.dynTankLevelAlarmCMD,
            DynaleneDescription.dynSafetyResetFlag,
            DynaleneDescription.dynSysFault,
            DynaleneDescription.dynSysWarning,
            DynaleneDescription.dynSysOK,
        ]
    }
    | {
        f"LSST/PISO05/DYNALENE/Status/{dyn_enum.name.replace('dyn', 'Dyn')}": {
            "topic": HvacTopic.dynaleneP05.name,
            "item": dyn_enum.name,
            "event": f"evt_{dyn_enum.name}",
            "type": "boolean",
            "item_description": f"{dyn_enum.value.replace(' State.', ' state;')} On (true) or Off (false).",
            "evt_description": f"{dyn_enum.value}",
        }
        for dyn_enum in [
            DynaleneDescription.dynRemoteLocalModeStatus,
            DynaleneDescription.dynAmbientDeltaModeStatus,
            DynaleneDescription.dynExhaustAirBackupModeStatus,
        ]
    }
)

# Dict of index: DeviceId, where index is the index of the device in DeviceId.
# Used to understand the bits in the device_ids field of the deviceEnabled
# event.
DeviceIndex = {i: dev_id for i, dev_id in enumerate(DeviceId)}

# Dict grouping MQTT topics representing HVAC devices together.
DEVICE_GROUPS = {
    "CHILLER": [
        "LSST/PISO01/CHILLER_01",
        "LSST/PISO01/CHILLER_02",
        "LSST/PISO01/CHILLER_03",
    ],
    "CRACK": [
        "LSST/PISO02/CRACK01",
        "LSST/PISO02/CRACK02",
    ],
    "DYNALENE": ["LSST/PISO05/DYNALENE"],
    "FANCOIL": [
        "LSST/PISO02/FANCOIL01",
        "LSST/PISO02/FANCOIL02",
        "LSST/PISO02/FANCOIL03",
        "LSST/PISO02/FANCOIL04",
        "LSST/PISO02/FANCOIL05",
        "LSST/PISO02/FANCOIL06",
        "LSST/PISO02/FANCOIL07",
        "LSST/PISO02/FANCOIL08",
        "LSST/PISO02/FANCOIL09",
        "LSST/PISO02/FANCOIL10",
        "LSST/PISO02/FANCOIL11",
        "LSST/PISO02/FANCOIL12",
    ],
    "MANEJADORA_LOWER": [
        "LSST/PISO05/MANEJADORA/LOWER_01",
        "LSST/PISO05/MANEJADORA/LOWER_02",
        "LSST/PISO05/MANEJADORA/LOWER_03",
        "LSST/PISO05/MANEJADORA/LOWER_04",
    ],
    "MANEJADORA": [
        "LSST/PISO04/MANEJADORA/GENERAL/SBLANCA",
        "LSST/PISO04/MANEJADORA/GENERAL/SLIMPIA",
    ],
    "VEA": [
        "LSST/PISO05/VEA_01",
        "LSST/PISO05/VEA_08",
        "LSST/PISO05/VEA_09",
        "LSST/PISO05/VEA_10",
        "LSST/PISO05/VEA_11",
        "LSST/PISO05/VEA_12",
        "LSST/PISO05/VEA_13",
        "LSST/PISO05/VEA_14",
        "LSST/PISO05/VEA_15",
        "LSST/PISO05/VEA_16",
        "LSST/PISO05/VEA_17",
    ],
    "SALA_MAQUINAS": [
        "LSST/PISO01/VEA_01",
        "LSST/PISO01/VIN_01",
        "LSST/PISO01/VEC_01",
    ],
    "VEX": [
        "LSST/PISO04/VEX_03/DAMPER_LOWER/GENERAL",
        "LSST/PISO04/VEX_04/ZONA_CARGA/GENERAL",
    ],
}

# Dict assigning an ID to each device group. This is used in dictionary
# comprehension so it is better to keep it as a dict instead of an enum.
DEVICE_GROUP_IDS = {
    "CHILLER": 100,
    "CRACK": 200,
    "FANCOIL": 300,
    "MANEJADORA_LOWER": 400,
    "MANEJADORA": 500,
    "VEA": 600,
    "SALA_MAQUINAS": 700,
    "VEX": 800,
    "DYNALENE": 900,
}
