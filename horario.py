"""Clase Horario: franja semanal de una hora en la que un médico atiende."""
from medico import Medico
from constantes import DIAS_SEMANA, HORA_INICIO, HORA_FIN


class Horario:
    """Cada Horario pertenece a un único Medico (1 médico - 1..* horarios)."""

    def __init__(self, dia, hora, medico, disponibilidad=True):
        self.dia = dia
        self.hora = hora
        self.medico = medico
        self.disponibilidad = disponibilidad

    @property
    def dia(self):
        return self.__dia

    @dia.setter
    def dia(self, valor):
        texto = str(valor).strip().capitalize()
        if texto not in DIAS_SEMANA:
            raise ValueError(f"El día debe ser uno de {DIAS_SEMANA}.")
        self.__dia = texto

    @property
    def hora(self):
        return self.__hora

    @hora.setter
    def hora(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError("La hora debe ser un número entero.")
        if not HORA_INICIO <= valor <= HORA_FIN:
            raise ValueError(f"La hora debe estar entre {HORA_INICIO} y {HORA_FIN}.")
        self.__hora = valor

    @property
    def disponibilidad(self):
        return self.__disponibilidad

    @disponibilidad.setter
    def disponibilidad(self, valor):
        if not isinstance(valor, bool):
            raise ValueError("La disponibilidad debe ser True o False.")
        self.__disponibilidad = valor

    @property
    def medico(self):
        return self.__medico

    @medico.setter
    def medico(self, valor):
        if not isinstance(valor, Medico):
            raise ValueError("El horario debe pertenecer a un objeto Medico.")
        self.__medico = valor

    def __str__(self):
        estado = "disponible" if self.disponibilidad else "no disponible"
        return f"{self.dia} {self.hora:02d}:00 ({estado})"
