import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# --- Variables globales para almacenar referencias a los widgets ---
entry_funcion_objetivo_vars = []
restricciones_data = []
# Nueva variable para almacenar la selección de optimización (Max/Min)
tipo_optimizacion_var = None  # Se inicializará en generar_campos_problema()


# --- Funciones de Lógica ---
def limpiar_frame(frame):
    """Elimina todos los widgets dentro de un frame."""
    for widget in frame.winfo_children():
        widget.destroy()


def actualizar_interfaz_metodo(*args):
    """
    Esta función se llama cada vez que se cambia el método seleccionado.
    Ocultará/mostrará los elementos relevantes y ajustará los spinbox.
    """
    metodo_seleccionado = metodo_var.get()
    print(f"Método seleccionado: {metodo_seleccionado}")

    # Limpiamos y ocultamos los frames de la función objetivo y restricciones
    limpiar_frame(frame_funcion_objetivo)
    limpiar_frame(frame_restricciones)
    frame_funcion_objetivo.pack_forget()
    frame_restricciones.pack_forget()
    boton_calcular_final.pack_forget()

    # Mostrar el frame de configuración si no está ya visible
    frame_configuracion_problema.pack(pady=10)

    if metodo_seleccionado == "Gráfico":
        spinbox_num_variables.config(from_=2, to=2)  # Limita a 2 variables
        num_variables_var.set(2)  # Establece el valor por defecto a 2
    else:  # Para otros métodos (Simplex, etc.)
        spinbox_num_variables.config(from_=1, to=10)  # Permite más variables
        num_variables_var.set(3)  # Puedes poner un valor por defecto que desees


def generar_campos_problema():
    """
    Esta función se llamará cuando se presione el botón "Aceptar" de configuración.
    Se encarga de limpiar la interfaz anterior y dibujar
    los campos de la función objetivo y las restricciones dinámicamente.
    """
    global entry_funcion_objetivo_vars, restricciones_data, tipo_optimizacion_var  # Acceder a las variables globales

    num_vars = num_variables_var.get()
    num_rest = num_restricciones_var.get()
    metodo = metodo_var.get()

    # Validar que los números sean válidos (aunque el spinbox ayuda, es buena práctica)
    if num_vars <= 0 or num_rest <= 0:
        messagebox.showwarning("Entrada Inválida", "La cantidad de variables y restricciones debe ser mayor a cero.")
        return

    # Limpiar y ocultar frames antes de redibujar
    limpiar_frame(frame_funcion_objetivo)
    limpiar_frame(frame_restricciones)
    frame_funcion_objetivo.pack_forget()
    frame_restricciones.pack_forget()
    boton_calcular_final.pack_forget()

    entry_funcion_objetivo_vars = []  # Reiniciar lista para la función objetivo
    restricciones_data = []  # Reiniciar lista para las restricciones

    # --- Generar campos de la Función Objetivo ---
    tk.Label(frame_funcion_objetivo, text=f"Función Objetivo ({metodo}):", font=("Arial", 10, "bold")).grid(row=0,
                                                                                                            column=0,
                                                                                                            columnspan=(
                                                                                                                        num_vars * 2 + 3),
                                                                                                            pady=5,
                                                                                                            sticky="w")

    # NUEVO: Selector de Maximizar/Minimizar
    tipo_optimizacion_var = tk.StringVar(ventana)
    tipo_optimizacion_var.set("Maximizar")  # Valor inicial
    opciones_optimizacion = ["Maximizar", "Minimizar"]
    dropdown_optimizacion = ttk.OptionMenu(frame_funcion_objetivo, tipo_optimizacion_var, tipo_optimizacion_var.get(),
                                           *opciones_optimizacion)
    dropdown_optimizacion.grid(row=1, column=0, padx=2, pady=5)  # Posicionado al inicio de la fila

    tk.Label(frame_funcion_objetivo, text="Z =", font=("Arial", 10)).grid(row=1, column=1, padx=2, pady=5)

    # Coeficientes de la función objetivo
    for i in range(num_vars):
        entry_coef = tk.Entry(frame_funcion_objetivo, width=5)
        entry_coef.grid(row=1, column=2 + i * 3, padx=2, pady=5)  # Ajustar el column para dejar espacio al Max/Min Z=
        entry_funcion_objetivo_vars.append(entry_coef)
        tk.Label(frame_funcion_objetivo, text=f"X{i + 1}").grid(row=1, column=3 + i * 3, padx=2, pady=5)
        if i < num_vars - 1:  # Añadir el signo '+' entre variables
            tk.Label(frame_funcion_objetivo, text="+").grid(row=1, column=4 + i * 3, padx=2, pady=5)

    frame_funcion_objetivo.pack(pady=10)
    frame_funcion_objetivo.config(relief="raised")  # Le damos un relieve para que se vea mejor

    # --- Generar campos de las Restricciones ---
    tk.Label(frame_restricciones, text="Restricciones:", font=("Arial", 10, "bold")).grid(row=0, column=0,
                                                                                          columnspan=(num_vars * 2 + 3),
                                                                                          pady=10, sticky="w")

    opciones_desigualdad = ["<=", ">=", "="]

    # Encabezados de columna para las restricciones
    for i in range(num_vars):
        tk.Label(frame_restricciones, text=f"X{i + 1}", font=("Arial", 9)).grid(row=1, column=i * 2, padx=5, pady=2)
        if i < num_vars - 1:
            tk.Label(frame_restricciones, text="+", font=("Arial", 9)).grid(row=1, column=i * 2 + 1, padx=2, pady=2)
    tk.Label(frame_restricciones, text="Signo", font=("Arial", 9)).grid(row=1, column=num_vars * 2, padx=5, pady=2)
    tk.Label(frame_restricciones, text="RHS", font=("Arial", 9)).grid(row=1, column=num_vars * 2 + 1, padx=5,
                                                                      pady=2)  # RHS = Right Hand Side (lado derecho)

    for r_idx in range(num_rest):  # r_idx de restriccion_index
        restriccion_entries_vars = []  # Para los Entry de esta restricción
        restriccion_signo_var = tk.StringVar(ventana)
        restriccion_signo_var.set("<=")  # Valor inicial

        for v_idx in range(num_vars):  # v_idx de variable_index
            entry_coef = tk.Entry(frame_restricciones, width=5)
            entry_coef.grid(row=r_idx + 2, column=v_idx * 2, padx=2, pady=2)
            restriccion_entries_vars.append(entry_coef)
            if v_idx < num_vars - 1:
                tk.Label(frame_restricciones, text="+").grid(row=r_idx + 2, column=v_idx * 2 + 1, padx=2, pady=2)

        # Dropdown para el signo de desigualdad
        dropdown_signo = ttk.OptionMenu(frame_restricciones, restriccion_signo_var, restriccion_signo_var.get(),
                                        *opciones_desigualdad)
        dropdown_signo.grid(row=r_idx + 2, column=num_vars * 2, padx=5, pady=2)

        # Campo para el término independiente (RHS)
        entry_rhs = tk.Entry(frame_restricciones, width=7)
        entry_rhs.grid(row=r_idx + 2, column=num_vars * 2 + 1, padx=5, pady=2)

        # Guardar todos los elementos de esta restricción
        restricciones_data.append({
            "coeficientes": restriccion_entries_vars,
            "signo": restriccion_signo_var,
            "rhs": entry_rhs
        })

    frame_restricciones.pack(pady=10)
    frame_restricciones.config(relief="raised")  # Le damos un relieve para que se vea mejor

    # Mostrar el botón de calcular final
    boton_calcular_final.pack(pady=20)


def calcular():
    """
    Esta función se ejecutará cuando el botón "Calcular" final sea presionado.
    Aquí se recogerán todos los datos y se realizará la operación.
    """
    print("\n--- Recopilando Datos ---")

    tipo_optimizacion = tipo_optimizacion_var.get()
    print(f"Tipo de Optimización: {tipo_optimizacion}")

    # Obtener datos de la Función Objetivo
    coeficientes_fo = []
    for entry_coef in entry_funcion_objetivo_vars:
        try:
            coef = float(entry_coef.get())
            coeficientes_fo.append(coef)
        except ValueError:
            messagebox.showerror("Error de Entrada",
                                 "Por favor, ingresa números válidos para los coeficientes de la Función Objetivo.")
            return
    print(f"Función Objetivo: {coeficientes_fo}")

    # Obtener datos de las Restricciones
    restricciones = []
    for restriccion_info in restricciones_data:
        restriccion_actual = {
            "coeficientes": [],
            "signo": restriccion_info["signo"].get(),
            "rhs": None
        }
        for entry_coef in restriccion_info["coeficientes"]:
            try:
                coef = float(entry_coef.get())
                restriccion_actual["coeficientes"].append(coef)
            except ValueError:
                messagebox.showerror("Error de Entrada",
                                     f"Por favor, ingresa números válidos para los coeficientes de una restricción.")
                return

        try:
            rhs_val = float(restriccion_info["rhs"].get())
            restriccion_actual["rhs"] = rhs_val
        except ValueError:
            messagebox.showerror("Error de Entrada",
                                 f"Por favor, ingresa un número válido para el lado derecho de una restricción.")
            return

        restricciones.append(restriccion_actual)

    print("Restricciones:")
    for r in restricciones:
        print(f"  {r['coeficientes']} {r['signo']} {r['rhs']}")

    print("\n--- Realizando Cálculos (Lógica futura) ---")
    messagebox.showinfo("Cálculo Iniciado",
                        "Datos recopilados. Aquí se iniciaría la lógica del método Gráfico/Simplex.")
    # Aquí iría la lógica para resolver el problema de programación lineal
    # usando los datos recopilados (coeficientes_fo y restricciones).
    # Dependiendo del método seleccionado (metodo_var.get()), se llamaría
    # a la función de resolución adecuada.
    # Por ejemplo:
    # if metodo_var.get() == "Gráfico":
    #     resolver_metodo_grafico(coeficientes_fo, restricciones, tipo_optimizacion)
    # elif metodo_var.get() == "Simplex":
    #     resolver_metodo_simplex(coeficientes_fo, restricciones, tipo_optimizacion)


# --- Configuración de la Ventana Principal ---
ventana = tk.Tk()
ventana.title("Calculadora de Programación Lineal")
ventana.geometry("800x700")

# --- Frame para la Selección del Método ---
frame_seleccion_metodo = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_seleccion_metodo.pack(pady=20)

tk.Label(frame_seleccion_metodo, text="Seleccione el tipo de optimización:").grid(row=0, column=0, padx=5, pady=5)

metodo_var = tk.StringVar(ventana)
metodo_var.set("Gráfico")  # Valor inicial
opciones_metodo = ["Gráfico", "Simplex"]
dropdown_metodo = ttk.OptionMenu(frame_seleccion_metodo, metodo_var, metodo_var.get(), *opciones_metodo,
                                 command=actualizar_interfaz_metodo)
dropdown_metodo.grid(row=0, column=1, padx=5, pady=5)

# --- Frame para Cantidad de Variables y Restricciones ---
frame_configuracion_problema = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_configuracion_problema.pack(pady=10)

tk.Label(frame_configuracion_problema, text="Cantidad de Variables:").grid(row=0, column=0, padx=5, pady=5)
num_variables_var = tk.IntVar(ventana)
num_variables_var.set(2)
spinbox_num_variables = ttk.Spinbox(frame_configuracion_problema, from_=2, to=2, textvariable=num_variables_var,
                                    width=5)
spinbox_num_variables.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_configuracion_problema, text="Cantidad de Restricciones:").grid(row=0, column=2, padx=5, pady=5)
num_restricciones_var = tk.IntVar(ventana)
num_restricciones_var.set(3)
spinbox_num_restricciones = ttk.Spinbox(frame_configuracion_problema, from_=1, to=10,
                                        textvariable=num_restricciones_var, width=5)
spinbox_num_restricciones.grid(row=0, column=3, padx=5, pady=5)

# Botón para aceptar la cantidad de variables/restricciones y generar los campos
boton_aceptar_cantidades = tk.Button(frame_configuracion_problema, text="Aceptar", command=generar_campos_problema)
boton_aceptar_cantidades.grid(row=1, column=0, columnspan=4, pady=10)

# --- Frames para la Función Objetivo y Restricciones (inicialmente vacíos) ---
frame_funcion_objetivo = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_restricciones = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)

# --- Botón de Calcular Final ---
boton_calcular_final = tk.Button(ventana, text="Calcular", command=calcular)

# Llama a la función de actualización inicial para configurar el estado por defecto
actualizar_interfaz_metodo()

ventana.mainloop()