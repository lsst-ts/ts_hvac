from enum import Enum

dictionary = {
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


class Escape(Enum):
    BARRAOBL = "/"
    PCTO = "%"
    GUION = "-"
    AMPER = "&"
    ESPACIO = " "
