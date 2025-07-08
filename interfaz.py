# interfaz.py

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# Colores y Estilos
DARK_BG = "#1e1e1e"
DARKER_BG = "#161616"
LIGHT_TEXT = "#f8f9fa"
ACCENT_COLOR = "#3a86ff"
SECONDARY_COLOR = "#6c757d"
ENTRY_BG = "#2d2d2d"


class InterfazProgramacionLineal:
    def __init__(self, root, calcular_callback):
        self.root = root
        self.calcular_callback = calcular_callback
        self.configurar_estilos()
        self.configurar_interfaz()
        self.variables_interfaz()

    def configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure("TFrame", background=DARK_BG)
        self.style.configure("TLabel", background=DARK_BG, foreground=LIGHT_TEXT)
        self.style.configure("TButton", background=DARKER_BG, foreground=LIGHT_TEXT)
        self.style.map("TButton", background=[('active', "#343a40")], foreground=[('active', LIGHT_TEXT)])

        self.style.configure("Accent.TButton", background=ACCENT_COLOR, foreground=LIGHT_TEXT,
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[('active', '#2563eb')])

        # Estilo personalizado para los OptionMenu de los signos (+, -, <=, etc.)
        self.style.configure("Signo.TMenubutton",
                             padding=[2, 2, 2, 2],
                             arrowsize=8,
                             font=("Segoe UI", 10))

    def configurar_interfaz(self):
        self.root.title("Programación Lineal - Solver")
        self.root.geometry("1200x700")
        self.root.configure(bg=DARK_BG)

        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        plt.style.use('dark_background')

    def variables_interfaz(self):
        self.num_variables_var = tk.IntVar(value=2)
        self.num_restricciones_var = tk.IntVar(value=3)
        self.tipo_optimizacion_var = tk.StringVar(value="Maximizar")
        self.metodo_resolucion_var = tk.StringVar(value="Simplex")

        self.crear_widgets_configuracion()
        self.crear_widgets_io()
        self.actualizar_variables_metodo()

    def crear_widgets_configuracion(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        ttk.Label(frame, text="Solver de Programación Lineal", font=("Segoe UI", 14, "bold")).grid(row=0, column=0,
                                                                                                   pady=5, sticky="w")

        controls_frame = ttk.Frame(self.root, padding="10 0 10 10")
        controls_frame.grid(row=1, column=0, sticky="ew")

        ttk.Label(controls_frame, text="Método:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_metodo = ttk.Combobox(controls_frame, textvariable=self.metodo_resolucion_var,
                                         values=["Gráfico", "Simplex", "Dos Fases"], state="readonly", width=10)
        self.combo_metodo.grid(row=0, column=1, padx=5, pady=5)
        self.combo_metodo.bind("<<ComboboxSelected>>", self.actualizar_variables_metodo)

        ttk.Label(controls_frame, text="Variables:").grid(row=0, column=2, padx=(15, 5), pady=5, sticky="w")
        self.spinbox_variables = ttk.Spinbox(controls_frame, from_=2, to=10, textvariable=self.num_variables_var,
                                             width=5)
        self.spinbox_variables.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(controls_frame, text="Restricciones:").grid(row=0, column=4, padx=(15, 5), pady=5, sticky="w")
        self.spinbox_restricciones = ttk.Spinbox(controls_frame, from_=1, to=10,
                                                 textvariable=self.num_restricciones_var, width=5)
        self.spinbox_restricciones.grid(row=0, column=5, padx=5, pady=5)

        botones_frame = ttk.Frame(controls_frame)
        botones_frame.grid(row=1, column=0, columnspan=6, pady=10, sticky="ew")
        botones_frame.grid_columnconfigure(0, weight=1)
        botones_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(botones_frame, text="Generar Campos", command=self.generar_campos_problema).grid(row=0, column=0,
                                                                                                    sticky="ew")
        ttk.Button(botones_frame, text="Limpiar", command=self.reiniciar_interfaz).grid(row=0, column=1, padx=5,
                                                                                        sticky="ew")

    def crear_widgets_io(self):
        self.frame_io = ttk.Frame(self.root)
        self.frame_io.grid(row=2, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.frame_io.grid_rowconfigure(1, weight=1)

        self.frame_funcion_objetivo = ttk.Frame(self.frame_io, padding=10)
        self.frame_restricciones = ttk.Frame(self.frame_io, padding=10)

        self.frame_resultados = ttk.Frame(self.root)
        self.frame_resultados.grid(row=1, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")
        self.frame_resultados.grid_rowconfigure(0, weight=1)
        self.frame_resultados.grid_columnconfigure(0, weight=1)

        self.boton_resolver = ttk.Button(self.root, text="Resolver", style="Accent.TButton", command=self.calcular)
        self.entry_funcion_objetivo_vars = []
        self.signos_fo_vars = []
        self.restricciones_data = []

    def actualizar_variables_metodo(self, event=None):
        if self.metodo_resolucion_var.get() == "Gráfico":
            if self.num_variables_var.get() > 2: self.num_variables_var.set(2)
            self.spinbox_variables.config(state="disabled")
        else:
            self.spinbox_variables.config(state="normal")
        self.generar_campos_problema()

    def generar_campos_problema(self):
        for frame in [self.frame_funcion_objetivo, self.frame_restricciones]:
            for widget in frame.winfo_children(): widget.destroy()

        self._generar_campos_funcion_objetivo()
        self._generar_campos_restricciones()

        self.frame_funcion_objetivo.grid(row=0, column=0, sticky="ew")
        self.frame_restricciones.grid(row=1, column=0, sticky="nsew")
        self.boton_resolver.grid(row=4, column=0, padx=10, pady=20, sticky="ew")
        self.limpiar_resultados()

    # En interfaz.py, reemplaza esta función

    def _generar_campos_funcion_objetivo(self):
        self.entry_funcion_objetivo_vars = []
        self.signos_fo_vars = []
        ttk.Label(self.frame_funcion_objetivo, text="Función Objetivo:", font=("Segoe UI", 11, "bold")).grid(row=0,
                                                                                                             column=0,
                                                                                                             columnspan=2,
                                                                                                             pady=5,
                                                                                                             sticky="w")

        optim_frame = ttk.Frame(self.frame_funcion_objetivo)
        optim_frame.grid(row=1, column=0, padx=2, pady=5, sticky="w")
        ttk.OptionMenu(optim_frame, self.tipo_optimizacion_var, self.tipo_optimizacion_var.get(), "Maximizar",
                       "Minimizar").pack()

        fo_entries_frame = ttk.Frame(self.frame_funcion_objetivo)
        fo_entries_frame.grid(row=1, column=1, sticky="w")
        ttk.Label(fo_entries_frame, text="Z =").pack(side="left", padx=5)

        for i in range(self.num_variables_var.get()):
            # --- CAMBIO CLAVE: Se quitó el "if i > 0" ---
            # Ahora el selector de signo aparece para TODOS los términos, incluido X1
            signo_var = tk.StringVar(value="+")
            signo_widget = ttk.Spinbox(
                fo_entries_frame,
                textvariable=signo_var,
                values=("+", "-"),
                width=2,
                wrap=True,
                state='readonly'
            )
            signo_widget.pack(side="left", padx=4)
            self.signos_fo_vars.append(signo_var)

            entry = ttk.Entry(fo_entries_frame, width=5)
            entry.pack(side="left", padx=2)
            self.entry_funcion_objetivo_vars.append(entry)

            ttk.Label(fo_entries_frame, text=f"X{i + 1}").pack(side="left")

    # En interfaz.py, reemplaza esta función

    def _generar_campos_restricciones(self):
        self.restricciones_data = []
        ttk.Label(self.frame_restricciones, text="Restricciones:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0,
                                                                                                       pady=10,
                                                                                                       sticky="w")

        for r_idx in range(self.num_restricciones_var.get()):
            row_frame = ttk.Frame(self.frame_restricciones)
            row_frame.grid(row=r_idx + 1, column=0, pady=2, sticky="w")

            entries, signos_vars = [], []
            for i in range(self.num_variables_var.get()):
                # --- CAMBIO CLAVE: Se quitó el "if i > 0" ---
                signo_var = tk.StringVar(value="+")
                signo_widget = ttk.Spinbox(
                    row_frame,
                    textvariable=signo_var,
                    values=("+", "-"),
                    width=2,
                    wrap=True,
                    state='readonly'
                )
                signo_widget.pack(side="left", padx=4)
                signos_vars.append(signo_var)

                entry = ttk.Entry(row_frame, width=5)
                entry.pack(side="left", padx=2)
                entries.append(entry)

                ttk.Label(row_frame, text=f"X{i + 1}").pack(side="left")

            signo_desigualdad_var = tk.StringVar(value="<=")
            ttk.OptionMenu(row_frame, signo_desigualdad_var, "<=", "<=", ">=", "=", style="Signo.TMenubutton").pack(
                side="left", padx=10)

            rhs_entry = ttk.Entry(row_frame, width=7)
            rhs_entry.pack(side="left", padx=2)

            self.restricciones_data.append({
                "coeficientes": entries,
                "signos_vars": signos_vars,
                "signo_desigualdad": signo_desigualdad_var,
                "rhs": rhs_entry
            })

    def calcular(self):
        datos_problema = self.obtener_datos_problema()
        if datos_problema:
            resultado = self.calcular_callback(datos_problema)
            self.mostrar_resultados(resultado)

    # En interfaz.py, reemplaza esta función

    def obtener_datos_problema(self):
        try:
            # Procesar función objetivo
            coef_fo = []
            for i, signo_var in enumerate(self.signos_fo_vars):
                val = float(self.entry_funcion_objetivo_vars[i].get())
                coef_fo.append(val if signo_var.get() == '+' else -val)

            # Procesar restricciones
            restricciones = []
            for r in self.restricciones_data:
                coef_r = []
                for i, signo_var in enumerate(r["signos_vars"]):
                    val = float(r["coeficientes"][i].get())
                    coef_r.append(val if signo_var.get() == '+' else -val)

                restricciones.append({
                    "coeficientes": coef_r,
                    "signo": r["signo_desigualdad"].get(),
                    "rhs": float(r["rhs"].get())
                })

            return {
                "tipo_optimizacion": self.tipo_optimizacion_var.get(),
                "funcion_objetivo": coef_fo,
                "restricciones": restricciones,
                "metodo": self.metodo_resolucion_var.get()
            }
        except (ValueError, IndexError):
            messagebox.showerror("Error de Entrada",
                                 "Por favor, ingrese valores numéricos válidos en todos los campos.")
            return None

    def reiniciar_interfaz(self):
        self.limpiar_resultados()
        for frame in [self.frame_funcion_objetivo, self.frame_restricciones]:
            for widget in frame.winfo_children(): widget.destroy()
        self.boton_resolver.grid_forget()
        self.num_variables_var.set(2);
        self.num_restricciones_var.set(3)
        self.metodo_resolucion_var.set("Simplex");
        self.actualizar_variables_metodo()

    def limpiar_resultados(self):
        for widget in self.frame_resultados.winfo_children(): widget.destroy()
        if hasattr(self, 'fig'): plt.close(self.fig)

    def mostrar_resultados(self, resultado):
        self.limpiar_resultados()
        if not resultado:
            return
        
        # Método Gráfico -> Mostrar gráfico
        if resultado.get('metodo') == "Gráfico":
            self.mostrar_resultados_grafico(resultado)
        
        # Simplex o Dos Fases -> Mostrar solo texto
        else:
            self.mostrar_resultados_simplex(resultado)

    def mostrar_resultados_simplex(self, resultado):
        text_frame = ttk.Frame(self.frame_resultados)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_resultados = tk.Text(text_frame, wrap="none", font=("Consolas", 10), bg=DARKER_BG, fg=LIGHT_TEXT, bd=0,
                                  highlightthickness=0)
        v_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_resultados.yview)
        h_scroll = ttk.Scrollbar(text_frame, orient="horizontal", command=text_resultados.xview)
        text_resultados.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.pack(side="right", fill="y");
        h_scroll.pack(side="bottom", fill="x");
        text_resultados.pack(fill="both", expand=True)

        text_resultados.insert(tk.END, "=== ANÁLISIS MÉTODO SIMPLEX ===\n\n", "title")
        historial = resultado.get('historial_iteraciones', [])
        if not historial:
            text_resultados.insert(tk.END, resultado.get('mensaje', 'No se generó historial.'), "error")
        else:
            for paso in historial:
                text_resultados.insert(tk.END, paso['descripcion'] + '\n', "descripcion")
                if paso.get('tableau') is not None:
                    tabla_str = self._formatear_tableau(paso['tableau'])
                    text_resultados.insert(tk.END, tabla_str + '\n\n', "tableau_font")

        if resultado.get('solucion_optima'):
            text_resultados.insert(tk.END, f"\n=== RESUMEN DE LA SOLUCIÓN ===\n", "title")
            text_resultados.insert(tk.END, f"Estado: {resultado.get('mensaje', '')}\n", "descripcion")
            text_resultados.insert(tk.END, f"Valor Óptimo de Z: {resultado.get('valor_optimo', 0):.4f}\n\n", "optimo")
            for var, val in resultado.get('variables', {}).items(): text_resultados.insert(tk.END,
                                                                                           f"{var} = {val:.4f}\n",
                                                                                           "descripcion")
        elif 'mensaje' in resultado:
            text_resultados.insert(tk.END, f"\nEstado final: {resultado['mensaje']}\n", "error")

        text_resultados.tag_config("title", font=("Segoe UI", 12, "bold"));
        text_resultados.tag_config("descripcion", font=("Segoe UI", 10))
        text_resultados.tag_config("optimo", font=("Segoe UI", 11, "bold"), foreground=ACCENT_COLOR);
        text_resultados.tag_config("error", foreground="#ff6b6b")
        text_resultados.tag_config("tableau_font", font=("Consolas", 10));
        text_resultados.config(state="disabled")

    def _formatear_tableau(self, tableau):
        num_vars = len(self.entry_funcion_objetivo_vars)
        num_rest = tableau.shape[0] - 1
        headers = ["Base", "Z"] + [f"X{i + 1}" for i in range(num_vars)] + [f"S{i + 1}" for i in range(num_rest)] + [
            "RHS"]
        base_vars = self._identificar_variables_base(tableau, num_vars, num_rest)

        filas_str = ["".join(f"{h:<9}" for h in headers), "-" * len(headers) * 9]
        for i, fila in enumerate(tableau):
            filas_str.append(f"{base_vars[i]:<9}" + "".join(f"{val:<9.2f}" for val in fila))
        return "\n".join(filas_str)

    def _identificar_variables_base(self, tableau, num_vars, num_rest):
        base_vars = [""] * (num_rest + 1);
        base_vars[0] = "Z"
        var_map = {i + 1: f"X{i + 1}" for i in range(num_vars)}
        var_map.update({1 + num_vars + i: f"S{i + 1}" for i in range(num_rest)})
        for col_idx in range(1, 1 + num_vars + num_rest):
            columna = tableau[1:, col_idx]
            if abs(np.sum(columna) - 1.0) < 1e-6 and np.count_nonzero(columna) == 1:
                fila_idx = np.where(abs(columna - 1.0) < 1e-6)[0][0] + 1
                base_vars[fila_idx] = var_map.get(col_idx, '')
        return base_vars

    def mostrar_resultados_grafico(self, resultado):
        fig, ax = plt.subplots(figsize=(6, 5), facecolor=DARKER_BG)
        fig.patch.set_facecolor(DARKER_BG)

        ax.set_title("Región Factible", color=LIGHT_TEXT);
        ax.set_xlabel("X1", color=LIGHT_TEXT);
        ax.set_ylabel("X2", color=LIGHT_TEXT)
        ax.grid(True, color=SECONDARY_COLOR, alpha=0.3);
        ax.axhline(0, color=LIGHT_TEXT, lw=0.5);
        ax.axvline(0, color=LIGHT_TEXT, lw=0.5)
        ax.set_facecolor(DARKER_BG);
        ax.tick_params(colors=LIGHT_TEXT)

        for r in resultado.get('restricciones_grafico', []): ax.plot(r['x_points'], r['y_points'], label=r['label'])
        sol_opt = resultado.get('solucion_optima')
        if sol_opt and 'punto' in sol_opt:
            x_opt, y_opt = sol_opt['punto']
            ax.plot(x_opt, y_opt, 'o', color=ACCENT_COLOR, markersize=8, label='Solución Óptima')
            ax.annotate(f'({x_opt:.2f}, {y_opt:.2f})', (x_opt, y_opt), textcoords="offset points", xytext=(10, 10),
                        ha='center', color='white')

        lims = resultado.get('limites', {'x_max': 10, 'y_max': 10});
        ax.set_xlim(0, lims['x_max']);
        ax.set_ylim(0, lims['y_max'])
        legend = ax.legend(facecolor=DARKER_BG, edgecolor=SECONDARY_COLOR)
        for text in legend.get_texts(): text.set_color(LIGHT_TEXT)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_resultados)
        canvas.draw();
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self.frame_resultados);
        toolbar.update()