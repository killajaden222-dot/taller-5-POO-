# Sistema de Gestión "Centro de Salud"

Taller 5 · Unidad 2 · Programación Orientada a Objetos · Universidad Cooperativa de Colombia

Sistema en **Python 3.10+** y **Tkinter** (librería nativa, sin dependencias externas) que modela la gestión de pacientes, médicos, horarios y citas de un centro médico, según el diagrama de clases del taller.

**Integrantes:** Freddy Duarte

**Docente:** Gustavo Gómez

**Video de sustentación:** _[Enlace]_

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `constantes.py` | Días, horas de atención, tipos de cita/médico y la función `nombre_dia()`. |
| `persona.py` | Clase base `Persona` (encapsulación, validaciones, métodos polimórficos). |
| `paciente.py` | `Paciente(Persona)`: citas, médico asignado y estadísticas. |
| `medico.py` | `Medico(Persona)`: horarios, pacientes, citas, disponibilidad y sueldo anual. |
| `horario.py` | `Horario`: franja semanal de una hora de un médico. |
| `cita.py` | `Cita`: asociación médico–paciente con fecha, hora, tipo y consultorio. |
| `gestor.py` | `CentroSalud`: controlador con las listas generales y las reglas de agendamiento. |
| `gui.py` | Interfaz gráfica Tkinter (pestañas Pacientes, Médicos, Citas y Consultas). |
| `main.py` | Punto de entrada. |
| `test_centro_salud.py` | Pruebas unitarias de la lógica (no requieren interfaz). |

## Ejecución

```bash
python main.py            # inicia con datos de ejemplo
python main.py --vacio    # inicia sin datos
python test_centro_salud.py   # ejecuta las pruebas
```

En Windows se usa `python` o `py`. Tkinter viene incluido con el instalador oficial de Python; en Linux puede requerir `sudo apt install python3-tk`.

## Conceptos de POO aplicados

- **Herencia:** `Paciente` y `Medico` heredan de `Persona`.
- **Encapsulación:** todos los atributos son privados (`__atributo`) y se acceden con getters/setters (`@property`) que validan los datos.
- **Polimorfismo:** `cantidad_citas()` y `describir()` se sobrescriben en `Paciente` y `Medico`; `CentroSalud.resumen_personas()` los invoca sobre una lista mixta de `Persona`.
- **Relaciones y listas:** `Paciente 1—0..* Cita`, `Medico 1—1..* Cita`, `Medico 1—1..* Horario`, `Medico 1—1..* Paciente`, implementadas con `list`.

## Adaptaciones respecto al diagrama

- Los nombres de métodos usan `snake_case` de Python (`calcularEdad` → `calcular_edad`; `CalcularSueldoAnnio` → `calcular_sueldo_annio`).
- `coidgoPosta` se corrigió a `codigo_postal`.
- `calcularEdad()` y `esMayorEdad()` son privados como en el diagrama; la edad se consulta con la propiedad pública `edad`.
- Se agregó la clase controladora `CentroSalud`, que no está en el diagrama, para coordinar las listas generales y aplicar las reglas de negocio sin mezclar esa lógica con la interfaz.
- Para respetar las cardinalidades `1..*`, `Medico` guarda además las listas de `pacientes` y `horarios`.
- `Horario.disponibilidad` indica si el médico atiende esa franja semanal; los choques en una fecha concreta se verifican con las citas existentes.
- `Medico.calcular_sueldo_annio()` suma 12 mensualidades más una bonificación según el tipo (Titular 10 %, Interino 5 %, Sustituto 0 %). Es un supuesto de diseño.

## Reglas de agendamiento (`CentroSalud.agendar_cita`)

1. Paciente y médico deben estar registrados.
2. No se agendan citas en el pasado ni los domingos.
3. El médico debe atender ese día y esa hora (`verificar_disponibilidad`).
4. Ni el médico ni el paciente pueden tener otra cita en la misma fecha y hora.
5. El tipo de cita (General, Odontología, Especialista) se deduce de la especialidad del médico.
