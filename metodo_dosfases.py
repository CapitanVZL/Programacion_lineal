import numpy as np
import tkinter as tk
from tkinter import ttk

class MetodoDosFases:
    def __init__(self):
        self.tableau = None
        self.c = None
        self.artificiales = []
        self.fase = 1
        self.historial = []
        self.num_variables = 0
        self.num_restricciones = 0
        self.nombres_columnas = []

    def resolver(self, datos_problema):
        self.historial = []
        self.c = np.array(datos_problema['funcion_objetivo'])
        A = np.array([r['coeficientes'] for r in datos_problema['restricciones']])
        b = np.array([r['rhs'] for r in datos_problema['restricciones']])
        signos = [r['signo'] for r in datos_problema['restricciones']]
        self.num_variables = len(self.c)
        self.num_restricciones = len(b)

        # Initialize column names
        self._inicializar_nombres_columnas(signos)

        # --- Phase 1 ---
        self.historial.append({
            "descripcion": "=== FASE 1: Minimizar suma de variables artificiales ===",
            "tableau": None,
            "nombres_columnas": self.nombres_columnas
        })
        
        self._inicializar_fase1(A, b, signos)
        
        self.historial.append({
            "descripcion": "Tableau inicial Fase 1:",
            "tableau": self.tableau.copy(),
            "nombres_columnas": self.nombres_columnas
        })

        if not self._ejecutar_simplex(fase=1):
            self._mostrar_resultados("Problema no factible (Fase 1 no alcanzó Z=0).")
            return {
                "solucion_optima": False,
                "mensaje": "Problema no factible",
                "historial_iteraciones": self.historial,
                "metodo": "Dos Fases"
            }

        # --- Phase 2 ---
        self.historial.append({
            "descripcion": "\n=== FASE 2: Optimizar función objetivo original ===",
            "tableau": None,
            "nombres_columnas": [col for i, col in enumerate(self.nombres_columnas) 
                                if i not in self.artificiales]
        })
        
        self._inicializar_fase2()
        
        self.historial.append({
            "descripcion": "Tableau inicial Fase 2:",
            "tableau": self.tableau.copy(),
            "nombres_columnas": [col for i, col in enumerate(self.nombres_columnas) 
                                if i not in self.artificiales]
        })

        if not self._ejecutar_simplex(fase=2):
            self._mostrar_resultados("Problema no acotado.")
            return {
                "solucion_optima": False,
                "mensaje": "Problema no acotado",
                "historial_iteraciones": self.historial,
                "metodo": "Dos Fases"
            }

        resultado = self._generar_resultado_final()
        self._mostrar_resultados(self._generar_texto_resultado(resultado))
        return resultado

    def _inicializar_nombres_columnas(self, signos):
        """Generate column names: X1, X2, S1 (slack), E1 (excess), A1 (artificial)"""
        self.nombres_columnas = ["Z"] + [f"X{i+1}" for i in range(self.num_variables)]
        
        # Slack/excess/artificial variables
        contador_holgura = 1
        contador_artificial = 1
        for s in signos:
            if s == "<=":
                self.nombres_columnas.append(f"S{contador_holgura}")
                contador_holgura += 1
            elif s == ">=":
                self.nombres_columnas.append(f"E{contador_holgura}")  # Excess
                self.nombres_columnas.append(f"A{contador_artificial}")  # Artificial
                contador_holgura += 1
                contador_artificial += 1
            elif s == "=":
                self.nombres_columnas.append(f"A{contador_artificial}")
                contador_artificial += 1
                
        self.nombres_columnas.append("RHS")

    def _inicializar_fase1(self, A, b, signos):
        num_artificiales = sum(1 for s in signos if s in (">=", "="))
        total_columnas = 1 + self.num_variables + self.num_restricciones + num_artificiales + 1
        self.tableau = np.zeros((self.num_restricciones + 1, total_columnas))
        
        # Configure Phase 1 objective row (minimize sum of artificials)
        self.tableau[0, 0] = 1  # Z
        
        # Artificial variables (columns)
        self.artificiales = []
        col_artificial = 1 + self.num_variables + self.num_restricciones
        
        # Fill constraints
        for i in range(self.num_restricciones):
            # Original variables coefficients
            self.tableau[i+1, 1:1+self.num_variables] = A[i]
            
            # Slack/excess variables
            col_s = 1 + self.num_variables + i
            if signos[i] == "<=":
                self.tableau[i+1, col_s] = 1  # Slack
            elif signos[i] == ">=":
                self.tableau[i+1, col_s] = -1  # Excess
                # Artificial variable
                self.tableau[i+1, col_artificial] = 1
                self.artificiales.append(col_artificial)
                col_artificial += 1
            elif signos[i] == "=":
                # Artificial variable
                self.tableau[i+1, col_artificial] = 1
                self.artificiales.append(col_artificial)
                col_artificial += 1
            
            # Right-hand side
            self.tableau[i+1, -1] = b[i]
        
        # Configure Phase 1 objective (coefficients 1 for artificials)
        for col in self.artificiales:
            self.tableau[0, col] = 1
        
        # Subtract artificial rows from Z row to get zero reduced costs
        for col in self.artificiales:
            for row in range(1, self.num_restricciones + 1):
                if self.tableau[row, col] == 1:
                    self.tableau[0, :] -= self.tableau[row, :]
                    break

    def _inicializar_fase2(self):
        # Remove artificial variables columns
        columnas_a_mantener = [col for col in range(self.tableau.shape[1]) if col not in self.artificiales]
        self.tableau = self.tableau[:, columnas_a_mantener]
        
        # Restore original objective function
        self.tableau[0, 0] = 1  # Z
        self.tableau[0, 1:1+self.num_variables] = -self.c  # Negative because it's maximization
        
        # Ensure zero reduced cost for basic variables
        for col in range(1, self.tableau.shape[1]):
            if np.sum(self.tableau[1:, col]) == 1 and np.count_nonzero(self.tableau[1:, col]) == 1:
                row = np.where(self.tableau[1:, col] == 1)[0][0] + 1
                self.tableau[0, :] -= self.tableau[0, col] * self.tableau[row, :]

    def _ejecutar_simplex(self, fase):
        iteracion = 1
        while True:
            if self._condicion_de_parada(fase):
                break

            col_pivote = self._encontrar_columna_pivote(fase)
            fila_pivote = self._encontrar_fila_pivote(col_pivote)
            
            if fila_pivote == -1:
                self.historial.append({
                    "descripcion": f"Fase {fase} - Iteración {iteracion}:\nSolución no acotada.",
                    "tableau": self.tableau.copy(),
                    "nombres_columnas": self.nombres_columnas if fase == 1 else 
                                       [col for i, col in enumerate(self.nombres_columnas) 
                                        if i not in self.artificiales]
                })
                return False

            # Name of leaving variable
            if fase == 1:
                var_sale = f"S{fila_pivote}" if fila_pivote <= self.num_restricciones else f"R{fila_pivote}"
            else:
                col_basica = np.where(self.tableau[fila_pivote, 1:-1] == 1)[0][0] + 1
                var_sale = self.nombres_columnas[col_basica]

            self.historial.append({
                "descripcion": f"Fase {fase} - Iteración {iteracion}:\n"
                              f"Variable entra: {self.nombres_columnas[col_pivote]}\n"
                              f"Variable sale: {var_sale}\n"
                              f"Elemento pivote: {self.tableau[fila_pivote, col_pivote]:.4f}",
                "tableau": self.tableau.copy(),
                "nombres_columnas": self.nombres_columnas if fase == 1 else 
                                   [col for i, col in enumerate(self.nombres_columnas) 
                                    if i not in self.artificiales]
            })

            self._realizar_pivote(fila_pivote, col_pivote)
            iteracion += 1
            
            # Safety limit
            if iteracion > 100:
                self.historial.append({
                    "descripcion": f"Fase {fase} - Iteración {iteracion}:\n"
                                  "Se detuvo por alcanzar el límite de iteraciones.",
                    "tableau": self.tableau.copy(),
                    "nombres_columnas": self.nombres_columnas if fase == 1 else 
                                       [col for i, col in enumerate(self.nombres_columnas) 
                                        if i not in self.artificiales]
                })
                return False

        return True

    def _condicion_de_parada(self, fase):
        return np.all(self.tableau[0, 1:-1] >= -1e-6)

    def _encontrar_columna_pivote(self, fase):
        return np.argmin(self.tableau[0, 1:-1]) + 1

    def _encontrar_fila_pivote(self, col_pivote):
        columna = self.tableau[1:, col_pivote]
        rhs = self.tableau[1:, -1]
        ratios = np.full_like(rhs, np.inf)
        np.divide(rhs, columna, out=ratios, where=columna > 1e-6)
        if np.all(np.isinf(ratios)):
            return -1
        return np.argmin(ratios) + 1

    def _realizar_pivote(self, fila_pivote, col_pivote):
        pivote = self.tableau[fila_pivote, col_pivote]
        self.tableau[fila_pivote, :] /= pivote
        for i in range(self.tableau.shape[0]):
            if i != fila_pivote:
                factor = self.tableau[i, col_pivote]
                self.tableau[i, :] -= factor * self.tableau[fila_pivote, :]

    def _generar_resultado_final(self):
        solucion = {}
        for i in range(self.num_variables):
            col = i + 1
            columna = self.tableau[:, col]
            if np.sum(columna) == 1 and np.count_nonzero(columna) == 1:
                fila = np.where(columna == 1)[0][0] + 1
                solucion[f"X{i + 1}"] = self.tableau[fila, -1]
            else:
                solucion[f"X{i + 1}"] = 0.0

        self.historial.append({
            "descripcion": "=== SOLUCIÓN ÓPTIMA ENCONTRADA ===",
            "tableau": None,
            "nombres_columnas": [col for i, col in enumerate(self.nombres_columnas) 
                                if i not in self.artificiales]
        })

        return {
            "solucion_optima": True,
            "valor_optimo": self.tableau[0, -1],
            "variables": solucion,
            "mensaje": "Solución óptima encontrada con Método de Dos Fases.",
            "historial_iteraciones": self.historial,
            "metodo": "Dos Fases"
        }

    def _formatear_tableau(self, tableau, nombres_columnas):
        """Format tableau as text for display"""
        headers = ["Base"] + nombres_columnas
        ancho_col = max(10, max(len(h) for h in headers) + 2)
        
        # Build rows
        filas = []
        fila_z = ["Z"] + [f"{val:.4f}" for val in tableau[0, :]]
        filas.append(fila_z)
        
        for i in range(1, tableau.shape[0]):
            # Find basic variable
            col_basica = np.where(tableau[i, 1:-1] == 1)[0]
            nombre_fila = nombres_columnas[col_basica[0]+1] if len(col_basica) > 0 else f"R{i}"
            fila = [nombre_fila] + [f"{val:.4f}" for val in tableau[i, :]]
            filas.append(fila)
        
        # Align text
        tabla_str = "  ".join(h.ljust(ancho_col) for h in headers) + "\n"
        tabla_str += "-" * (len(headers) * ancho_col) + "\n"
        for fila in filas:
            tabla_str += "  ".join(val.ljust(ancho_col) for val in fila) + "\n"
        
        return tabla_str

    def _mostrar_resultados(self, texto):
        ventana = tk.Toplevel()
        ventana.title("Resultados - Método de Dos Fases")
        ventana.geometry("1000x700")
        
        # Main frame
        frame = ttk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Text area with scroll
        text_widget = tk.Text(frame, wrap=tk.NONE, font=('Consolas', 10))
        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        text_widget.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Grid layout
        text_widget.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')

        # Configure expansion
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Insert text
        text_widget.insert(tk.END, texto)
        text_widget.config(state=tk.DISABLED)

        # Close button
        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)

    def _generar_texto_resultado(self, resultado):
        texto = "=== RESULTADOS MÉTODO DE DOS FASES ===\n\n"
        
        if not resultado["solucion_optima"]:
            texto += f"✖ {resultado['mensaje']}\n"
            return texto

        # Show iteration history
        for paso in self.historial:
            texto += f"\n{paso['descripcion']}\n"
            if paso.get("tableau") is not None:
                texto += self._formatear_tableau(paso["tableau"], paso["nombres_columnas"]) + "\n"

        # Show final solution
        texto += "\n★ SOLUCIÓN ÓPTIMA ★\n"
        texto += f"Valor óptimo: {resultado['valor_optimo']:.4f}\n"
        for var, val in resultado["variables"].items():
            texto += f"{var} = {val:.4f}\n"
        
        return texto