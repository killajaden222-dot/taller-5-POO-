"""Interfaz gráfica (solo Tkinter) para gestionar el Centro de Salud."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta

from paciente import Paciente
from medico import Medico
from constantes import DIAS_SEMANA, HORA_INICIO, HORA_FIN, TIPOS_MEDICO, nombre_dia

SIN_MEDICO = "(ninguno)"


# --------------------------------------------------------------- utilidades
def crear_formulario(padre, campos):
    """Crea filas 'etiqueta + control'. campos = [(clave, etiqueta, valores, inicial)].

    Si 'valores' es None se crea un Entry; si es una lista, un Combobox.
    Retorna dos diccionarios: variables y controles, indexados por clave."""
    variables, controles = {}, {}
    for fila, (clave, etiqueta, valores, inicial) in enumerate(campos):
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=4, pady=2)
        variable = tk.StringVar(value=inicial)
        if valores is None:
            control = ttk.Entry(padre, textvariable=variable, width=26)
        else:
            control = ttk.Combobox(padre, textvariable=variable, values=valores,
                                   state="readonly", width=24)
        control.grid(row=fila, column=1, padx=4, pady=2)
        variables[clave], controles[clave] = variable, control
    return variables, controles


def crear_tabla(padre, columnas, anchos=None):
    """Crea un Treeview con barra de desplazamiento vertical."""
    anchos = anchos or {}
    tabla = ttk.Treeview(padre, columns=columnas, show="headings", height=16)
    for columna in columnas:
        tabla.heading(columna, text=columna)
        tabla.column(columna, width=anchos.get(columna, 85), anchor="center")
    barra = ttk.Scrollbar(padre, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    return tabla, barra


def vaciar_tabla(tabla):
    for item in tabla.get_children():
        tabla.delete(item)


def a_entero(texto, campo):
    try:
        return int(str(texto).strip())
    except ValueError:
        raise ValueError(f"{campo} debe ser un número entero.") from None


# --------------------------------------------------------- pestaña Pacientes
class PestanaPacientes(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        self.app = app
        marco = ttk.LabelFrame(self, text="Registrar paciente")
        marco.pack(side="left", fill="y", padx=8, pady=8)
        self.vars, self.controles = crear_formulario(marco, [
            ("id", "Identificación", None, ""),
            ("nombres", "Nombres", None, ""),
            ("anio", "Año de nacimiento", None, ""),
            ("mes", "Mes de nacimiento", None, ""),
            ("dia", "Día de nacimiento", None, ""),
            ("genero", "Género", ["M", "F"], "M"),
            ("direccion", "Dirección", None, ""),
            ("cp", "Código postal", None, "681011"),
            ("estrato", "Estrato (1-6)", None, "3"),
            ("telefono", "Teléfono", None, ""),
            ("ciudad", "Ciudad", None, "Giron"),
            ("medico", "Médico asignado", [SIN_MEDICO], SIN_MEDICO),
        ])
        ttk.Button(marco, text="Registrar paciente", command=self.registrar).grid(
            row=12, column=0, columnspan=2, pady=8)

        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        columnas = ("ID", "Nombres", "Edad", "Género", "Estrato", "Ciudad",
                    "Teléfono", "Médico", "Citas")
        self.tabla, barra = crear_tabla(derecha, columnas, {"Nombres": 140, "Médico": 130})
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def registrar(self):
        v = self.vars
        try:
            medico = self.app.medico_por_etiqueta(v["medico"].get())
            paciente = Paciente(
                v["id"].get(), v["nombres"].get(),
                a_entero(v["anio"].get(), "El año"),
                a_entero(v["mes"].get(), "El mes"),
                a_entero(v["dia"].get(), "El día"),
                v["genero"].get(), v["direccion"].get(), v["cp"].get(),
                v["estrato"].get(), v["telefono"].get(), v["ciudad"].get())
            self.app.centro.registrar_paciente(paciente)
            if medico is not None:
                medico.agregar_paciente(paciente)
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        messagebox.showinfo("Paciente registrado", paciente.describir())
        for clave in ("id", "nombres", "anio", "mes", "dia", "direccion", "telefono"):
            v[clave].set("")
        self.app.refrescar()

    def refrescar(self):
        self.controles["medico"]["values"] = [SIN_MEDICO] + self.app.etiquetas_medicos()
        vaciar_tabla(self.tabla)
        for p in self.app.centro.pacientes:
            medico = p.medico.nombres if p.medico else "-"
            self.tabla.insert("", "end", values=(
                p.identificacion, p.nombres, p.edad, p.genero, p.estrato,
                p.ciudad, p.telefono, medico, p.cantidad_citas()))


# ----------------------------------------------------------- pestaña Médicos
class PestanaMedicos(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        self.app = app
        marco = ttk.LabelFrame(self, text="Registrar médico")
        marco.pack(side="left", fill="y", padx=8, pady=8)
        horas = [str(h) for h in range(HORA_INICIO, HORA_FIN + 1)]
        self.vars, _ = crear_formulario(marco, [
            ("id", "Identificación", None, ""),
            ("nombres", "Nombres", None, ""),
            ("anio", "Año de nacimiento", None, ""),
            ("mes", "Mes de nacimiento", None, ""),
            ("dia", "Día de nacimiento", None, ""),
            ("genero", "Género", ["M", "F"], "M"),
            ("direccion", "Dirección", None, ""),
            ("cp", "Código postal", None, "681011"),
            ("tipo", "Tipo de médico", list(TIPOS_MEDICO), TIPOS_MEDICO[0]),
            ("especialidad", "Especialidad", None, "Medicina General"),
            ("sueldo", "Sueldo mensual", None, ""),
            ("hora_ini", "Hora inicial (6-18)", horas, "8"),
            ("hora_fin", "Hora final (6-18)", horas, "16"),
        ])
        fila_dias = ttk.Frame(marco)
        fila_dias.grid(row=13, column=0, columnspan=2, pady=4)
        self.dias = {d: tk.BooleanVar(value=d != "Sab") for d in DIAS_SEMANA}
        for i, dia in enumerate(DIAS_SEMANA):
            ttk.Checkbutton(fila_dias, text=dia, variable=self.dias[dia]).grid(row=0, column=i)
        ttk.Button(marco, text="Registrar médico", command=self.registrar).grid(
            row=14, column=0, columnspan=2, pady=8)

        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        columnas = ("ID", "Nombres", "Tipo", "Especialidad", "Sueldo mensual",
                    "Sueldo anual", "Pacientes", "Citas")
        self.tabla, barra = crear_tabla(derecha, columnas, {
            "Nombres": 130, "Especialidad": 120, "Sueldo mensual": 105, "Sueldo anual": 105})
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def registrar(self):
        v = self.vars
        try:
            medico = Medico(
                v["id"].get(), v["nombres"].get(),
                a_entero(v["anio"].get(), "El año"),
                a_entero(v["mes"].get(), "El mes"),
                a_entero(v["dia"].get(), "El día"),
                v["genero"].get(), v["direccion"].get(), v["cp"].get(),
                v["tipo"].get(), v["especialidad"].get(), v["sueldo"].get())
            dias = [d for d, var in self.dias.items() if var.get()]
            if not dias:
                raise ValueError("Seleccione al menos un día de atención.")
            medico.generar_horarios(dias, a_entero(v["hora_ini"].get(), "La hora inicial"),
                                    a_entero(v["hora_fin"].get(), "La hora final"))
            self.app.centro.registrar_medico(medico)
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        messagebox.showinfo("Médico registrado", medico.describir())
        for clave in ("id", "nombres", "anio", "mes", "dia", "direccion", "sueldo"):
            v[clave].set("")
        self.app.refrescar()

    def refrescar(self):
        vaciar_tabla(self.tabla)
        for m in self.app.centro.medicos:
            self.tabla.insert("", "end", values=(
                m.identificacion, m.nombres, m.tipo_medico, m.especialidad,
                f"${m.sueldo:,.0f}", f"${m.calcular_sueldo_annio():,.0f}",
                len(m.pacientes), m.cantidad_citas()))


# ------------------------------------------------------------ pestaña Citas
class PestanaCitas(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        self.app = app
        self.citas_por_fila = {}   # id de fila del Treeview -> objeto Cita
        marco = ttk.LabelFrame(self, text="Agendar cita")
        marco.pack(fill="x", padx=8, pady=8)
        manana = date.today() + timedelta(days=1)
        self.v_paciente, self.v_medico = tk.StringVar(), tk.StringVar()
        self.v_fecha = tk.StringVar(value=manana.isoformat())
        self.v_hora, self.v_consultorio = tk.StringVar(), tk.StringVar(value="NA")

        ttk.Label(marco, text="Paciente").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.combo_paciente = ttk.Combobox(marco, textvariable=self.v_paciente,
                                           state="readonly", width=34)
        self.combo_paciente.grid(row=0, column=1, padx=4)
        ttk.Label(marco, text="Médico").grid(row=0, column=2, sticky="w", padx=4)
        self.combo_medico = ttk.Combobox(marco, textvariable=self.v_medico,
                                         state="readonly", width=40)
        self.combo_medico.grid(row=0, column=3, padx=4)
        ttk.Label(marco, text="Fecha (AAAA-MM-DD)").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(marco, textvariable=self.v_fecha, width=14).grid(row=1, column=1, sticky="w", padx=4)
        ttk.Button(marco, text="Ver horas libres", command=self.ver_horas).grid(
            row=1, column=2, padx=4)
        self.combo_hora = ttk.Combobox(marco, textvariable=self.v_hora,
                                       state="readonly", width=10)
        self.combo_hora.grid(row=1, column=3, sticky="w", padx=4)
        ttk.Label(marco, text="Consultorio (número o NA)").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(marco, textvariable=self.v_consultorio, width=14).grid(row=2, column=1, sticky="w", padx=4)
        ttk.Button(marco, text="Agendar cita", command=self.agendar).grid(
            row=2, column=2, padx=4, pady=4)
        ttk.Button(marco, text="Cancelar cita seleccionada", command=self.cancelar).grid(
            row=2, column=3, sticky="w", padx=4)

        inferior = ttk.Frame(self)
        inferior.pack(fill="both", expand=True, padx=8, pady=8)
        columnas = ("Fecha", "Día", "Hora", "Paciente", "Médico", "Especialidad",
                    "Tipo", "Consultorio")
        self.tabla, barra = crear_tabla(inferior, columnas, {
            "Paciente": 150, "Médico": 150, "Especialidad": 120, "Tipo": 100})
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def leer_fecha(self):
        try:
            return date.fromisoformat(self.v_fecha.get().strip())
        except ValueError:
            raise ValueError("La fecha debe tener el formato AAAA-MM-DD.") from None

    def ver_horas(self):
        try:
            medico = self.app.medico_por_etiqueta(self.v_medico.get())
            if medico is None:
                raise ValueError("Seleccione un médico.")
            fecha = self.leer_fecha()
            horas = medico.horas_libres(fecha)
            if fecha == date.today():
                horas = [h for h in horas if h > datetime.now().hour]
        except ValueError as error:
            messagebox.showerror("Consulta no válida", str(error))
            return
        self.combo_hora["values"] = [f"{h:02d}:00" for h in horas]
        self.v_hora.set(f"{horas[0]:02d}:00" if horas else "")
        if not horas:
            messagebox.showinfo("Sin disponibilidad",
                                f"El médico no tiene horas libres el {nombre_dia(fecha)} {fecha}.")

    def agendar(self):
        try:
            paciente = self.app.paciente_por_etiqueta(self.v_paciente.get())
            medico = self.app.medico_por_etiqueta(self.v_medico.get())
            if paciente is None or medico is None:
                raise ValueError("Seleccione un paciente y un médico.")
            if not self.v_hora.get():
                raise ValueError("Pulse 'Ver horas libres' y elija una hora.")
            hora = int(self.v_hora.get().split(":")[0])
            cita = self.app.centro.agendar_cita(paciente, medico, self.leer_fecha(),
                                                hora, self.v_consultorio.get())
        except ValueError as error:
            messagebox.showerror("No se pudo agendar", str(error))
            return
        messagebox.showinfo("Cita agendada", str(cita))
        self.combo_hora["values"] = []
        self.v_hora.set("")
        self.app.refrescar()

    def cancelar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Cancelar cita", "Seleccione una cita de la tabla.")
            return
        cita = self.citas_por_fila[seleccion[0]]
        if messagebox.askyesno("Cancelar cita", f"¿Cancelar esta cita?\n{cita}"):
            self.app.centro.cancelar_cita(cita)
            self.app.refrescar()

    def refrescar(self):
        self.combo_paciente["values"] = self.app.etiquetas_pacientes()
        self.combo_medico["values"] = self.app.etiquetas_medicos()
        vaciar_tabla(self.tabla)
        self.citas_por_fila = {}
        for c in sorted(self.app.centro.citas, key=lambda c: (c.fecha, c.hora)):
            fila = self.tabla.insert("", "end", values=(
                c.fecha.isoformat(), nombre_dia(c.fecha), f"{c.hora:%H:%M}",
                c.paciente.nombres, c.medico.nombres, c.medico.especialidad,
                c.tipo, c.num_consultorio))
            self.citas_por_fila[fila] = c


# --------------------------------------------------------- pestaña Consultas
class PestanaConsultas(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        self.app = app
        marco = ttk.LabelFrame(self, text="Consultas")
        marco.pack(fill="x", padx=8, pady=8)
        self.v_paciente, self.v_medico = tk.StringVar(), tk.StringVar()
        self.combo_paciente = ttk.Combobox(marco, textvariable=self.v_paciente,
                                           state="readonly", width=40)
        self.combo_paciente.grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(marco, text="Ver paciente y estadísticas",
                   command=self.ver_paciente).grid(row=0, column=1, padx=4)
        self.combo_medico = ttk.Combobox(marco, textvariable=self.v_medico,
                                         state="readonly", width=40)
        self.combo_medico.grid(row=1, column=0, padx=4, pady=4)
        ttk.Button(marco, text="Ver médico y horarios",
                   command=self.ver_medico).grid(row=1, column=1, padx=4)
        ttk.Button(marco, text="Listar todas las personas (polimorfismo)",
                   command=self.ver_personas).grid(row=0, column=2, rowspan=2, padx=12)
        self.salida = tk.Text(self, height=22, wrap="word", state="disabled")
        self.salida.pack(fill="both", expand=True, padx=8, pady=8)

    def mostrar(self, lineas):
        self.salida.configure(state="normal")
        self.salida.delete("1.0", "end")
        self.salida.insert("end", "\n".join(lineas))
        self.salida.configure(state="disabled")

    def ver_paciente(self):
        p = self.app.paciente_por_etiqueta(self.v_paciente.get())
        if p is None:
            messagebox.showwarning("Consulta", "Seleccione un paciente.")
            return
        por_esp = ", ".join(f"{e}: {n}" for e, n in p.cantidad_citas_por_esp())
        lineas = [p.describir(), "",
                  "Citas por mes: " + (", ".join(p.resumen_por_mes()) or "sin citas"),
                  "Citas por especialidad: " + (por_esp or "sin citas"), "", "Citas:"]
        lineas += [f"  - {c}" for c in sorted(p.citas, key=lambda c: (c.fecha, c.hora))]
        self.mostrar(lineas)

    def ver_medico(self):
        m = self.app.medico_por_etiqueta(self.v_medico.get())
        if m is None:
            messagebox.showwarning("Consulta", "Seleccione un médico.")
            return
        dias = [d for d in DIAS_SEMANA if m.verificar_disponibilidad(d)]
        lineas = [m.describir(), "",
                  f"Sueldo mensual: ${m.sueldo:,.0f}",
                  f"Sueldo anual (con bonificación): ${m.calcular_sueldo_annio():,.0f}",
                  "Días de atención: " + ", ".join(dias), "", "Pacientes que atiende:"]
        lineas += [f"  - {p.nombres}" for p in m.pacientes] or ["  (ninguno)"]
        self.mostrar(lineas)

    def ver_personas(self):
        self.mostrar(self.app.centro.resumen_personas())

    def refrescar(self):
        self.combo_paciente["values"] = self.app.etiquetas_pacientes()
        self.combo_medico["values"] = self.app.etiquetas_medicos()


# ------------------------------------------------------------ ventana principal
class App(tk.Tk):
    def __init__(self, centro):
        super().__init__()
        self.centro = centro
        self.title(f"{centro.nombre} - Gestión de citas")
        self.geometry("1150x650")
        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True, padx=6, pady=6)
        self.pestanas = [(PestanaPacientes(cuaderno, self), "Pacientes"),
                         (PestanaMedicos(cuaderno, self), "Médicos"),
                         (PestanaCitas(cuaderno, self), "Citas"),
                         (PestanaConsultas(cuaderno, self), "Consultas")]
        for pestana, titulo in self.pestanas:
            cuaderno.add(pestana, text=titulo)
        self.refrescar()

    def refrescar(self):
        """Actualiza todas las pestañas después de cualquier cambio en los datos."""
        for pestana, _ in self.pestanas:
            pestana.refrescar()

    def etiquetas_pacientes(self):
        return [f"{p.identificacion} - {p.nombres}" for p in self.centro.pacientes]

    def etiquetas_medicos(self):
        return [f"{m.identificacion} - {m.nombres} ({m.especialidad})"
                for m in self.centro.medicos]

    def paciente_por_etiqueta(self, etiqueta):
        return self.centro.buscar_paciente(etiqueta.split(" - ")[0]) if etiqueta else None

    def medico_por_etiqueta(self, etiqueta):
        if not etiqueta or etiqueta == SIN_MEDICO:
            return None
        return self.centro.buscar_medico(etiqueta.split(" - ")[0])
