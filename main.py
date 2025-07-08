import tkinter as tk
from interfaz import InterfazProgramacionLineal
from metodografico import MetodoGrafico
from metodosimplex_manual import MetodoSimplexManual  # Usamos la versión manual
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
            # ¡Importante! Aquí usamos la clase que implementa el algoritmo manualmente.
            solver = MetodoSimplexManual()
        elif metodo_seleccionado == "Dos Fases":
            solver = MetodoDosFases()
        else:
            # Manejo de error por si se añade un método no implementado
            return {
                "solucion_optima": False,
                "mensaje": f'Método "{metodo_seleccionado}" no reconocido.',
                "historial_iteraciones": []
            }

        return solver.resolver(datos_problema)

    # Creamos la instancia de la aplicación, pasándole la raíz de Tkinter y nuestra función de callback.
    app = InterfazProgramacionLineal(root, calcular_callback)
    # Iniciamos el bucle principal de la interfaz gráfica.
    root.mainloop()

if __name__ == "__main__":
    main()