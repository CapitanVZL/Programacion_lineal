from interfaz import InterfazProgramacionLineal
from metodografico import MetodoGrafico
import tkinter as tk

def main():
    root = tk.Tk()
    
    # Crear instancia del método gráfico
    metodo_grafico = MetodoGrafico()
    
    # Función callback que conecta la interfaz con el método gráfico
    def calcular_callback(datos_problema):
        return metodo_grafico.resolver(datos_problema)
    
    # Crear interfaz
    app = InterfazProgramacionLineal(root, calcular_callback)
    
    # Ejecutar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()