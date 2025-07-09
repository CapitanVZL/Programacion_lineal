import tkinter as tk
from interfaz import InterfazProgramacionLineal
from metodografico import MetodoGrafico
from metodosimplex_manual import MetodoSimplexManual
from metodo_dosfases import MetodoDosFases

def main():
    """
    Función principal que inicia la aplicación.
    """
    root = tk.Tk()

    def calcular_callback(datos_problema):
        """
        Esta función se pasa a la interfaz y actúa como un "router".
        Decide qué clase de solucionador usar basado en la selección del usuario.
        """
        metodo_seleccionado = datos_problema.get('metodo')

        if metodo_seleccionado == "Gráfico":
            solver = MetodoGrafico()
        elif metodo_seleccionado == "Simplex":
            solver = MetodoSimplexManual()
        elif metodo_seleccionado == "Dos Fases":
            solver = MetodoDosFases()
        else:
            return {
                "solucion_optima": False,
                "mensaje": f'Método "{metodo_seleccionado}" no reconocido.',
                "historial_iteraciones": []
            }

        resultado = solver.resolver(datos_problema)
        resultado["metodo"] = metodo_seleccionado  # Asegurarse que esté incluido
        return resultado

    def post_wrap_calcular(datos):
        resultado = calcular_callback(datos)
        post_procesar_resultado(resultado)
        return resultado

    def post_procesar_resultado(resultado):
        if resultado.get("metodo") == "Dos Fases" and resultado.get("historial_iteraciones"):
            popup = tk.Toplevel()
            popup.title("Detalles del Método Dos Fases")
            popup.geometry("800x500")
            popup.configure(bg="#1e1e1e")

            text = tk.Text(popup, wrap="none", bg="#161616", fg="#f8f9fa", font=("Consolas", 10))
            text.pack(fill="both", expand=True)

            v_scroll = tk.Scrollbar(popup, orient="vertical", command=text.yview)
            v_scroll.pack(side="right", fill="y")
            text.configure(yscrollcommand=v_scroll.set)

            for paso in resultado["historial_iteraciones"]:
                text.insert("end", paso["descripcion"] + "\n\n")
                if paso.get("tableau") is not None:
                    text.insert("end", formatear_tableau_custom(paso["tableau"]) + "\n\n")

    def formatear_tableau_custom(tableau):
        if tableau is None:
            return ""
        num_filas, num_columnas = tableau.shape
        headers = ["Z"] + [f"X{i + 1}" for i in range(num_columnas - 2)] + ["RHS"]
        filas_str = ["".join(f"{h:<8}" for h in headers), "-" * len(headers) * 8]
        for fila in tableau:
            filas_str.append("".join(f"{val:<8.2f}" for val in fila))
        return "\n".join(filas_str)

    # Crear la interfaz con el callback envuelto
    app = InterfazProgramacionLineal(root, post_wrap_calcular)

    # Iniciar la aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
