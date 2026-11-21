"""Constantes compartidas por los módulos del sistema Centro de Salud."""

DIAS_SEMANA = ("Lun", "Mar", "Mie", "Jue", "Vie", "Sab")  # días de atención
HORA_INICIO = 6    # primera hora de atención (inicio de bloque de 1 hora)
HORA_FIN = 18      # última hora de atención (inicio de bloque de 1 hora)
TIPOS_CITA = ("General", "Odontología", "Especialista")
TIPOS_MEDICO = ("Titular", "Interino", "Sustituto")
MESES = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")


def nombre_dia(fecha):
    """Convierte una fecha en la abreviatura del día ('Lun'...'Sab'; 'Dom' si es domingo)."""
    indice = fecha.weekday()  # lunes = 0 ... domingo = 6
    return DIAS_SEMANA[indice] if indice < len(DIAS_SEMANA) else "Dom"
