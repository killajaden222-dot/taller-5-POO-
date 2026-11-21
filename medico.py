"""Clase Medico: hereda de Persona y administra horarios, pacientes y citas."""
from persona import Persona
from constantes import (DIAS_SEMANA, HORA_INICIO, HORA_FIN, TIPOS_MEDICO,
                        nombre_dia)


class Medico(Persona):
    """Médico del centro. Relaciones: 1..* Horario, 1..* Cita y 1..* Paciente."""

    # Porcentaje de bonificación anual según el tipo de vinculación.
    BONIFICACION_ANUAL = {"Titular": 0.10, "Interino": 0.05, "Sustituto": 0.0}

    def __init__(self, identificacion, nombres, annio_nac, mes_nac, dia_nac,
                 genero, direccion, codigo_postal, tipo_medico, especialidad,
                 sueldo):
        super().__init__(identificacion, nombres, annio_nac, mes_nac, dia_nac,
                         genero, direccion, codigo_postal)
        if self.edad < Persona.MAYORIA_EDAD:
            raise ValueError("Un médico debe ser mayor de edad.")
        self.tipo_medico = tipo_medico
        self.especialidad = especialidad
        self.sueldo = sueldo
        self.__citas = []       # asociación 1..* con Cita
        self.__pacientes = []   # asociación 1..* con Paciente ("Atiende")
        self.__horarios = []    # asociación 1..* con Horario ("Tiene")

    # ------------------------------------------------- getters y setters
    @property
    def tipo_medico(self):
        return self.__tipo_medico

    @tipo_medico.setter
    def tipo_medico(self, valor):
        texto = str(valor).strip().capitalize()
        if texto not in TIPOS_MEDICO:
            raise ValueError(f"El tipo de médico debe ser uno de {TIPOS_MEDICO}.")
        self.__tipo_medico = texto

    @property
    def especialidad(self):
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, valor):
        self.__especialidad = self._texto_obligatorio(valor, "La especialidad")

    @property
    def sueldo(self):
        return self.__sueldo

    @sueldo.setter
    def sueldo(self, valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError("El sueldo debe ser un número.") from None
        if numero <= 0:
            raise ValueError("El sueldo debe ser mayor que cero.")
        self.__sueldo = numero

    @property
    def citas(self):
        return list(self.__citas)  # copia: la lista interna no se expone

    @citas.setter
    def citas(self, valor):
        from cita import Cita
        if not isinstance(valor, list) or not all(
                isinstance(c, Cita) and c.medico is self for c in valor):
            raise ValueError("'citas' debe ser una lista de Cita de este médico.")
        self.__citas = list(valor)

    @property
    def pacientes(self):
        return list(self.__pacientes)

    @pacientes.setter
    def pacientes(self, valor):
        from paciente import Paciente
        if not isinstance(valor, list) or not all(isinstance(p, Paciente) for p in valor):
            raise ValueError("'pacientes' debe ser una lista de Paciente.")
        self.__pacientes = list(valor)

    @property
    def horarios(self):
        return list(self.__horarios)

    @horarios.setter
    def horarios(self, valor):
        from horario import Horario
        if not isinstance(valor, list) or not all(
                isinstance(h, Horario) and h.medico is self for h in valor):
            raise ValueError("'horarios' debe ser una lista de Horario de este médico.")
        self.__horarios = list(valor)

    # ------------------------------------------------ gestión de relaciones
    def agregar_cita(self, cita):
        from cita import Cita  # importación diferida: evita dependencia circular
        if not isinstance(cita, Cita) or cita.medico is not self:
            raise ValueError("La cita no pertenece a este médico.")
        if cita not in self.__citas:
            self.__citas.append(cita)

    def quitar_cita(self, cita):
        if cita in self.__citas:
            self.__citas.remove(cita)

    def agregar_paciente(self, paciente):
        """Asocia un paciente a este médico, manteniendo consistentes ambos lados."""
        from paciente import Paciente
        if not isinstance(paciente, Paciente):
            raise ValueError("Solo se pueden asignar objetos Paciente.")
        anterior = paciente.medico
        if anterior is not None and anterior is not self:
            anterior.quitar_paciente(paciente)
        if paciente not in self.__pacientes:
            self.__pacientes.append(paciente)
        paciente.medico = self

    def quitar_paciente(self, paciente):
        if paciente in self.__pacientes:
            self.__pacientes.remove(paciente)
            if paciente.medico is self:
                paciente.medico = None

    def agregar_horario(self, horario):
        from horario import Horario
        if not isinstance(horario, Horario) or horario.medico is not self:
            raise ValueError("El horario no pertenece a este médico.")
        if any(h.dia == horario.dia and h.hora == horario.hora for h in self.__horarios):
            raise ValueError("El médico ya tiene ese horario registrado.")
        self.__horarios.append(horario)

    def generar_horarios(self, dias, hora_inicio=HORA_INICIO, hora_fin=HORA_FIN):
        """Crea un Horario por cada día y cada hora del rango (ambos extremos incluidos)."""
        from horario import Horario
        if hora_inicio > hora_fin:
            raise ValueError("La hora de inicio no puede ser mayor que la hora final.")
        for dia in dias:
            for hora in range(hora_inicio, hora_fin + 1):
                if not any(h.dia == dia and h.hora == hora for h in self.__horarios):
                    self.__horarios.append(Horario(dia, hora, self))

    # ------------------------------------------------ lógica del diagrama
    def verificar_disponibilidad(self, dia, hora=None):
        """Retorna la lista de Horario disponibles para un día (y una hora opcional)."""
        if dia not in DIAS_SEMANA:
            raise ValueError(f"El día debe ser uno de {DIAS_SEMANA}.")
        if hora is not None and not (HORA_INICIO <= hora <= HORA_FIN):
            raise ValueError(f"La hora debe estar entre {HORA_INICIO} y {HORA_FIN}.")
        libres = []
        for horario in self.__horarios:
            if horario.dia != dia or not horario.disponibilidad:
                continue
            if hora is None or horario.hora == hora:
                libres.append(horario)
        return libres

    def tiene_cita_en(self, fecha, hora):
        """True si ya existe una cita del médico en esa fecha y hora."""
        return any(c.fecha == fecha and c.hora.hour == hora for c in self.__citas)

    def horas_libres(self, fecha):
        """Horas del día que el médico atiende y que aún no tienen cita."""
        dia = nombre_dia(fecha)
        if dia == "Dom":
            return []
        horas = [h.hora for h in self.verificar_disponibilidad(dia)
                 if not self.tiene_cita_en(fecha, h.hora)]
        return sorted(horas)

    def calcular_sueldo_annio(self):
        """12 mensualidades más la bonificación anual según el tipo de médico."""
        factor = 1 + Medico.BONIFICACION_ANUAL[self.__tipo_medico]
        return round(self.__sueldo * 12 * factor, 2)

    # ------------------------------------------------ polimorfismo
    def cantidad_citas(self):
        return len(self.__citas)

    def describir(self):
        return (f"Dr(a). {super().describir()} | {self.tipo_medico} - "
                f"{self.especialidad} | pacientes: {len(self.__pacientes)}, "
                f"citas: {len(self.__citas)}")
