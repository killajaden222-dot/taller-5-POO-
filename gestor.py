"""CentroSalud: clase controladora que coordina las demás clases (la usa la GUI)."""
from datetime import date, datetime, time, timedelta
from paciente import Paciente
from medico import Medico
from cita import Cita
from constantes import nombre_dia


class CentroSalud:
    """Contiene las listas principales del sistema y aplica las reglas de negocio."""

    def __init__(self, nombre="Centro de Salud Giron"):
        self.__nombre = nombre
        self.__pacientes = []   # list[Paciente]
        self.__medicos = []     # list[Medico]
        self.__citas = []       # list[Cita]

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre del centro no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def pacientes(self):
        return list(self.__pacientes)

    @pacientes.setter
    def pacientes(self, valor):
        if not all(isinstance(p, Paciente) for p in valor):
            raise ValueError("Solo se admiten objetos Paciente.")
        self.__pacientes = list(valor)

    @property
    def medicos(self):
        return list(self.__medicos)

    @medicos.setter
    def medicos(self, valor):
        if not all(isinstance(m, Medico) for m in valor):
            raise ValueError("Solo se admiten objetos Medico.")
        self.__medicos = list(valor)

    @property
    def citas(self):
        return list(self.__citas)

    @citas.setter
    def citas(self, valor):
        if not all(isinstance(c, Cita) for c in valor):
            raise ValueError("Solo se admiten objetos Cita.")
        self.__citas = list(valor)

    # ------------------------------------------------------------ registros
    def registrar_paciente(self, paciente):
        if self.buscar_paciente(paciente.identificacion):
            raise ValueError("Ya existe un paciente con esa identificación.")
        self.__pacientes.append(paciente)

    def registrar_medico(self, medico):
        if self.buscar_medico(medico.identificacion):
            raise ValueError("Ya existe un médico con esa identificación.")
        self.__medicos.append(medico)

    def buscar_paciente(self, identificacion):
        for p in self.__pacientes:
            if p.identificacion == str(identificacion).strip():
                return p
        return None

    def buscar_medico(self, identificacion):
        for m in self.__medicos:
            if m.identificacion == str(identificacion).strip():
                return m
        return None

    # ----------------------------------------------------------------- citas
    def agendar_cita(self, paciente, medico, fecha, hora, num_consultorio="NA"):
        """Crea una cita si se cumplen todas las reglas; si no, lanza ValueError."""
        if paciente not in self.__pacientes or medico not in self.__medicos:
            raise ValueError("El paciente y el médico deben estar registrados.")
        ahora = datetime.now()
        if fecha < ahora.date() or (fecha == ahora.date() and hora <= ahora.hour):
            raise ValueError("No se pueden agendar citas en el pasado.")
        dia = nombre_dia(fecha)
        if dia == "Dom":
            raise ValueError("El centro no atiende los domingos.")
        if not medico.verificar_disponibilidad(dia, hora):
            raise ValueError(f"El médico no atiende los {dia} a las {hora:02d}:00.")
        if medico.tiene_cita_en(fecha, hora):
            raise ValueError("El médico ya tiene una cita en ese horario.")
        if paciente.tiene_cita_en(fecha, hora):
            raise ValueError("El paciente ya tiene una cita en ese horario.")

        tipo = Cita.tipo_para_especialidad(medico.especialidad)
        cita = Cita(medico, paciente, fecha, time(hora, 0), tipo, num_consultorio)
        paciente.agregar_cita(cita)
        medico.agregar_cita(cita)
        self.__citas.append(cita)
        if paciente.medico is None:      # primera cita: queda asignado ese médico
            medico.agregar_paciente(paciente)
        return cita

    def cancelar_cita(self, cita):
        if cita not in self.__citas:
            raise ValueError("La cita no existe.")
        cita.paciente.quitar_cita(cita)
        cita.medico.quitar_cita(cita)
        self.__citas.remove(cita)

    # ---------------------------------------------------------- polimorfismo
    def personas(self):
        """Lista mixta de Persona (pacientes y médicos) tratada de forma uniforme."""
        lista = []  # list[Persona]
        lista.extend(self.__medicos)
        lista.extend(self.__pacientes)
        return lista

    def resumen_personas(self):
        """Llama describir() y cantidad_citas() sin importar la clase concreta."""
        return [f"[{type(p).__name__}] {p.describir()}" for p in self.personas()]

    # ------------------------------------------------------------ datos demo
    def cargar_datos_demo(self):
        """Carga médicos, pacientes y citas de ejemplo para probar el sistema."""
        dias = ("Lun", "Mar", "Mie", "Jue", "Vie")
        m1 = Medico("1098111111", "Laura Ortiz", 1980, 5, 14, "F", "Cra 25 # 10-20",
                    681011, "Titular", "Medicina General", 6500000)
        m2 = Medico("1098222222", "Carlos Rueda", 1975, 9, 3, "M", "Cll 30 # 8-15",
                    681011, "Interino", "Odontología", 5200000)
        m3 = Medico("1098333333", "Andrea Duarte", 1988, 12, 21, "F", "Cra 18 # 22-40",
                    681011, "Sustituto", "Pediatría", 7100000)
        m1.generar_horarios(dias, 7, 17)
        m2.generar_horarios(("Lun", "Mie", "Vie", "Sab"), 8, 16)
        m3.generar_horarios(("Mar", "Jue", "Sab"), 6, 12)
        for m in (m1, m2, m3):
            self.registrar_medico(m)

        p1 = Paciente("1005444111", "Juan Pérez", 1995, 3, 8, "M", "Cll 12 # 4-50",
                      681011, 3, "3001234567")
        p2 = Paciente("1005444222", "María Gómez", 2001, 11, 30, "F", "Cra 9 # 15-12",
                      681011, 2, "3109876543", medico=m1)
        p3 = Paciente("1005444333", "Sofía Díaz", 2016, 7, 19, "F", "Cll 40 # 20-33",
                      681011, 4, "3157654321")
        for p in (p1, p2, p3):
            self.registrar_paciente(p)

        lunes = date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)
        self.agendar_cita(p1, m1, lunes, 8)
        self.agendar_cita(p1, m2, lunes, 10, 3)
        self.agendar_cita(p2, m1, lunes, 9, 1)
        self.agendar_cita(p3, m3, lunes + timedelta(days=1), 7, 2)
