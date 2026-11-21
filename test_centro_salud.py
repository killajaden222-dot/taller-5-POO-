"""Pruebas unitarias de la lógica del sistema (no requieren Tkinter)."""
import unittest
from datetime import date, timedelta

from gestor import CentroSalud
from medico import Medico
from paciente import Paciente
from persona import Persona


def proximo_dia(indice_semana):
    """Próxima fecha futura cuyo weekday() sea indice_semana (0 = lunes)."""
    hoy = date.today()
    return hoy + timedelta(days=(indice_semana - hoy.weekday()) % 7 or 7)


class PruebasCentroSalud(unittest.TestCase):
    def setUp(self):
        self.centro = CentroSalud()
        self.centro.cargar_datos_demo()
        self.laura = self.centro.buscar_medico("1098111111")
        self.juan = self.centro.buscar_paciente("1005444111")

    def test_encapsulacion_valida_datos(self):
        with self.assertRaises(ValueError):
            Paciente("12", "Ana", 2000, 1, 1, "F", "Cll 1", 681011, 3, "3001234567")
        with self.assertRaises(ValueError):
            self.juan.estrato = 9
        with self.assertRaises(ValueError):
            self.juan.set_fecha_nacimiento(2001, 2, 31)  # fecha inexistente
        with self.assertRaises(AttributeError):
            _ = self.juan.__estrato  # atributo privado (name mangling)

    def test_herencia_y_edad(self):
        self.assertIsInstance(self.juan, Persona)
        self.assertIsInstance(self.laura, Persona)
        self.assertGreaterEqual(self.laura.edad, 18)
        with self.assertRaises(ValueError):
            Medico("1098999999", "Menor Edad", date.today().year - 5, 1, 1, "M",
                   "Cll 1", 681011, "Titular", "Medicina General", 1000000)

    def test_polimorfismo(self):
        for persona in self.centro.personas():
            self.assertIsInstance(persona.cantidad_citas(), int)
        self.assertEqual(Persona("12345", "Ana", 2000, 1, 1, "F", "Cll 1", 681011)
                         .cantidad_citas(), 0)
        self.assertEqual(self.laura.cantidad_citas(), 2)

    def test_disponibilidad(self):
        lunes = proximo_dia(0)
        self.assertEqual(len(self.laura.verificar_disponibilidad("Lun", 8)), 1)
        self.assertEqual(self.laura.verificar_disponibilidad("Sab", 8), [])
        self.assertNotIn(8, self.laura.horas_libres(lunes))  # ya tiene cita
        self.assertEqual(self.laura.horas_libres(proximo_dia(6)), [])  # domingo

    def test_reglas_de_agendamiento(self):
        lunes = proximo_dia(0)
        with self.assertRaises(ValueError):   # médico ocupado
            self.centro.agendar_cita(self.centro.buscar_paciente("1005444333"),
                                     self.laura, lunes, 8)
        with self.assertRaises(ValueError):   # fuera de horario
            self.centro.agendar_cita(self.juan, self.laura, lunes, 18)
        with self.assertRaises(ValueError):   # domingo
            self.centro.agendar_cita(self.juan, self.laura, proximo_dia(6), 8)
        with self.assertRaises(ValueError):   # pasado
            self.centro.agendar_cita(self.juan, self.laura,
                                     date.today() - timedelta(days=1), 8)

    def test_agendar_y_cancelar(self):
        martes = proximo_dia(1)
        cita = self.centro.agendar_cita(self.juan, self.laura, martes, 10)
        self.assertIn(cita, self.juan.citas)
        self.assertIn(cita, self.laura.citas)
        self.centro.cancelar_cita(cita)
        self.assertNotIn(cita, self.juan.citas)
        self.assertIn(10, self.laura.horas_libres(martes))

    def test_estadisticas_paciente(self):
        por_mes = self.juan.cantidad_citas_por_mes()
        self.assertEqual(len(por_mes), 12)
        self.assertEqual(sum(por_mes), 2)
        self.assertEqual(dict(self.juan.cantidad_citas_por_esp()),
                         {"Medicina General": 1, "Odontología": 1})

    def test_sueldo_anual_y_relaciones(self):
        self.assertEqual(self.laura.calcular_sueldo_annio(), 6500000 * 12 * 1.10)
        self.assertIs(self.centro.buscar_paciente("1005444222").medico, self.laura)
        self.assertIn(self.juan, self.laura.pacientes)  # asignado en su primera cita


if __name__ == "__main__":
    unittest.main(verbosity=2)
