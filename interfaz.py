import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

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
        self.style.map("TButton", 
                      background=[('active', "#343a40"), ('pressed', "#495057")],
                      foreground=[('active', LIGHT_TEXT), ('pressed', LIGHT_TEXT)])
        
        self.style.configure("Accent.TButton", background=ACCENT_COLOR, foreground=LIGHT_TEXT,
                           font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", 
                      background=[('active', '#2563eb'), ('pressed', '#1e40af')])

    def configurar_interfaz(self):
        self.root.title("Programación Lineal - Solver")
        self.root.geometry("1200x700")
        self.root.configure(bg=DARK_BG)
        
        # Configurar grid principal
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        # Configurar matplotlib para modo oscuro
        plt.style.use('dark_background')

    def variables_interfaz(self):
        self.num_variables_var = tk.IntVar(value=2)
        self.num_restricciones_var = tk.IntVar(value=3)
        self.tipo_optimizacion_var = tk.StringVar(value="Maximizar")
        self.metodo_resolucion_var = tk.StringVar(value="Gráfico")
        
        self.crear_widgets_seleccion()
        self.crear_widgets_configuracion()
        self.crear_widgets_funcion_objetivo()
        self.crear_widgets_restricciones()
        self.crear_widgets_resultados()
        
        self.frame_funcion_objetivo.grid_forget()
        self.frame_restricciones.grid_forget()
        self.frame_resultados.grid_forget()

    def crear_widgets_seleccion(self):
        self.frame_seleccion = ttk.Frame(self.root, padding=10)
        self.frame_seleccion.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(self.frame_seleccion, text="Solver de Programación Lineal", 
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

    def crear_widgets_configuracion(self):
        self.frame_configuracion = ttk.Frame(self.root, padding=10)
        self.frame_configuracion.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Método de resolución
        ttk.Label(self.frame_configuracion, text="Método:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_metodo = ttk.Combobox(self.frame_configuracion, 
                                       textvariable=self.metodo_resolucion_var,
                                       values=["Gráfico", "Simplex"], 
                                       state="readonly", width=8)
        self.combo_metodo.grid(row=0, column=1, padx=5, pady=5)
        self.combo_metodo.bind("<<ComboboxSelected>>", self.actualizar_variables_metodo)
        
        # Variables
        ttk.Label(self.frame_configuracion, text="Variables:").grid(row=0, column=2, padx=5, pady=5)
        self.spinbox_variables = ttk.Spinbox(self.frame_configuracion, from_=2, to=10,
                                          textvariable=self.num_variables_var, width=5)
        self.spinbox_variables.grid(row=0, column=3, padx=5, pady=5)
        
        # Restricciones
        ttk.Label(self.frame_configuracion, text="Restricciones:").grid(row=0, column=4, padx=5, pady=5)
        self.spinbox_restricciones = ttk.Spinbox(self.frame_configuracion, from_=1, to=10,
                                              textvariable=self.num_restricciones_var, width=5)
        self.spinbox_restricciones.grid(row=0, column=5, padx=5, pady=5)
        
        # Botón Aceptar
        self.boton_aceptar = ttk.Button(self.frame_configuracion, text="Generar Campos", 
                                      command=self.generar_campos_problema)
        self.boton_aceptar.grid(row=1, column=0, columnspan=6, pady=10, sticky="ew")

    def actualizar_variables_metodo(self, event=None):
        if self.metodo_resolucion_var.get() == "Gráfico":
            self.num_variables_var.set(2)
            self.spinbox_variables.config(state="disabled")
        else:
            self.spinbox_variables.config(state="normal")

    def generar_campos_problema(self):
        num_vars = self.num_variables_var.get()
        num_rest = self.num_restricciones_var.get()

        if num_rest <= 0:
            messagebox.showwarning("Error", "Debe haber al menos 1 restricción")
            return

        self.limpiar_frame(self.frame_funcion_objetivo)
        self.limpiar_frame(self.frame_restricciones)
        
        self.generar_campos_funcion_objetivo()
        self.generar_campos_restricciones(num_rest)
        
        self.frame_funcion_objetivo.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_restricciones.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.boton_calcular_final.grid(row=4, column=0, padx=10, pady=20, sticky="ew")

    def limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def limpiar_resultados(self):
        if hasattr(self, 'canvas_widget') and self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        if hasattr(self, 'toolbar') and self.toolbar:
            self.toolbar.destroy()
        if hasattr(self, 'fig') and self.fig:
            plt.close(self.fig)
        
        if hasattr(self, 'frame_resultados') and self.frame_resultados.winfo_children():
            self.limpiar_frame(self.frame_resultados)
        
        self.frame_resultados.grid_forget()

    def crear_widgets_funcion_objetivo(self):
        self.frame_funcion_objetivo = ttk.Frame(self.root, padding=10)
        self.entry_funcion_objetivo_vars = []

    def crear_widgets_restricciones(self):
        self.frame_restricciones = ttk.Frame(self.root, padding=10)
        self.restricciones_data = []

    def crear_widgets_resultados(self):
        self.frame_resultados = ttk.Frame(self.root)
        self.boton_calcular_final = ttk.Button(self.root, text="Resolver", style="Accent.TButton",
                                         command=self.calcular)

    def generar_campos_funcion_objetivo(self):
        self.entry_funcion_objetivo_vars = []
        
        ttk.Label(self.frame_funcion_objetivo, 
                 text="Función Objetivo:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=7, pady=5, sticky="w")

        optim_frame = ttk.Frame(self.frame_funcion_objetivo)
        optim_frame.grid(row=1, column=0, padx=2, pady=5)
        
        opciones_optimizacion = ["Maximizar", "Minimizar"]
        dropdown_optimizacion = ttk.OptionMenu(optim_frame, self.tipo_optimizacion_var, 
                                             self.tipo_optimizacion_var.get(), *opciones_optimizacion)
        dropdown_optimizacion.pack()
        
        ttk.Label(self.frame_funcion_objetivo, text="Z =", font=("Segoe UI", 10)).grid(row=1, column=1, padx=2, pady=5)

        for i in range(self.num_variables_var.get()):
            entry_coef = ttk.Entry(self.frame_funcion_objetivo, width=5)
            entry_coef.grid(row=1, column=2 + i * 3, padx=2, pady=5)
            self.entry_funcion_objetivo_vars.append(entry_coef)
            
            ttk.Label(self.frame_funcion_objetivo, text=f"X{i + 1}", 
                     font=("Segoe UI", 9)).grid(row=1, column=3 + i * 3, padx=2, pady=5)
            
            if i < self.num_variables_var.get() - 1:
                ttk.Label(self.frame_funcion_objetivo, text="+", 
                         font=("Segoe UI", 9)).grid(row=1, column=4 + i * 3, padx=2, pady=5)

    def generar_campos_restricciones(self, num_rest):
        self.restricciones_data = []
        
        ttk.Label(self.frame_restricciones, text="Restricciones:", 
                font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=3 + self.num_variables_var.get(), pady=10, sticky="w")

        # Encabezados de variables (X1, X2, X3...)
        for i in range(self.num_variables_var.get()):
            ttk.Label(self.frame_restricciones, text=f"X{i+1}", font=("Segoe UI", 9)).grid(row=1, column=i*2, padx=5, pady=2)
            if i < self.num_variables_var.get() - 1:
                ttk.Label(self.frame_restricciones, text="+", font=("Segoe UI", 9)).grid(row=1, column=i*2 + 1, padx=2, pady=2)

        # Encabezados fijos (Signo y RHS)
        ttk.Label(self.frame_restricciones, text="Signo", font=("Segoe UI", 9)).grid(row=1, column=self.num_variables_var.get()*2, padx=5, pady=2)
        ttk.Label(self.frame_restricciones, text="RHS", font=("Segoe UI", 9)).grid(row=1, column=self.num_variables_var.get()*2 + 1, padx=5, pady=2)

        opciones_desigualdad = ["<=", ">=", "="]

        for r_idx in range(num_rest):
            restriccion_entries_vars = []
            restriccion_signo_var = tk.StringVar(self.root, value="<=")

            # Campos para coeficientes (X1, X2, X3...)
            for i in range(self.num_variables_var.get()):
                entry_coef = ttk.Entry(self.frame_restricciones, width=5)
                entry_coef.grid(row=r_idx + 2, column=i*2, padx=2, pady=2)
                restriccion_entries_vars.append(entry_coef)
                
                if i < self.num_variables_var.get() - 1:
                    ttk.Label(self.frame_restricciones, text="+").grid(row=r_idx + 2, column=i*2 + 1, padx=2, pady=2)

            # Dropdown para signo
            signo_frame = ttk.Frame(self.frame_restricciones)
            signo_frame.grid(row=r_idx + 2, column=self.num_variables_var.get()*2, padx=5, pady=2)
            dropdown_signo = ttk.OptionMenu(signo_frame, restriccion_signo_var, restriccion_signo_var.get(), *opciones_desigualdad)
            dropdown_signo.pack()

            # Campo RHS
            entry_rhs = ttk.Entry(self.frame_restricciones, width=7)
            entry_rhs.grid(row=r_idx + 2, column=self.num_variables_var.get()*2 + 1, padx=5, pady=2)

            self.restricciones_data.append({
                "coeficientes": restriccion_entries_vars,
                "signo": restriccion_signo_var,
                "rhs": entry_rhs
            })

    def calcular(self):
        datos_problema = self.obtener_datos_problema()
        
        if datos_problema is None:
            return
            
        resultado = self.calcular_callback(datos_problema)
        self.mostrar_resultados(resultado)

    def obtener_datos_problema(self):
        try:
            tipo_optimizacion = self.tipo_optimizacion_var.get()
            
            coeficientes_fo = []
            for entry_coef in self.entry_funcion_objetivo_vars:
                coef = float(entry_coef.get())
                coeficientes_fo.append(coef)
                
            restricciones = []
            for restriccion_info in self.restricciones_data:
                coeficientes = [float(entry.get()) for entry in restriccion_info["coeficientes"]]
                restriccion_actual = {
                    "coeficientes": coeficientes,
                    "signo": restriccion_info["signo"].get(),
                    "rhs": float(restriccion_info["rhs"].get())
                }
                restricciones.append(restriccion_actual)
                
            return {
                "tipo_optimizacion": tipo_optimizacion,
                "funcion_objetivo": coeficientes_fo,
                "restricciones": restricciones,
                "metodo": self.metodo_resolucion_var.get()
            }
            
        except ValueError as e:
            messagebox.showerror("Error de Entrada", "Por favor ingrese valores numéricos válidos en todos los campos.")
            return None

    def mostrar_resultados(self, resultado):
        self.limpiar_resultados()
        self.frame_resultados.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky="nsew")
        
        if resultado.get('metodo') == 'Simplex':
            self.mostrar_resultados_simplex(resultado)
        else:
            self.mostrar_resultados_grafico(resultado)

    def mostrar_resultados_simplex(self, resultado):
        text_frame = ttk.Frame(self.frame_resultados)
        text_frame.grid(row=0, column=0, sticky="nsew")
        
        text_resultados = tk.Text(text_frame, height=15, width=60, wrap="word", 
                                font=("Consolas", 10), bg=DARKER_BG, fg=LIGHT_TEXT)
        scrollbar = ttk.Scrollbar(text_frame, command=text_resultados.yview)
        text_resultados.config(yscrollcommand=scrollbar.set)
        
        text_resultados.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        text_resultados.insert(tk.END, "=== RESULTADOS (SIMPLEX) ===\n\n", "title")
        if resultado['solucion_optima']:
            text_resultados.insert(tk.END, f"Valor Óptimo: {resultado['valor_optimo']:.4f}\n\n", "optimo")
            for var, val in resultado['variables'].items():
                text_resultados.insert(tk.END, f"{var} = {val:.4f}\n")
        else:
            text_resultados.insert(tk.END, resultado['mensaje'] + "\n", "error")
        
        text_resultados.tag_config("title", font=("Segoe UI", 11, "bold"))
        text_resultados.tag_config("optimo", foreground=ACCENT_COLOR)
        text_resultados.tag_config("error", foreground="#ff6b6b")
        text_resultados.config(state="disabled")

    def mostrar_resultados_grafico(self, resultado):
        self.fig, self.ax = plt.subplots(figsize=(6, 5), facecolor=DARKER_BG)
        self.fig.patch.set_facecolor(DARKER_BG)

        self.ax.set_title("Región Factible", color=LIGHT_TEXT)
        self.ax.set_xlabel("X1", color=LIGHT_TEXT)
        self.ax.set_ylabel("X2", color=LIGHT_TEXT)
        self.ax.grid(True, color=SECONDARY_COLOR, alpha=0.3)
        self.ax.axhline(0, color=LIGHT_TEXT, linewidth=0.5)
        self.ax.axvline(0, color=LIGHT_TEXT, linewidth=0.5)
        self.ax.set_facecolor(DARKER_BG)
        self.ax.tick_params(colors=LIGHT_TEXT)

        for idx, r in enumerate(resultado['restricciones_grafico']):
            x_points = r['x_points']
            y_points = r['y_points']
            label = r['label']
            self.ax.plot(x_points, y_points, label=label)

        if resultado['solucion_optima']:
            x_opt, y_opt = resultado['solucion_optima']['punto']
            self.ax.plot(x_opt, y_opt, 'ro', markersize=8, label='Solución Óptima')
            self.ax.annotate(f'({x_opt:.2f}, {y_opt:.2f})', 
                            (x_opt, y_opt),
                            textcoords="offset points", 
                            xytext=(10,10), 
                            ha='center',
                            color='white')

        self.ax.set_xlim(0, resultado['limites']['x_max'])
        self.ax.set_ylim(0, resultado['limites']['y_max'])

        legend = self.ax.legend(facecolor=DARKER_BG, edgecolor=SECONDARY_COLOR)
        for text in legend.get_texts():
            text.set_color(LIGHT_TEXT)

        canvas = FigureCanvasTkAgg(self.fig, master=self.frame_resultados)
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.toolbar = NavigationToolbar2Tk(canvas, self.frame_resultados)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        for child in self.toolbar.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(background=DARKER_BG)