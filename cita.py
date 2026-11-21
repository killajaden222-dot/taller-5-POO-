"""Clase Cita: une a un Medico y un Paciente en una fecha y hora."""
from datetime import date, datetime, time
from medico import Medico
from paciente import Paciente
from constantes import TIPOS_CITA, nombre_dia


class Cita:
    """Asociación entre Medico y Paciente (cada cita tiene exactamente uno de cada uno)."""

    def __init__(self, medico, paciente, fecha=None, hora=None,
                 tipo="General", num_consultorio="NA"):
        self.medico = medico
        self.paciente = paciente
        # Valores por defecto del diagrama: fecha = hoy(), hora = ahora().
        self.fecha = fecha if fecha is not None else date.today()
        self.hora = hora if hora is not None else datetime.now().time().replace(
            second=0, microsecond=0)
        self.tipo = tipo
        self.num_consultorio = num_consultorio

    @staticmethod
    def tipo_para_especialidad(especialidad):
        """Deduce el tipo de cita a partir de la especialidad del médico."""
        esp = especialidad.strip().lower()
        if esp in ("medicina general", "general"):
            return "General"
        if esp in ("odontología", "odontologia"):
            return "Odontología"
        return "Especialista"

    # ------------------------------------------------- getters y setters
    @property
    def medico(self):
        return self.__medico

    @medico.setter
    def medico(self, valor):
        if not isinstance(valor, Medico):
            raise ValueError("La cita requiere un objeto Medico.")
        self.__medico = valor

    @property
    def paciente(self):
        return self.__paciente

    @paciente.setter
    def paciente(self, valor):
        if not isinstance(valor, Paciente):
            raise ValueError("La cita requiere un objeto Paciente.")
        self.__paciente = valor

    @property
    def fecha(self):
        return self.__fecha

    @fecha.setter
    def fecha(self, valor):
        if isinstance(valor, datetime):
            valor = valor.date()
        if not isinstance(valor, date):
            raise ValueError("La fecha debe ser un objeto date.")
        self.__fecha = valor

    @property
    def hora(self):
        return self.__hora

    @hora.setter
    def hora(self, valor):
        if not isinstance(valor, time):
            raise ValueError("La hora debe ser un objeto time.")
        self.__hora = valor

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, valor):
        if valor not in TIPOS_CITA:
            raise ValueError(f"El tipo de cita debe ser uno de {TIPOS_CITA}.")
        self.__tipo = valor

    @property
    def num_consultorio(self):
        return self.__num_consultorio

    @num_consultorio.setter
    def num_consultorio(self, valor):
        if str(valor).strip().upper() == "NA":
            self.__num_consultorio = "NA"
            return
        texto = str(valor).strip()
        if not (texto.isdigit() and int(texto) > 0):
            raise ValueError("El consultorio debe ser un entero positivo o 'NA'.")
        self.__num_consultorio = int(texto)

    # ------------------------------------------------ consultas del diagrama
    def consultar_medico(self):
        return self.__medico

    def consultar_paciente(self):
        return self.__paciente

    def __str__(self):
        return (f"{nombre_dia(self.fecha)} {self.fecha:%d/%m/%Y} "
                f"{self.hora:%H:%M} | {self.tipo} | "
                f"{self.paciente.nombres} con Dr(a). {self.medico.nombres}")
