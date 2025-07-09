import numpy as np
import tkinter as tk
from tkinter import ttk


class MetodoDosFases:
    def __init__(self):
        self.historial = []

    def resolver(self, datos_problema):
        self.historial = []
        texto_total = ""

        restricciones = datos_problema['restricciones']
        fo_original = datos_problema['funcion_objetivo'][:]
        num_vars = len(fo_original)
        tipo = datos_problema['tipo_optimizacion']

        A = []
        b = []
        signos = []
        for r in restricciones:
            A.append(r['coeficientes'])
            b.append(r['rhs'])
            signos.append(r['signo'])

        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)

        m, n = A.shape
        identidad = np.eye(m)
        columnas = []
        artificiales = []
        base = []
        col_index = n

        var_map = []  # Guarda nombres de columnas
        for i in range(n):
            var_map.append(f"X{i+1}")

        for i, signo in enumerate(signos):
            if signo == '<=':
                columnas.append(identidad[i])
                var_map.append(f"S{i+1}")
                base.append(f"S{i+1}")
                col_index += 1
            elif signo == '>=':
                columnas.append(-identidad[i])
                var_map.append(f"E{i+1}")
                columnas.append(identidad[i])
                var_map.append(f"A{i+1}")
                artificiales.append(len(var_map) - 1)
                base.append(f"A{i+1}")
                col_index += 2
            elif signo == '=':
                columnas.append(identidad[i])
                var_map.append(f"A{i+1}")
                artificiales.append(len(var_map) - 1)
                base.append(f"A{i+1}")
                col_index += 1

        if columnas:
            extras = np.column_stack(columnas)
            A_std = np.hstack((A, extras))
        else:
            A_std = A.copy()

        num_total_vars = A_std.shape[1]

        c_f1 = np.zeros(num_total_vars)
        for idx in artificiales:
            c_f1[idx] = 1

        Z = np.zeros(num_total_vars)
        for idx in artificiales:
            row_idx = base.index(var_map[idx])
            Z += A_std[row_idx]
        Z = -Z

        tableau = np.vstack([Z, A_std])
        tableau = np.hstack([tableau, np.vstack([[0], b.reshape(-1, 1)])])

        texto_total += "--- FASE 1 ---\n\n"
        iteracion = 1
        while any(val < 0 for val in tableau[0, :-1]):
            texto_total += f"--- ITERACIÓN {iteracion} ---\n"
            texto_total += self.formatear_tableau(var_map, base, tableau) + "\n\n"

            col_pivote = np.argmin(tableau[0, :-1])
            razones = []
            for i in range(1, tableau.shape[0]):
                if tableau[i, col_pivote] > 0:
                    razones.append(tableau[i, -1] / tableau[i, col_pivote])
                else:
                    razones.append(np.inf)
            fila_pivote = np.argmin(razones) + 1

            pivote = tableau[fila_pivote, col_pivote]
            tableau[fila_pivote] = tableau[fila_pivote] / pivote
            for i in range(tableau.shape[0]):
                if i != fila_pivote:
                    tableau[i] -= tableau[i, col_pivote] * tableau[fila_pivote]

            base[fila_pivote - 1] = var_map[col_pivote]
            iteracion += 1

        texto_total += f"--- ITERACIÓN {iteracion} (FINAL FASE 1) ---\n"
        texto_total += self.formatear_tableau(var_map, base, tableau) + "\n\n"

        texto_total += "--- FASE 2 ---\n\n"
        fo_completa = np.zeros(num_total_vars)
        fo_completa[:num_vars] = -np.array(fo_original)

        for i, var in enumerate(base):
            if var in var_map[:num_vars]:
                fo_completa += tableau[i+1, :-1] * fo_completa[var_map.index(var)]

        tableau[0, :-1] = fo_completa
        tableau[0, -1] = 0
        for i in range(1, tableau.shape[0]):
            if base[i - 1] in var_map[:num_vars]:
                tableau[0, -1] += tableau[i, -1] * fo_completa[var_map.index(base[i - 1])]

        iteracion = 1
        while any(val < 0 for val in tableau[0, :-1]):
            texto_total += f"--- ITERACIÓN {iteracion} ---\n"
            texto_total += self.formatear_tableau(var_map, base, tableau) + "\n\n"

            col_pivote = np.argmin(tableau[0, :-1])
            razones = []
            for i in range(1, tableau.shape[0]):
                if tableau[i, col_pivote] > 0:
                    razones.append(tableau[i, -1] / tableau[i, col_pivote])
                else:
                    razones.append(np.inf)
            fila_pivote = np.argmin(razones) + 1

            pivote = tableau[fila_pivote, col_pivote]
            tableau[fila_pivote] = tableau[fila_pivote] / pivote
            for i in range(tableau.shape[0]):
                if i != fila_pivote:
                    tableau[i] -= tableau[i, col_pivote] * tableau[fila_pivote]

            base[fila_pivote - 1] = var_map[col_pivote]
            iteracion += 1

        texto_total += f"--- ITERACIÓN {iteracion} (FINAL FASE 2) ---\n"
        texto_total += self.formatear_tableau(var_map, base, tableau) + "\n\n"

        texto_total += "--- SOLUCIÓN FINAL ---\n"
        texto_total += f"Valor óptimo de Z: {tableau[0, -1]:.4f}\n"
        for i, var in enumerate(base):
            texto_total += f"{var} = {tableau[i+1, -1]:.4f}\n"

        self.mostrar_resultados_en_ventana(texto_total)

        return {
            'metodo': 'Dos Fases',
            'valor_optimo': tableau[0, -1],
            'variables': {var: tableau[i+1, -1] for i, var in enumerate(base)}
        }

    def formatear_tableau(self, nombre_variables, base, tableau):
        headers = ["Base", "Z"] + nombre_variables + ["RHS"]
        filas_str = ["".join(f"{h:<9}" for h in headers), "-" * len(headers) * 9]
        for i, fila in enumerate(tableau):
            base_name = base[i - 1] if i > 0 else "Z"
            fila_str = f"{base_name:<9}" + "".join(f"{val:<9.2f}" for val in fila)
            filas_str.append(fila_str)
        return "\n".join(filas_str)

    def mostrar_resultados_en_ventana(self, texto):
        ventana = tk.Toplevel()
        ventana.title("Resultado Método Dos Fases")
        ventana.geometry("950x600")
        ventana.configure(bg="#1e1e1e")

        label = tk.Label(ventana, text="=== ANÁLISIS MÉTODO DOS FASES ===", fg="#3a86ff",
                         bg="#1e1e1e", font=("Segoe UI", 12, "bold"))
        label.pack(pady=10)

        text_widget = tk.Text(ventana, wrap="none", font=("Consolas", 10), bg="#161616", fg="#f8f9fa")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        text_widget.insert("end", texto)
        text_widget.config(state="disabled")

        y_scroll = ttk.Scrollbar(ventana, orient="vertical", command=text_widget.yview)
        y_scroll.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=y_scroll.set)
