"""Clase base Persona: datos comunes de pacientes y médicos."""
from datetime import date


class Persona:
    """Superclase de Paciente y Medico. Todos sus atributos son privados."""

    GENEROS = ("M", "F")
    MAYORIA_EDAD = 18

    def __init__(self, identificacion, nombres, annio_nac, mes_nac, dia_nac,
                 genero, direccion, codigo_postal):
        # Cada asignación pasa por su setter, que valida el dato.
        self.identificacion = identificacion
        self.nombres = nombres
        self.set_fecha_nacimiento(annio_nac, mes_nac, dia_nac)
        self.genero = genero
        self.direccion = direccion
        self.codigo_postal = codigo_postal

    # ------------------------------------------------------------ utilidades
    @staticmethod
    def _texto_obligatorio(valor, campo):
        """Valida que el valor sea un texto no vacío (lo reutilizan las subclases)."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{campo} no puede estar vacío.")
        return " ".join(valor.split())

    # ------------------------------------------------- getters y setters
    @property
    def identificacion(self):
        return self.__identificacion

    @identificacion.setter
    def identificacion(self, valor):
        texto = str(valor).strip()
        if not (texto.isdigit() and 5 <= len(texto) <= 12):
            raise ValueError("La identificación debe tener entre 5 y 12 dígitos.")
        self.__identificacion = texto

    @property
    def nombres(self):
        return self.__nombres

    @nombres.setter
    def nombres(self, valor):
        texto = self._texto_obligatorio(valor, "Los nombres")
        if not all(c.isalpha() or c.isspace() for c in texto):
            raise ValueError("Los nombres solo pueden contener letras y espacios.")
        self.__nombres = texto.title()

    def set_fecha_nacimiento(self, annio, mes, dia):
        """Valida la fecha completa (evita combinaciones como 31 de febrero)."""
        try:
            nacimiento = date(int(annio), int(mes), int(dia))
        except (TypeError, ValueError):
            raise ValueError("La fecha de nacimiento no es válida.") from None
        if not (1900 <= nacimiento.year and nacimiento <= date.today()):
            raise ValueError("La fecha de nacimiento debe estar entre 1900 y hoy.")
        self.__annio_nac = nacimiento.year
        self.__mes_nac = nacimiento.month
        self.__dia_nac = nacimiento.day

    @property
    def annio_nac(self):
        return self.__annio_nac

    @annio_nac.setter
    def annio_nac(self, valor):
        self.set_fecha_nacimiento(valor, self.__mes_nac, self.__dia_nac)

    @property
    def mes_nac(self):
        return self.__mes_nac

    @mes_nac.setter
    def mes_nac(self, valor):
        self.set_fecha_nacimiento(self.__annio_nac, valor, self.__dia_nac)

    @property
    def dia_nac(self):
        return self.__dia_nac

    @dia_nac.setter
    def dia_nac(self, valor):
        self.set_fecha_nacimiento(self.__annio_nac, self.__mes_nac, valor)

    @property
    def genero(self):
        return self.__genero

    @genero.setter
    def genero(self, valor):
        texto = str(valor).strip().upper()
        if texto not in Persona.GENEROS:
            raise ValueError("El género debe ser 'M' o 'F'.")
        self.__genero = texto

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        self.__direccion = self._texto_obligatorio(valor, "La dirección")

    @property
    def codigo_postal(self):
        return self.__codigo_postal

    @codigo_postal.setter
    def codigo_postal(self, valor):
        texto = str(valor).strip()
        if not (texto.isdigit() and len(texto) == 6):
            raise ValueError("El código postal debe tener 6 dígitos.")
        self.__codigo_postal = int(texto)

    # ---------------------------------------- métodos privados del diagrama
    def __calcular_edad(self):
        hoy = date.today()
        edad = hoy.year - self.__annio_nac
        if (hoy.month, hoy.day) < (self.__mes_nac, self.__dia_nac):
            edad -= 1  # todavía no ha cumplido años este año
        return edad

    def __es_mayor_edad(self):
        return self.__calcular_edad() >= Persona.MAYORIA_EDAD

    @property
    def edad(self):
        """Acceso público de solo lectura al método privado calcularEdad()."""
        return self.__calcular_edad()

    # ------------------------------------------------ métodos polimórficos
    def cantidad_citas(self):
        """La Persona genérica no tiene citas; las subclases sobrescriben este método."""
        return 0

    def describir(self):
        mayoria = "mayor de edad" if self.__es_mayor_edad() else "menor de edad"
        return f"{self.nombres} (ID {self.identificacion}), {self.edad} años, {mayoria}"

    def __str__(self):
        return self.describir()
