import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# --- Variables globales para almacenar referencias a los widgets ---
entry_funcion_objetivo_vars = []
restricciones_data = []
tipo_optimizacion_var = None

# Variables para Matplotlib
fig = None
ax = None
canvas_widget = None
toolbar = None


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
    frame_funcion_objetivo.grid_forget()
    frame_restricciones.grid_forget()
    boton_calcular_final.grid_forget()

    # Ocultar y limpiar el frame de resultados si ya existe
    global fig, ax, canvas_widget, toolbar
    if canvas_widget:
        canvas_widget.get_tk_widget().destroy()
        canvas_widget = None
    if toolbar:
        toolbar.destroy()
        toolbar = None
    if fig:
        plt.close(fig)
        fig = None
        ax = None

    if frame_resultados.winfo_children():
        limpiar_frame(frame_resultados)
    frame_resultados.grid_forget()

    # Mostrar el frame de configuración si no está ya visible
    frame_configuracion_problema.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    if metodo_seleccionado == "Gráfico":
        spinbox_num_variables.config(from_=2, to=2)
        num_variables_var.set(2)
    else:  # Para otros métodos (Simplex, etc.)
        spinbox_num_variables.config(from_=1, to=10)
        num_variables_var.set(3)


def generar_campos_problema():
    """
    Esta función se llamará cuando se presione el botón "Aceptar" de configuración.
    Se encarga de limpiar la interfaz anterior y dibujar
    los campos de la función objetivo y las restricciones dinámicamente.
    """
    global entry_funcion_objetivo_vars, restricciones_data, tipo_optimizacion_var

    num_vars = num_variables_var.get()
    num_rest = num_restricciones_var.get()
    metodo = metodo_var.get()

    if num_vars <= 0 or num_rest <= 0:
        messagebox.showwarning("Entrada Inválida", "La cantidad de variables y restricciones debe ser mayor a cero.")
        return

    # Limpiar y ocultar frames antes de redibujar
    limpiar_frame(frame_funcion_objetivo)
    limpiar_frame(frame_restricciones)
    frame_funcion_objetivo.grid_forget()
    frame_restricciones.grid_forget()
    boton_calcular_final.grid_forget()

    # Ocultar y limpiar el frame de resultados si ya existe
    global fig, ax, canvas_widget, toolbar
    if canvas_widget:
        canvas_widget.get_tk_widget().destroy()
        canvas_widget = None
    if toolbar:
        toolbar.destroy()
        toolbar = None
    if fig:
        plt.close(fig)
        fig = None
        ax = None

    if frame_resultados.winfo_children():
        limpiar_frame(frame_resultados)
    frame_resultados.grid_forget()

    entry_funcion_objetivo_vars = []
    restricciones_data = []

    # --- Generar campos de la Función Objetivo ---
    tk.Label(frame_funcion_objetivo, text=f"Función Objetivo ({metodo}):", font=("Arial", 10, "bold")).grid(row=0,
                                                                                                            column=0,
                                                                                                            columnspan=(
                                                                                                                        num_vars * 2 + 3),
                                                                                                            pady=5,
                                                                                                            sticky="w")

    if tipo_optimizacion_var is None:
        tipo_optimizacion_var = tk.StringVar(ventana)
    tipo_optimizacion_var.set("Maximizar")
    opciones_optimizacion = ["Maximizar", "Minimizar"]
    dropdown_optimizacion = ttk.OptionMenu(frame_funcion_objetivo, tipo_optimizacion_var, tipo_optimizacion_var.get(),
                                           *opciones_optimizacion)
    dropdown_optimizacion.grid(row=1, column=0, padx=2, pady=5)

    tk.Label(frame_funcion_objetivo, text="Z =", font=("Arial", 10)).grid(row=1, column=1, padx=2, pady=5)

    for i in range(num_vars):
        entry_coef = tk.Entry(frame_funcion_objetivo, width=5)
        entry_coef.grid(row=1, column=2 + i * 3, padx=2, pady=5)
        entry_funcion_objetivo_vars.append(entry_coef)
        tk.Label(frame_funcion_objetivo, text=f"X{i + 1}").grid(row=1, column=3 + i * 3, padx=2, pady=5)
        if i < num_vars - 1:
            tk.Label(frame_funcion_objetivo, text="+").grid(row=1, column=4 + i * 3, padx=2, pady=5)

    frame_funcion_objetivo.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    frame_funcion_objetivo.config(relief="raised")

    # --- Generar campos de las Restricciones ---
    tk.Label(frame_restricciones, text="Restricciones:", font=("Arial", 10, "bold")).grid(row=0, column=0,
                                                                                          columnspan=(num_vars * 2 + 3),
                                                                                          pady=10, sticky="w")

    opciones_desigualdad = ["<=", ">=", "="]

    for i in range(num_vars):
        tk.Label(frame_restricciones, text=f"X{i + 1}", font=("Arial", 9)).grid(row=1, column=i * 2, padx=5, pady=2)
        if i < num_vars - 1:
            tk.Label(frame_restricciones, text="+", font=("Arial", 9)).grid(row=1, column=i * 2 + 1, padx=2, pady=2)
    tk.Label(frame_restricciones, text="Signo", font=("Arial", 9)).grid(row=1, column=num_vars * 2, padx=5, pady=2)
    tk.Label(frame_restricciones, text="RHS", font=("Arial", 9)).grid(row=1, column=num_vars * 2 + 1, padx=5, pady=2)

    for r_idx in range(num_rest):
        restriccion_entries_vars = []
        restriccion_signo_var = tk.StringVar(ventana)
        restriccion_signo_var.set("<=")

        for v_idx in range(num_vars):
            entry_coef = tk.Entry(frame_restricciones, width=5)
            entry_coef.grid(row=r_idx + 2, column=v_idx * 2, padx=2, pady=2)
            restriccion_entries_vars.append(entry_coef)
            if v_idx < num_vars - 1:
                tk.Label(frame_restricciones, text="+").grid(row=r_idx + 2, column=v_idx * 2 + 1, padx=2, pady=2)

        dropdown_signo = ttk.OptionMenu(frame_restricciones, restriccion_signo_var, restriccion_signo_var.get(),
                                        *opciones_desigualdad)
        dropdown_signo.grid(row=r_idx + 2, column=num_vars * 2, padx=5, pady=2)

        entry_rhs = tk.Entry(frame_restricciones, width=7)
        entry_rhs.grid(row=r_idx + 2, column=num_vars * 2 + 1, padx=5, pady=2)

        restricciones_data.append({
            "coeficientes": restriccion_entries_vars,
            "signo": restriccion_signo_var,
            "rhs": entry_rhs
        })

    frame_restricciones.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
    frame_restricciones.config(relief="raised")

    boton_calcular_final.grid(row=4, column=0, padx=10, pady=20)


def calcular():
    """
    Esta función se ejecutará cuando el botón "Calcular" final sea presionado.
    Aquí se recogerán todos los datos y se realizará la operación y la visualización.
    """
    global fig, ax, canvas_widget, toolbar

    print("\n--- Recopilando Datos ---")

    if tipo_optimizacion_var is None:
        messagebox.showerror("Error", "No se ha inicializado el tipo de optimización. Presiona 'Aceptar' primero.")
        return
    tipo_optimizacion = tipo_optimizacion_var.get()
    print(f"Tipo de Optimización: {tipo_optimizacion}")

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

    print("\n--- Realizando Cálculos y Gráficos ---")

    # --- Lógica de graficación ---
    if frame_resultados.winfo_children():
        limpiar_frame(frame_resultados)

    if fig:
        plt.close(fig)
        fig = None
        ax = None
    if canvas_widget:
        canvas_widget.get_tk_widget().destroy()
        canvas_widget = None
    if toolbar:
        toolbar.destroy()
        toolbar = None

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.set_title("Gráfico de la Región Factible")
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    ax.grid(True)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)

    # --- Determinar límites del gráfico dinámicamente y de forma más robusta ---
    max_val_x1_axis = 0  # Máximo valor para X1 en el eje X
    max_val_x2_axis = 0  # Máximo valor para X2 en el eje Y

    for r in restricciones:
        a, b = r['coeficientes']
        rhs = r['rhs']

        if a != 0 and rhs / a > 0:  # Considerar solo valores positivos para los límites
            max_val_x1_axis = max(max_val_x1_axis, rhs / a)
        if b != 0 and rhs / b > 0:
            max_val_x2_axis = max(max_val_x2_axis, rhs / b)

        # También considerar el RHS directamente si es el valor dominante y positivo
        if rhs > 0:
            max_val_x1_axis = max(max_val_x1_axis, rhs)
            max_val_x2_axis = max(max_val_x2_axis, rhs)

    # Añadir un margen a los límites. Asegurar que sean al menos 10.
    x_lim = max(10.0, max_val_x1_axis * 1.2)
    y_lim = max(10.0, max_val_x2_axis * 1.2)

    ax.set_xlim(0, x_lim)
    ax.set_ylim(0, y_lim)

    # Graficación de las restricciones usando las intersecciones con los ejes
    for r_idx, r in enumerate(restricciones):
        try:
            a, b = r['coeficientes']
            rhs = r['rhs']
            signo = r['signo']

            x_points = []
            y_points = []

            # Calcular puntos de intersección con los ejes
            if a != 0:
                # Intersección con el eje X1 (cuando X2=0)
                x_intercept = rhs / a
                if x_intercept >= 0 and x_intercept <= x_lim + 1:  # Si está dentro de los límites visibles o un poco fuera
                    x_points.append(x_intercept)
                    y_points.append(0)

            if b != 0:
                # Intersección con el eje X2 (cuando X1=0)
                y_intercept = rhs / b
                if y_intercept >= 0 and y_intercept <= y_lim + 1:  # Si está dentro de los límites visibles o un poco fuera
                    x_points.append(0)
                    y_points.append(y_intercept)

            # Caso de líneas horizontales (solo X2)
            if a == 0 and b != 0:
                y_const = rhs / b
                if y_const >= 0 and y_const <= y_lim + 1:
                    ax.axhline(y=y_const, color=f'C{r_idx}', linestyle='-', label=f'R{r_idx + 1}: {b}X2 {signo} {rhs}')
            # Caso de líneas verticales (solo X1)
            elif b == 0 and a != 0:
                x_const = rhs / a
                if x_const >= 0 and x_const <= x_lim + 1:
                    ax.axvline(x=x_const, color=f'C{r_idx}', linestyle='-', label=f'R{r_idx + 1}: {a}X1 {signo} {rhs}')
            # Caso de línea general aX1 + bX2 = rhs
            elif a != 0 and b != 0:
                if len(x_points) == 2:  # Si encontramos ambas intersecciones
                    ax.plot(x_points, y_points, label=f'R{r_idx + 1}: {a}X1 + {b}X2 {signo} {rhs}')
                elif len(x_points) == 1:  # Si solo hay una intersección (la otra está fuera de los límites o es 0)
                    # Necesitamos un segundo punto. Podría ser un punto en el otro extremo del eje
                    if x_points[0] == 0:  # Intersección con Y, el punto es (0, y_intercept)
                        # Calcular X1 para Y=y_lim (o un punto más allá del límite)
                        x2_at_ylim = y_lim
                        x1_from_eq = (rhs - b * x2_at_ylim) / a
                        if x1_from_eq >= 0:
                            ax.plot([0, x1_from_eq], [y_points[0], x2_at_ylim],
                                    label=f'R{r_idx + 1}: {a}X1 + {b}X2 {signo} {rhs}')
                        else:  # Si el punto x1_from_eq es negativo, intentamos con X1=x_lim
                            y2_from_eq = (rhs - a * x_lim) / b
                            if y2_from_eq >= 0:
                                ax.plot([0, x_lim], [y_points[0], y2_from_eq],
                                        label=f'R{r_idx + 1}: {a}X1 + {b}X2 {signo} {rhs}')


                    elif y_points[0] == 0:  # Intersección con X, el punto es (x_intercept, 0)
                        # Calcular X2 para X1=x_lim
                        x1_at_xlim = x_lim
                        y2_from_eq = (rhs - a * x1_at_xlim) / b
                        if y2_from_eq >= 0:
                            ax.plot([x_points[0], x1_at_xlim], [0, y2_from_eq],
                                    label=f'R{r_idx + 1}: {a}X1 + {b}X2 {signo} {rhs}')
                        else:  # Si el punto y2_from_eq es negativo, intentamos con Y=y_lim
                            x1_from_eq = (rhs - b * y_lim) / a
                            if x1_from_eq >= 0:
                                ax.plot([x_points[0], x1_from_eq], [0, y_lim],
                                        label=f'R{r_idx + 1}: {a}X1 + {b}X2 {signo} {rhs}')

                    # Fallback si no se pudieron encontrar 2 puntos adecuados en los ejes
                    else:
                        messagebox.showwarning("Graficación",
                                               f"No se pudieron encontrar 2 puntos para graficar la restricción {r_idx + 1} correctamente. Puede que la línea esté fuera de los límites visibles.")
                        print(f"DEBUG: No se pudieron encontrar 2 puntos para R{r_idx + 1}")
                else:  # No se encontraron puntos en los ejes (ej. pasa por el origen, o ambos coeficientes son 0)
                    if rhs != 0:  # Si rhs no es 0, y ambos coeficientes son 0, es una restricción trivial (0 = RHS)
                        messagebox.showwarning("Restricción Trivial",
                                               f"La restricción {r_idx + 1} (0X1 + 0X2 {signo} {rhs}) es trivial y no define una línea. No se graficará.")
                        print(f"DEBUG: Restricción {r_idx + 1} es trivial o mal formada: {a}X1 + {b}X2 {signo} {rhs}")
                    else:  # Pasa por el origen (0,0)
                        # Necesitamos un segundo punto que no sea el origen. Ej. (x_lim, (rhs-a*x_lim)/b)
                        if b != 0:
                            y_val_at_xlim = (rhs - a * x_lim) / b
                            ax.plot([0, x_lim], [0, y_val_at_xlim], label=f'R{r_idx + 1}: {a}X1 + {b}X2 {signo} {rhs}')
                        elif a != 0:
                            x_val_at_ylim = (rhs - b * y_lim) / a
                            ax.plot([0, x_val_at_ylim], [0, y_lim], label=f'R{r_idx + 1}: {a}X1 + {b}X2 {signo} {rhs}')
                        else:  # 0X1 + 0X2 = 0
                            messagebox.showwarning("Restricción Trivial",
                                                   f"La restricción {r_idx + 1} (0X1 + 0X2 = 0) no define una región específica. No se graficará.")
                            print(f"DEBUG: Restricción {r_idx + 1} es 0=0")

        except Exception as e:
            print(f"Error al graficar restricción {r_idx + 1}: {e}")
            messagebox.showwarning("Error de Graficación",
                                   f"No se pudo graficar la restricción {r_idx + 1}. Asegúrate de ingresar coeficientes válidos y que la línea no sea infinita o trivial. Detalles: {e}")

    ax.legend()
    # --- Fin de la graficación de líneas ---

    canvas = FigureCanvasTkAgg(fig, master=frame_resultados)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    toolbar = NavigationToolbar2Tk(canvas, frame_resultados)
    toolbar.update()
    toolbar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    text_resultados = tk.Text(frame_resultados, height=10, width=50, wrap="word", font=("Arial", 10))
    text_resultados.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
    text_resultados.insert(tk.END, f"Tipo de Optimización: {tipo_optimizacion}\n\n")
    text_resultados.insert(tk.END, "Tipo de Solución: Óptima (Ejemplo)\n\n")
    text_resultados.insert(tk.END, "Interpretación: Los valores óptimos para X1 y X2 son...\n\n")
    text_resultados.insert(tk.END, "Aquí se mostrarían las operaciones, vértices, etc.")
    text_resultados.config(state="disabled")

    frame_resultados.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky="nsew")
    ventana.grid_columnconfigure(1, weight=1)
    frame_resultados.grid_rowconfigure(0, weight=1)
    frame_resultados.grid_rowconfigure(2, weight=1)

    canvas.draw()


# --- Configuración de la Ventana Principal ---
ventana = tk.Tk()
ventana.title("Calculadora de Programación Lineal")
ventana.geometry("1200x700")

ventana.grid_rowconfigure(0, weight=0)
ventana.grid_rowconfigure(1, weight=0)
ventana.grid_rowconfigure(2, weight=0)
ventana.grid_rowconfigure(3, weight=1)
ventana.grid_rowconfigure(4, weight=0)
ventana.grid_columnconfigure(0, weight=0)
ventana.grid_columnconfigure(1, weight=1)

# --- Frame para la Selección del Método (Columna 0, Fila 0) ---
frame_seleccion_metodo = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_seleccion_metodo.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

tk.Label(frame_seleccion_metodo, text="Seleccione el tipo de optimización:").grid(row=0, column=0, padx=5, pady=5)

metodo_var = tk.StringVar(ventana)
metodo_var.set("Gráfico")
opciones_metodo = ["Gráfico", "Simplex"]
dropdown_metodo = ttk.OptionMenu(frame_seleccion_metodo, metodo_var, metodo_var.get(), *opciones_metodo,
                                 command=actualizar_interfaz_metodo)
dropdown_metodo.grid(row=0, column=1, padx=5, pady=5)

# --- Frame para Cantidad de Variables y Restricciones (Columna 0, Fila 1) ---
frame_configuracion_problema = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_configuracion_problema.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

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

boton_aceptar_cantidades = tk.Button(frame_configuracion_problema, text="Aceptar", command=generar_campos_problema)
boton_aceptar_cantidades.grid(row=1, column=0, columnspan=4, pady=10)

# --- Frames para la Función Objetivo y Restricciones (inicialmente vacíos, se posicionan en generar_campos_problema) ---
frame_funcion_objetivo = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_restricciones = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)

# --- Botón de Calcular Final (se posiciona en generar_campos_problema) ---
boton_calcular_final = tk.Button(ventana, text="Calcular", command=calcular)

# --- Frame de Resultados (Contenedor para la gráfica y texto) ---
frame_resultados = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)

actualizar_interfaz_metodo()

ventana.mainloop()