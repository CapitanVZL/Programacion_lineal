from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, LpStatus, LpConstraint
import numpy as np

class MetodoGrafico:
    def __init__(self):
        self.problema = None
        self.x1 = None
        self.x2 = None
        
    def resolver(self, datos_problema):
        # Crear el problema de optimización
        self.crear_problema(datos_problema)
        
        # Agregar restricciones
        self.agregar_restricciones(datos_problema['restricciones'])
        
        # Resolver el problema
        self.problema.solve()
        
        # Obtener resultados
        resultados = self.obtener_resultados()
        
        # Calcular información para el gráfico
        resultados.update(self.calcular_info_grafico(datos_problema['restricciones']))
        
        return resultados
    
    def crear_problema(self, datos_problema):
        # Determinar si es maximización o minimización
        if datos_problema['tipo_optimizacion'] == "Maximizar":
            sentido = LpMaximize
        else:
            sentido = LpMinimize
            
        # Crear problema
        self.problema = LpProblem("Problema_Grafico", sentido)
        
        # Crear variables (siempre X1 y X2 para método gráfico)
        self.x1 = LpVariable("X1", lowBound=0)  # X1 >= 0
        self.x2 = LpVariable("X2", lowBound=0)  # X2 >= 0
        
        # Crear función objetivo
        objetivo = datos_problema['funcion_objetivo'][0] * self.x1 + datos_problema['funcion_objetivo'][1] * self.x2
        self.problema += objetivo, "Z"
    
    def agregar_restricciones(self, restricciones):
        for i, r in enumerate(restricciones, 1):
            expr = r['coeficientes'][0] * self.x1 + r['coeficientes'][1] * self.x2
            
            if r['signo'] == "<=":
                self.problema += expr <= r['rhs'], f"R{i}"
            elif r['signo'] == ">=":
                self.problema += expr >= r['rhs'], f"R{i}"
            else:  # "="
                self.problema += expr == r['rhs'], f"R{i}"
    
    def obtener_resultados(self):
        resultados = {
            'status': LpStatus[self.problema.status],
            'solucion_optima': None,
            'vertices': [],
            'mensaje': ""
        }
        
        if self.problema.status == 1:  # Óptimo encontrado
            x1_val = self.x1.varValue
            x2_val = self.x2.varValue
            z_val = self.problema.objective.value()
            
            resultados['solucion_optima'] = {
                'punto': (x1_val, x2_val),
                'valor_optimo': z_val
            }
            resultados['mensaje'] = "Solución óptima encontrada."
        else:
            resultados['mensaje'] = f"El problema no tiene solución óptima. Estado: {resultados['status']}"
            
        return resultados
    
    def calcular_info_grafico(self, restricciones):
        # Calcular los vértices de la región factible
        vertices = self.calcular_vertices(restricciones)
        
        # Calcular los límites del gráfico
        limites = self.calcular_limites_grafico(restricciones, vertices)
        
        # Preparar datos para graficar las restricciones
        restricciones_grafico = []
        for i, r in enumerate(restricciones, 1):
            a, b = r['coeficientes']
            rhs = r['rhs']
            signo = r['signo']
            
            # Calcular puntos para graficar la restricción
            x_points, y_points = self.calcular_puntos_restriccion(a, b, rhs, limites)
            
            restricciones_grafico.append({
                'x_points': x_points,
                'y_points': y_points,
                'label': f'R{i}: {a}X1 + {b}X2 {signo} {rhs}'
            })
        
        return {
            'restricciones_grafico': restricciones_grafico,
            'vertices': vertices,
            'limites': limites
        }
    
    def calcular_vertices(self, restricciones):
        # Convertir restricciones a formato para cálculos
        ecuaciones = []
        for r in restricciones:
            a, b = r['coeficientes']
            rhs = r['rhs']
            ecuaciones.append({'a': a, 'b': b, 'rhs': rhs, 'signo': r['signo']})
        
        # Agregar restricciones de no negatividad
        ecuaciones.append({'a': 1, 'b': 0, 'rhs': 0, 'signo': '>='})  # X1 >= 0
        ecuaciones.append({'a': 0, 'b': 1, 'rhs': 0, 'signo': '>='})  # X2 >= 0
        
        # Encontrar todas las intersecciones posibles
        vertices = []
        n = len(ecuaciones)
        
        for i in range(n):
            for j in range(i+1, n):
                # Resolver sistema de 2 ecuaciones
                a1, b1 = ecuaciones[i]['a'], ecuaciones[i]['b']
                rhs1 = ecuaciones[i]['rhs']
                
                a2, b2 = ecuaciones[j]['a'], ecuaciones[j]['b']
                rhs2 = ecuaciones[j]['rhs']
                
                # Matriz de coeficientes
                A = np.array([[a1, b1], [a2, b2]])
                B = np.array([rhs1, rhs2])
                
                try:
                    # Resolver el sistema
                    punto = np.linalg.solve(A, B)
                    x, y = punto[0], punto[1]
                    
                    # Verificar si el punto satisface todas las restricciones
                    if self.es_factible(x, y, ecuaciones):
                        vertices.append((x, y))
                except np.linalg.LinAlgError:
                    # Las rectas son paralelas, no hay intersección
                    continue
        
        return vertices
    
    def es_factible(self, x, y, ecuaciones):
        for eq in ecuaciones:
            valor = eq['a'] * x + eq['b'] * y
            rhs = eq['rhs']
            
            if eq['signo'] == "<=" and valor > rhs + 1e-6:  # Pequeña tolerancia
                return False
            elif eq['signo'] == ">=" and valor < rhs - 1e-6:
                return False
            elif eq['signo'] == "=" and abs(valor - rhs) > 1e-6:
                return False
                
        return True
    
    def calcular_limites_grafico(self, restricciones, vertices):
        # Inicializar con valores pequeños
        x_max, y_max = 10.0, 10.0
        
        # Calcular intersecciones con ejes para cada restricción
        for r in restricciones:
            a, b = r['coeficientes']
            rhs = r['rhs']
            
            if a != 0:
                x_int = rhs / a
                if x_int > 0:
                    x_max = max(x_max, x_int * 1.2)
            
            if b != 0:
                y_int = rhs / b
                if y_int > 0:
                    y_max = max(y_max, y_int * 1.2)
        
        # Considerar los vértices
        if vertices:
            x_vals = [v[0] for v in vertices]
            y_vals = [v[1] for v in vertices]
            
            x_max = max(x_max, max(x_vals) * 1.2)
            y_max = max(y_max, max(y_vals) * 1.2)
        
        return {'x_max': x_max, 'y_max': y_max}
    
    def calcular_puntos_restriccion(self, a, b, rhs, limites):
        x_max = limites['x_max']
        y_max = limites['y_max']
        
        if a == 0:  # Restricción horizontal: b*X2 = rhs
            y = rhs / b
            return [0, x_max], [y, y]
        elif b == 0:  # Restricción vertical: a*X1 = rhs
            x = rhs / a
            return [x, x], [0, y_max]
        else:  # Restricción general
            # Puntos de intersección con los ejes
            x_intercept = rhs / a if a != 0 else None
            y_intercept = rhs / b if b != 0 else None
            
            points = []
            
            # Intersección con eje X (y=0)
            if x_intercept is not None and 0 <= x_intercept <= x_max:
                points.append((x_intercept, 0))
            
            # Intersección con eje Y (x=0)
            if y_intercept is not None and 0 <= y_intercept <= y_max:
                points.append((0, y_intercept))
            
            # Intersección con x_max
            y_at_xmax = (rhs - a * x_max) / b
            if 0 <= y_at_xmax <= y_max:
                points.append((x_max, y_at_xmax))
            
            # Intersección con y_max
            x_at_ymax = (rhs - b * y_max) / a
            if 0 <= x_at_ymax <= x_max:
                points.append((x_at_ymax, y_max))
            
            # Ordenar puntos por coordenada x
            points.sort()
            
            # Si no hay suficientes puntos, usar origen
            if len(points) < 2:
                points = [(0, 0), (x_max, y_max)]
            
            # Separar coordenadas x e y
            x_points = [p[0] for p in points]
            y_points = [p[1] for p in points]
            
            return x_points, y_points