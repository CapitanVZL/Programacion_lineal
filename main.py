# main.py

import tkinter as tk
from interfaz import InterfazProgramacionLineal
from metodografico import MetodoGrafico
# Renombramos MetodoSimplexManual a MetodoSimplexSimple para claridad
from metodosimplex_manual import MetodoSimplexManual as MetodoSimplexSimple
from metodo_dosfases import MetodoDosFases

def main():
    root = tk.Tk()

    def calcular_callback(datos_problema):
        metodo = datos_problema.get('metodo')

        if metodo == "Gráfico":
            solver = MetodoGrafico()
        elif metodo == "Simplex":
            # El Simplex simple solo funciona para <=
            if any(r['signo'] != '<=' for r in datos_problema['restricciones']):
                # Si hay >= o =, automáticamente usamos Dos Fases
                solver = MetodoDosFases()
            else:
                solver = MetodoSimplexSimple()
        elif metodo == "Dos Fases":
            solver = MetodoDosFases()
        else:
            return {"solucion_optima": False, "mensaje": "Método no reconocido."}

        return solver.resolver(datos_problema)

    app = InterfazProgramacionLineal(root, calcular_callback)
    root.mainloop()

if __name__ == "__main__":
    main()