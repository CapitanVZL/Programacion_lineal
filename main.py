from interfaz import InterfazProgramacionLineal
from metodografico import MetodoGrafico
from metodosimplex import MetodoSimplex
import tkinter as tk

def main():
    root = tk.Tk()
    
    def calcular_callback(datos_problema):
        if datos_problema.get('metodo') == "Gráfico":
            metodo = MetodoGrafico()
        else:
            metodo = MetodoSimplex()
        return metodo.resolver(datos_problema)
    
    app = InterfazProgramacionLineal(root, calcular_callback)
    root.mainloop()

if __name__ == "__main__":
    main()