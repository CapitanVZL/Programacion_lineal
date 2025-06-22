from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, LpStatus

class MetodoSimplex:
    def __init__(self):
        self.problema = None
        self.variables = []

    def resolver(self, datos_problema):
        self.crear_problema(datos_problema)
        self.agregar_restricciones(datos_problema['restricciones'])
        self.problema.solve()
        
        return self.obtener_resultados()

    def crear_problema(self, datos_problema):
        sentido = LpMaximize if datos_problema['tipo_optimizacion'] == "Maximizar" else LpMinimize
        self.problema = LpProblem("Problema_Simplex", sentido)
        
        num_variables = len(datos_problema['funcion_objetivo'])
        self.variables = [LpVariable(f"X{i+1}", lowBound=0) for i in range(num_variables)]
        
        objetivo = sum(coef * var for coef, var in zip(datos_problema['funcion_objetivo'], self.variables))
        self.problema += objetivo, "Z"

    def agregar_restricciones(self, restricciones):
        for i, r in enumerate(restricciones, 1):
            expr = sum(coef * var for coef, var in zip(r['coeficientes'], self.variables))
            if r['signo'] == "<=":
                self.problema += expr <= r['rhs'], f"R{i}"
            elif r['signo'] == ">=":
                self.problema += expr >= r['rhs'], f"R{i}"
            else:
                self.problema += expr == r['rhs'], f"R{i}"

    def obtener_resultados(self):
        return {
            'status': LpStatus[self.problema.status],
            'solucion_optima': self.problema.status == 1,
            'variables': {var.name: var.varValue for var in self.variables},
            'valor_optimo': self.problema.objective.value() if self.problema.status == 1 else None,
            'mensaje': LpStatus[self.problema.status],
            'metodo': 'Simplex'
        }