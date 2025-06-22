import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        self.root.title("Programación Lineal - Método Gráfico")
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
    # Variables de control
        self.num_variables_var = tk.IntVar(value=2)
        self.num_restricciones_var = tk.IntVar(value=3)
        self.tipo_optimizacion_var = tk.StringVar(value="Maximizar")
    
    # Widgets de la interfaz
        self.crear_widgets_seleccion()
        self.crear_widgets_configuracion()
        self.crear_widgets_funcion_objetivo()
        self.crear_widgets_restricciones()
        self.crear_widgets_resultados()
    
    # Inicializar frames - SOLO OCULTAR LOS QUE EXISTEN
        self.frame_funcion_objetivo.grid_forget()
        self.frame_restricciones.grid_forget()
        self.frame_resultados.grid_forget()
    
    # No ocultar boton_calcular_final aquí porque aún no existe
    # Se creará más adelante en generar_campos_problema()

    def crear_widgets_seleccion(self):
        self.frame_seleccion = ttk.Frame(self.root, padding=10)
        self.frame_seleccion.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(self.frame_seleccion, text="Método Gráfico de Programación Lineal", 
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

    def crear_widgets_configuracion(self):
        self.frame_configuracion = ttk.Frame(self.root, padding=10)
        self.frame_configuracion.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Variables (fijo en 2 para método gráfico)
        ttk.Label(self.frame_configuracion, text="Variables (X1, X2):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.frame_configuracion, text="2").grid(row=0, column=1, padx=5, pady=5)
        
        # Restricciones
        ttk.Label(self.frame_configuracion, text="Cantidad de Restricciones:").grid(row=0, column=2, padx=5, pady=5)
        self.spinbox_restricciones = ttk.Spinbox(self.frame_configuracion, from_=1, to=10,
                                               textvariable=self.num_restricciones_var, width=5)
        self.spinbox_restricciones.grid(row=0, column=3, padx=5, pady=5)
        
        # Botón Aceptar
        self.boton_aceptar = ttk.Button(self.frame_configuracion, text="Generar Campos", 
                                      command=self.generar_campos_problema)
        self.boton_aceptar.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

    def crear_widgets_funcion_objetivo(self):
        self.frame_funcion_objetivo = ttk.Frame(self.root, padding=10)
        
        # Variables para almacenar los campos de entrada
        self.entry_funcion_objetivo_vars = []
        
    def crear_widgets_restricciones(self):
        self.frame_restricciones = ttk.Frame(self.root, padding=10)
        self.restricciones_data = []

    def crear_widgets_resultados(self):
        self.frame_resultados = ttk.Frame(self.root)
    
    # Variables para matplotlib
        self.fig = None
        self.ax = None
        self.canvas_widget = None
        self.toolbar = None
    
    # Área de texto para resultados
        self.text_frame = ttk.Frame(self.frame_resultados)
        self.scrollbar = ttk.Scrollbar(self.text_frame)
        self.text_resultados = tk.Text(self.text_frame, height=10, width=50, wrap="word", 
                                 font=("Segoe UI", 10), bg=DARKER_BG, fg=LIGHT_TEXT,
                                 insertbackground=LIGHT_TEXT, selectbackground=ACCENT_COLOR,
                                 yscrollcommand=self.scrollbar.set)
    
    # Inicializar el botón calcular_final aquí
        self.boton_calcular_final = ttk.Button(self.root, text="Resolver", style="Accent.TButton",
                                         command=self.calcular)
        
    def generar_campos_problema(self):
        num_rest = self.num_restricciones_var.get()
    
        if num_rest <= 0:
            messagebox.showwarning("Entrada Inválida", "La cantidad de restricciones debe ser mayor a cero.")
            return

    # Limpiar frames
        self.limpiar_frame(self.frame_funcion_objetivo)
        self.limpiar_frame(self.frame_restricciones)
        self.frame_funcion_objetivo.grid_forget()
        self.frame_restricciones.grid_forget()
    
    # No necesitamos ocultar boton_calcular_final aquí porque ya está creado
    # pero sí asegurarnos de que esté visible
        self.boton_calcular_final.grid(row=4, column=0, padx=10, pady=20, sticky="ew")

        # Limpiar resultados si existen
        self.limpiar_resultados()

        # Generar campos de la Función Objetivo
        self.generar_campos_funcion_objetivo()
        
        # Generar campos de Restricciones
        self.generar_campos_restricciones(num_rest)
        
        # Mostrar frames
        self.frame_funcion_objetivo.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_restricciones.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    def generar_campos_funcion_objetivo(self):
        self.entry_funcion_objetivo_vars = []
        
        ttk.Label(self.frame_funcion_objetivo, 
                 text="Función Objetivo:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=7, pady=5, sticky="w")

        # Dropdown para tipo de optimización
        optim_frame = ttk.Frame(self.frame_funcion_objetivo)
        optim_frame.grid(row=1, column=0, padx=2, pady=5)
        
        opciones_optimizacion = ["Maximizar", "Minimizar"]
        dropdown_optimizacion = ttk.OptionMenu(optim_frame, self.tipo_optimizacion_var, 
                                             self.tipo_optimizacion_var.get(), *opciones_optimizacion)
        dropdown_optimizacion.pack()
        
        ttk.Label(self.frame_funcion_objetivo, text="Z =", font=("Segoe UI", 10)).grid(row=1, column=1, padx=2, pady=5)

        # Campos para X1 y X2
        for i in range(2):  # Siempre 2 variables para método gráfico
            entry_coef = ttk.Entry(self.frame_funcion_objetivo, width=5)
            entry_coef.grid(row=1, column=2 + i * 3, padx=2, pady=5)
            self.entry_funcion_objetivo_vars.append(entry_coef)
            
            ttk.Label(self.frame_funcion_objetivo, text=f"X{i + 1}", 
                     font=("Segoe UI", 9)).grid(row=1, column=3 + i * 3, padx=2, pady=5)
            
            if i < 1:  # Solo un signo + entre X1 y X2
                ttk.Label(self.frame_funcion_objetivo, text="+", 
                         font=("Segoe UI", 9)).grid(row=1, column=4 + i * 3, padx=2, pady=5)

    def generar_campos_restricciones(self, num_rest):
        self.restricciones_data = []
        
        ttk.Label(self.frame_restricciones, text="Restricciones:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=7, pady=10, sticky="w")

        # Encabezados
        ttk.Label(self.frame_restricciones, text="X1", font=("Segoe UI", 9)).grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(self.frame_restricciones, text="+", font=("Segoe UI", 9)).grid(row=1, column=1, padx=2, pady=2)
        ttk.Label(self.frame_restricciones, text="X2", font=("Segoe UI", 9)).grid(row=1, column=2, padx=5, pady=2)
        ttk.Label(self.frame_restricciones, text="Signo", font=("Segoe UI", 9)).grid(row=1, column=3, padx=5, pady=2)
        ttk.Label(self.frame_restricciones, text="RHS", font=("Segoe UI", 9)).grid(row=1, column=4, padx=5, pady=2)

        opciones_desigualdad = ["<=", ">=", "="]

        for r_idx in range(num_rest):
            restriccion_entries_vars = []
            restriccion_signo_var = tk.StringVar(self.root, value="<=")

            # Coeficiente X1
            entry_coef1 = ttk.Entry(self.frame_restricciones, width=5)
            entry_coef1.grid(row=r_idx + 2, column=0, padx=2, pady=2)
            restriccion_entries_vars.append(entry_coef1)
            
            # Signo +
            ttk.Label(self.frame_restricciones, text="+").grid(row=r_idx + 2, column=1, padx=2, pady=2)
            
            # Coeficiente X2
            entry_coef2 = ttk.Entry(self.frame_restricciones, width=5)
            entry_coef2.grid(row=r_idx + 2, column=2, padx=2, pady=2)
            restriccion_entries_vars.append(entry_coef2)

            # Dropdown para signo de desigualdad
            signo_frame = ttk.Frame(self.frame_restricciones)
            signo_frame.grid(row=r_idx + 2, column=3, padx=5, pady=2)
            
            dropdown_signo = ttk.OptionMenu(signo_frame, restriccion_signo_var, 
                                          restriccion_signo_var.get(), *opciones_desigualdad)
            dropdown_signo.pack()

            # RHS
            entry_rhs = ttk.Entry(self.frame_restricciones, width=7)
            entry_rhs.grid(row=r_idx + 2, column=4, padx=5, pady=2)

            self.restricciones_data.append({
                "coeficientes": restriccion_entries_vars,
                "signo": restriccion_signo_var,
                "rhs": entry_rhs
            })

    def limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def limpiar_resultados(self):
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None

        if self.frame_resultados.winfo_children():
            self.limpiar_frame(self.frame_resultados)
        self.frame_resultados.grid_forget()

    def calcular(self):
        # Obtener datos de la interfaz
        datos_problema = self.obtener_datos_problema()
        
        if datos_problema is None:
            return  # Hubo un error en los datos
            
        # Llamar al callback con los datos del problema
        resultado = self.calcular_callback(datos_problema)
        
        # Mostrar resultados
        self.mostrar_resultados(resultado)

    def obtener_datos_problema(self):
        try:
            # Obtener tipo de optimización
            tipo_optimizacion = self.tipo_optimizacion_var.get()
            
            # Obtener coeficientes de la función objetivo
            coeficientes_fo = []
            for entry_coef in self.entry_funcion_objetivo_vars:
                coef = float(entry_coef.get())
                coeficientes_fo.append(coef)
                
            # Obtener restricciones
            restricciones = []
            for restriccion_info in self.restricciones_data:
                restriccion_actual = {
                    "coeficientes": [
                        float(restriccion_info["coeficientes"][0].get()),
                        float(restriccion_info["coeficientes"][1].get())
                    ],
                    "signo": restriccion_info["signo"].get(),
                    "rhs": float(restriccion_info["rhs"].get())
                }
                restricciones.append(restriccion_actual)
                
            return {
                "tipo_optimizacion": tipo_optimizacion,
                "funcion_objetivo": coeficientes_fo,
                "restricciones": restricciones
            }
            
        except ValueError as e:
            messagebox.showerror("Error de Entrada", "Por favor ingrese valores numéricos válidos en todos los campos.")
            return None

    def mostrar_resultados(self, resultado):
        # Limpiar resultados anteriores
        self.limpiar_resultados()
        
        # Configurar frame de resultados
        self.frame_resultados.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky="nsew")
        self.root.grid_columnconfigure(1, weight=1)
        self.frame_resultados.grid_rowconfigure(0, weight=1)
        self.frame_resultados.grid_rowconfigure(2, weight=1)
        
        # Mostrar gráfico
        self.mostrar_grafico(resultado)
        
        # Mostrar texto de resultados
        self.mostrar_texto_resultados(resultado)

    def mostrar_grafico(self, resultado):
        self.fig, self.ax = plt.subplots(figsize=(6, 5), facecolor=DARKER_BG)
        self.fig.patch.set_facecolor(DARKER_BG)

        # Configurar el gráfico
        self.ax.set_title("Región Factible", color=LIGHT_TEXT)
        self.ax.set_xlabel("X1", color=LIGHT_TEXT)
        self.ax.set_ylabel("X2", color=LIGHT_TEXT)
        self.ax.grid(True, color=SECONDARY_COLOR, alpha=0.3)
        self.ax.axhline(0, color=LIGHT_TEXT, linewidth=0.5)
        self.ax.axvline(0, color=LIGHT_TEXT, linewidth=0.5)
        self.ax.set_facecolor(DARKER_BG)
        self.ax.tick_params(colors=LIGHT_TEXT)

        # Graficar restricciones
        for idx, r in enumerate(resultado['restricciones_grafico']):
            x_points = r['x_points']
            y_points = r['y_points']
            label = r['label']
            self.ax.plot(x_points, y_points, label=label)

        # Graficar solución óptima si existe
        if resultado['solucion_optima']:
            x_opt, y_opt = resultado['solucion_optima']['punto']
            self.ax.plot(x_opt, y_opt, 'ro', markersize=8, label='Solución Óptima')
            
            # Etiqueta con los valores
            self.ax.annotate(f'({x_opt:.2f}, {y_opt:.2f})', 
                            (x_opt, y_opt),
                            textcoords="offset points", 
                            xytext=(10,10), 
                            ha='center',
                            color='white')

        # Configurar límites del gráfico
        self.ax.set_xlim(0, resultado['limites']['x_max'])
        self.ax.set_ylim(0, resultado['limites']['y_max'])

        # Configurar leyenda
        legend = self.ax.legend(facecolor=DARKER_BG, edgecolor=SECONDARY_COLOR)
        for text in legend.get_texts():
            text.set_color(LIGHT_TEXT)

        # Mostrar canvas
        canvas = FigureCanvasTkAgg(self.fig, master=self.frame_resultados)
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Barra de herramientas
        self.toolbar = NavigationToolbar2Tk(canvas, self.frame_resultados)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Cambiar color de fondo de la barra de herramientas
        for child in self.toolbar.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(background=DARKER_BG)

    def mostrar_texto_resultados(self, resultado):
        # Frame para texto y scrollbar
        self.text_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        # Scrollbar
        self.scrollbar.pack(side="right", fill="y")
        
        # Texto de resultados
        self.text_resultados.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.text_resultados.yview)
        
        # Insertar resultados
        self.text_resultados.config(state="normal")
        self.text_resultados.delete(1.0, tk.END)
        
        self.text_resultados.insert(tk.END, "=== RESULTADOS ===\n\n", "title")
        self.text_resultados.insert(tk.END, f"Tipo de Optimización: {resultado['tipo_optimizacion']}\n\n")
        
        if resultado['solucion_optima']:
            self.text_resultados.insert(tk.END, "Solución encontrada:\n", "subtitle")
            self.text_resultados.insert(tk.END, f"- X1 = {resultado['solucion_optima']['punto'][0]:.4f}\n")
            self.text_resultados.insert(tk.END, f"- X2 = {resultado['solucion_optima']['punto'][1]:.4f}\n")
            self.text_resultados.insert(tk.END, f"- Valor Óptimo (Z) = {resultado['solucion_optima']['valor_optimo']:.4f}\n\n")
        else:
            self.text_resultados.insert(tk.END, "No se encontró solución óptima.\n\n", "error")
            
        if resultado['mensaje']:
            self.text_resultados.insert(tk.END, f"Mensaje: {resultado['mensaje']}\n\n")
            
        self.text_resultados.insert(tk.END, "=== DETALLES ===\n\n", "title")
        self.text_resultados.insert(tk.END, "Vértices de la región factible:\n", "subtitle")
        for vertice in resultado['vertices']:
            self.text_resultados.insert(tk.END, f"- ({vertice[0]:.4f}, {vertice[1]:.4f})\n")
        
        self.text_resultados.config(state="disabled")
        self.text_resultados.tag_config("title", font=("Segoe UI", 10, "bold"))
        self.text_resultados.tag_config("subtitle", font=("Segoe UI", 10, "underline"))
        self.text_resultados.tag_config("error", foreground="#ff6b6b")