"""Clase Paciente: hereda de Persona y mantiene su historial de citas."""
from persona import Persona
from medico import Medico
from constantes import MESES


class Paciente(Persona):
    """Paciente del centro. Relaciones: 0..* Cita y 1 Medico asignado."""

    def __init__(self, identificacion, nombres, annio_nac, mes_nac, dia_nac,
                 genero, direccion, codigo_postal, estrato, telefono,
                 ciudad="Giron", medico=None):
        super().__init__(identificacion, nombres, annio_nac, mes_nac, dia_nac,
                         genero, direccion, codigo_postal)
        self.estrato = estrato
        self.telefono = telefono
        self.ciudad = ciudad
        self.__citas = []       # asociación 0..* con Cita ("Solicita")
        self.__medico = None    # asociación con Medico ("Atiende")
        if medico is not None:
            medico.agregar_paciente(self)  # mantiene ambos lados sincronizados

    # ------------------------------------------------- getters y setters
    @property
    def estrato(self):
        return self.__estrato

    @estrato.setter
    def estrato(self, valor):
        try:
            numero = int(valor)
        except (TypeError, ValueError):
            raise ValueError("El estrato debe ser un número entero.") from None
        if not 1 <= numero <= 6:
            raise ValueError("El estrato debe estar entre 1 y 6.")
        self.__estrato = numero

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        texto = str(valor).strip()
        if not (texto.isdigit() and 7 <= len(texto) <= 10):
            raise ValueError("El teléfono debe tener entre 7 y 10 dígitos.")
        self.__telefono = texto

    @property
    def ciudad(self):
        return self.__ciudad

    @ciudad.setter
    def ciudad(self, valor):
        self.__ciudad = self._texto_obligatorio(valor, "La ciudad")

    @property
    def citas(self):
        return list(self.__citas)  # copia: la lista interna no se expone

    @citas.setter
    def citas(self, valor):
        from cita import Cita
        if not isinstance(valor, list) or not all(
                isinstance(c, Cita) and c.paciente is self for c in valor):
            raise ValueError("'citas' debe ser una lista de Cita de este paciente.")
        self.__citas = list(valor)

    @property
    def medico(self):
        return self.__medico

    @medico.setter
    def medico(self, valor):
        if valor is not None and not isinstance(valor, Medico):
            raise ValueError("El médico asignado debe ser un objeto Medico.")
        self.__medico = valor

    # ------------------------------------------------ gestión de citas
    def agregar_cita(self, cita):
        from cita import Cita  # importación diferida: evita dependencia circular
        if not isinstance(cita, Cita) or cita.paciente is not self:
            raise ValueError("La cita no pertenece a este paciente.")
        if cita not in self.__citas:
            self.__citas.append(cita)

    def quitar_cita(self, cita):
        if cita in self.__citas:
            self.__citas.remove(cita)

    def tiene_cita_en(self, fecha, hora):
        """True si el paciente ya tiene una cita en esa fecha y hora."""
        return any(c.fecha == fecha and c.hora.hour == hora for c in self.__citas)

    # ------------------------------------------------ estadísticas
    def cantidad_citas_por_mes(self, anio=None):
        """Lista de 12 enteros (enero..diciembre) con las citas de cada mes."""
        conteo = [0] * 12
        for cita in self.__citas:
            if anio is None or cita.fecha.year == anio:
                conteo[cita.fecha.month - 1] += 1
        return conteo

    def cantidad_citas_por_esp(self):
        """Lista de tuplas (especialidad, cantidad), de mayor a menor cantidad."""
        acumulado = {}
        for cita in self.__citas:
            esp = cita.medico.especialidad
            acumulado[esp] = acumulado.get(esp, 0) + 1
        return sorted(acumulado.items(), key=lambda par: (-par[1], par[0]))

    def resumen_por_mes(self, anio=None):
        """Texto legible con los meses que tienen al menos una cita."""
        conteo = self.cantidad_citas_por_mes(anio)
        return [f"{MESES[i]}: {n}" for i, n in enumerate(conteo) if n > 0]

    # ------------------------------------------------ polimorfismo
    def cantidad_citas(self):
        return len(self.__citas)

    def describir(self):
        asignado = self.__medico.nombres if self.__medico else "sin médico asignado"
        return (f"{super().describir()} | estrato {self.estrato}, {self.ciudad}, "
                f"tel. {self.telefono} | médico: {asignado} | "
                f"citas: {len(self.__citas)}")
