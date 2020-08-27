__all__ = [
    "BombaAguaFriaP01",
    "Chiller01P01",
    "Crack01P02",
    "DamperLowerP04",
    "Fancoil01P02",
    "ManejadoraLower01P05",
    "ManejadoraSblancaP04",
    "ManejadoraSlimpiaP04",
    "ManejadoraZzzP04",
    "ManejadraSblancaP04",
    "TemperatuaAmbienteP01",
    "ValvulaP01",
    "Vea01P01",
    "Vea01P05",
    "Vea03P04",
    "Vea04P04",
    "Vea08P05",
    "Vea09P05",
    "Vea10P05",
    "Vea11P05",
    "Vea12P05",
    "Vea13P05",
    "Vea14P05",
    "Vea15P05",
    "Vea16P05",
    "Vea17P05",
    "Vec01P01",
    "Vex03P04",
    "Vex04P04",
    "Vin01P01",
    "ZonaCargaP04",
]

import random


class BombaAguaFriaP01:
    """Class holding the HVAC_bombaAguaFriaP01 telemetry status for the
    simulator.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.comandoEncendido = False

    async def update_status(self):
        # Nothing to be done here though for completeness sake I keep the
        # method. Also, in the near future additional fields may be added.
        pass


class Chiller01P01:
    """Class holding the HVAC_chiller01P01 telemetry status.
    """

    def __init__(self):
        self.comandoEncendido = False
        self.compresor01Funcionando = False
        self.compresor02Funcionando = False
        self.compresor03Funcionando = False
        self.compresor04Funcionando = False
        self.setpointActivo = -99.99
        self.temperaturaAguaRetornoEvaporador = -99.99
        self.temperaturaAguaImpulsionEvaporador = -99.99
        self.presionBajaCto1 = -99.99
        self.presionBajaCto2 = -99.99
        self.potenciaDisponibleChiller = -99.99
        self.potenciaTrabajo = -99.99
        self.estadoFuncionamiento = -99.99
        self.modoOperacion = -99.99
        self.estadoUnidad = -99.99
        self.horasCompresorPromedio = -99.99
        self.horasCompresor01 = -99.99
        self.horasCompresor02 = -99.99
        self.horasCompresor03 = -99.99
        self.horasCompresor04 = -99.99
        self.compresor01Alarmado = -99.99
        self.compresor02Alarmado = -99.99
        self.compresor03Alarmado = -99.99
        self.compresor04Alarmado = -99.99
        self.alarmaGeneral = -99.99

    async def update_status(self):
        if self.comandoEncendido:
            self.compresor01Funcionando = self.comandoEncendido
            self.compresor02Funcionando = self.comandoEncendido
            self.compresor03Funcionando = self.comandoEncendido
            self.compresor04Funcionando = self.comandoEncendido
            self.temperaturaAguaImpulsionEvaporador = random.randint(180, 220) / 10.0
            self.temperaturaAguaRetornoEvaporador = random.randint(180, 220) / 10.0
            self.presionBajaCto1 = random.randint(450, 550) / 10.0
            self.presionBajaCto2 = random.randint(450, 550) / 10.0
            self.potenciaDisponibleChiller = random.randint(450, 550) / 10.0
            self.potenciaTrabajo = random.randint(450, 550) / 10.0
            self.estadoFuncionamiento = random.randint(450, 550) / 10.0
            self.modoOperacion = random.randint(450, 550) / 10.0
            self.estadoUnidad = random.randint(450, 550) / 10.0
            self.horasCompresorPromedio = random.randint(450, 550) / 10.0
            self.horasCompresor01 = random.randint(450, 550) / 10.0
            self.horasCompresor02 = random.randint(450, 550) / 10.0
            self.horasCompresor03 = random.randint(450, 550) / 10.0
            self.horasCompresor04 = random.randint(450, 550) / 10.0
            self.compresor01Alarmado = random.randint(450, 550) / 10.0
            self.compresor02Alarmado = random.randint(450, 550) / 10.0
            self.compresor03Alarmado = random.randint(450, 550) / 10.0
            self.compresor04Alarmado = random.randint(450, 550) / 10.0
            self.alarmaGeneral = random.randint(450, 550) / 10.0


class Crack01P02:
    """Class holding the HVAC_crack01P02 telemetry status.
    """

    def __init__(self):
        self.comandoEncendido = False
        self.estadoFuncionamiento = False
        self.estadoPresenciaAlarma = False
        self.temperaturaInyeccion = -99.99
        self.temperaturaRetorno = -99.99
        self.humedadSala = -99.99
        self.setpointHumidificador = -99.99
        self.setpointDeshumidificador = -99.99
        self.setPointCooling = -99.99
        self.setPointHeating = -99.99
        self.aperturaValvula = -99.99
        self.requerimientoHumificador = -99.99
        self.estadoDeUnidad = -99.99
        self.modoOperacionUnidad = -99.99
        self.numeroCircuitos = -99.99

    async def update_status(self):
        if self.comandoEncendido:
            self.estadoFuncionamiento = self.comandoEncendido
            self.estadoPresenciaAlarma = False
            self.temperaturaInyeccion = random.randint(180, 220) / 10.0
            self.temperaturaRetorno = random.randint(180, 220) / 10.0
            self.humedadSala = random.randint(450, 550) / 10.0
            self.aperturaValvula = random.randint(450, 550) / 10.0
            self.requerimientoHumificador = random.randint(450, 550) / 10.0
            self.estadoDeUnidad = random.randint(450, 550) / 10.0
            self.modoOperacionUnidad = random.randint(450, 550) / 10.0
            self.numeroCircuitos = random.randint(450, 550) / 10.0


class DamperLowerP04:
    """Class holding the HVAC_damperLowerP04 telemetry status.
    """

    def __init__(self):
        self.comando = False

    async def update_status(self):
        # Nothing to be done here though for completeness sake I keep the
        # method. Also, in the near future additional fields may be added.
        pass


class Fancoil01P02:
    """Class holding the HVAC_fancoil01P02 telemetry status.
    """

    def __init__(self):
        self.comandoEncendido = False
        self.temperaturaSala = False
        self.estadoOperacion = False
        self.estadoCalefactor = False
        self.estadoVentilador = False
        self.aperturaValvulaFrio = -99.99
        self.setpointCoolingDay = -99.99
        self.setpointHeatingDay = -99.99
        self.setpointCoolingNight = -99.99
        self.setpointHeatingNight = -99.99
        self.setpointTrabajo = -99.99

    async def update_status(self):
        if self.comandoEncendido:
            self.temperaturaSala = self.comandoEncendido
            self.estadoOperacion = self.comandoEncendido
            self.estadoCalefactor = self.comandoEncendido
            self.estadoVentilador = self.comandoEncendido


class ManejadoraLower01P05:
    """Class holding the HVAC_manejadoraLower01P05 telemetry status.
    """

    def __init__(self):
        self.alarmaGeneral = False
        self.alarmaFiltro = False
        self.estadoFuncionamiento = False
        self.estadoDamper = False
        self.resetAlarma = False
        self.temperaturaAmbienteExterior = False
        self.estadoValvula = False
        self.caudalVentiladorImpulsion = False
        self.comandoEncendido = False
        self.valorConsigna = -99.99
        self.setpointTrabajo = -99.99
        self.setpointVentiladorMin = -99.99
        self.setpointVentiladorMax = -99.99
        self.setPointVentImpulsion = -99.99
        self.temperaturaAnticongelante = -99.99
        self.temperaturaInyeccion = -99.99
        self.temperaturaRetorno = -99.99

    async def update_status(self):
        if self.comandoEncendido:
            self.alarmaGeneral = False
            self.alarmaFiltro = False
            self.estadoFuncionamiento = self.comandoEncendido
            self.estadoDamper = self.comandoEncendido
            self.resetAlarma = False
            self.temperaturaAmbienteExterior = False
            self.caudalVentiladorImpulsion = False
            self.estadoValvula = self.comandoEncendido
            self.valorConsigna = random.randint(450, 550) / 10.0
            self.setPointVentImpulsion = random.randint(450, 550) / 10.0
            self.temperaturaInyeccion = random.randint(180, 220) / 10.0
            self.temperaturaRetorno = random.randint(180, 220) / 10.0


class ManejadoraSblancaP04:
    """Class holding the HVAC_manejadoraSblancaP04 telemetry status.
    """

    def __init__(self):
        self.alarmaGeneral = False
        self.alarmaFiltro = False
        self.resetAlarma = False
        self.estadoValvula = False
        self.calefaccionEtapa01 = False
        self.calefaccionEtapa02 = False
        self.comandoEncendido = False
        self.estadoFuncionamiento = False
        self.valorConsigna = -99.99
        self.estadoTemperaturaExterior = -99.99
        self.estadoTemperaturaAnticongelante = -99.99
        self.setpointTrabajo = -99.99
        self.temperaturaInyeccion = -99.99
        self.temperaturaRetorno = -99.99
        self.caudalVentiladorImpulsion = -99.99
        self.setpointVentiladorMin = -99.99
        self.setpointVentiladorMax = -99.99
        self.temperaturaSala = -99.99

    async def update_status(self):
        if self.comandoEncendido:
            self.alarmaGeneral = False
            self.alarmaFiltro = False
            self.resetAlarma = False
            self.estadoValvula = self.comandoEncendido
            self.calefaccionEtapa01 = self.comandoEncendido
            self.calefaccionEtapa02 = self.comandoEncendido
            self.estadoFuncionamiento = self.comandoEncendido
            self.estadoTemperaturaExterior = random.randint(450, 550) / 10.0
            self.estadoTemperaturaAnticongelante = random.randint(450, 550) / 10.0
            self.setpointTrabajo = random.randint(450, 550) / 10.0
            self.temperaturaInyeccion = random.randint(180, 220) / 10.0
            self.temperaturaRetorno = random.randint(180, 220) / 10.0
            self.caudalVentiladorImpulsion = random.randint(450, 550) / 10.0
            self.temperaturaSala = random.randint(180, 220) / 10.0


class ManejadraSblancaP04:
    """Class holding the HVAC_manejadraSblancaP04 telemetry status.
    """

    def __init__(self):
        self.estadoTemperaturaAmbiente = -99.99

    async def update_status(self):
        self.estadoTemperaturaAmbiente = random.randint(180, 220) / 10.0


class ManejadoraSlimpiaP04:
    """Class holding the HVAC_manejadoraSlimpiaP04 telemetry status.
    """

    def __init__(self):
        self.temperaturaSala = -99.99

    async def update_status(self):
        self.temperaturaSala = random.randint(180, 220) / 10.0


class ManejadoraZzzP04:
    """Class holding the HVAC_manejadoraZzzP04 telemetry status.
    """

    def __init__(self):
        self.ai4 = -99.99
        self.ai5 = -99.99

    async def update_status(self):
        self.ai4 = random.randint(180, 220) / 10.0
        self.ai5 = random.randint(180, 220) / 10.0


class TemperatuaAmbienteP01:
    """Class holding the HVAC_temperatuaAmbienteP01 telemetry status.
    """

    def __init__(self):
        self.temperaturaAmbiente = -99.99

    async def update_status(self):
        self.temperaturaAmbiente = random.randint(180, 220) / 10.0


class ValvulaP01:
    """Class holding the HVAC_valvulaP01 telemetry status.
    """

    def __init__(self):
        self.estadoValvula12 = False
        self.estadoValvula03 = False
        self.estadoValvula04 = False
        self.estadoValvula05 = False
        self.estadoValvula06 = False

    async def update_status(self):
        self.estadoValvula12 = False
        self.estadoValvula03 = False
        self.estadoValvula04 = False
        self.estadoValvula05 = False
        self.estadoValvula06 = False


class Vea01P01:
    """Class holding the HVAC_vea01P01 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.estadoSelector = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.estadoFuncionamiento = self.comandoEncendido
            self.estadoSelector = self.comandoEncendido


class Vea01P05:
    """Class holding the HVAC_vea01P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea08P05:
    """Class holding the HVAC_vea08P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea09P05:
    """Class holding the HVAC_vea09P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea10P05:
    """Class holding the HVAC_vea10P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea11P05:
    """Class holding the HVAC_vea11P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea12P05:
    """Class holding the HVAC_vea12P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea13P05:
    """Class holding the HVAC_vea13P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea14P05:
    """Class holding the HVAC_vea14P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea15P05:
    """Class holding the HVAC_vea15P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea16P05:
    """Class holding the HVAC_vea16P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea17P05:
    """Class holding the HVAC_vea17P05 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False
            self.estadoFuncionamiento = self.comandoEncendido


class Vea03P04:
    """Class holding the HVAC_vea03P04 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False

    async def update_status(self):
        # Nothing to be done here though for completeness sake I keep the
        # method. Also, in the near future additional fields may be added.
        pass


class Vea04P04:
    """Class holding the HVAC_vea04P04 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False

    async def update_status(self):
        # Nothing to be done here though for completeness sake I keep the
        # method. Also, in the near future additional fields may be added.
        pass


class Vec01P01:
    """Class holding the HVAC_vec01P01 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.estadoSelector = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.estadoFuncionamiento = self.comandoEncendido
            self.estadoSelector = False


class Vex03P04:
    """Class holding the HVAC_vex03P04 telemetry status.
    """

    def __init__(self):
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False


class Vex04P04:
    """Class holding the HVAC_vex04P04 telemetry status.
    """

    def __init__(self):
        self.fallaTermica = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.fallaTermica = False


class Vin01P01:
    """Class holding the HVAC_vin01P01 telemetry status.
    """

    def __init__(self):
        self.estadoFuncionamiento = False
        self.estadoSelector = False
        self.comandoEncendido = False

    async def update_status(self):
        if self.comandoEncendido:
            self.estadoFuncionamiento = self.comandoEncendido
            self.estadoSelector = False


class ZonaCargaP04:
    """Class holding the HVAC_zonaCargaP04 telemetry status.
    """

    def __init__(self):
        self.comandoEncendido = False

    async def update_status(self):
        # Nothing to be done here though for completeness sake I keep the
        # method. Also, in the near future additional fields may be added.
        pass
