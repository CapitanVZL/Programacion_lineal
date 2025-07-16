import numpy as np


class MetodoSimplexManual:
    def __init__(self):
        self.tableau = None
        self.c = None

    def resolver(self, datos_problema):
        # 1. Extraer y preparar los datos del problema
        if datos_problema['tipo_optimizacion'] != 'Maximizar' or any(
                r['signo'] != '<=' for r in datos_problema['restricciones']):
            return {
                'solucion_optima': False,
                'mensaje': "La implementación manual actual solo soporta problemas de Maximización con restricciones '<='.",
                'historial_iteraciones': []
            }

        self.c = np.array(datos_problema['funcion_objetivo'])
        A = np.array([r['coeficientes'] for r in datos_problema['restricciones']])
        b = np.array([r['rhs'] for r in datos_problema['restricciones']])

        historial = []

        # 2. Construir el Tableau Inicial
        self._crear_tableau_inicial(A, b)
        historial.append({
            "descripcion": "Paso 1: Se construye el Tableau Inicial. Las variables de holgura (S) se añaden para convertir las desigualdades en igualdades.",
            "tableau": self.tableau.copy()
        })

        # 3. Bucle de Iteraciones Simplex
        iteracion = 1
        while not self._condicion_de_parada():
            descripcion_paso = f"\n--- ITERACIÓN {iteracion} ---\n"

            col_pivote = self._encontrar_columna_pivote()
            descripcion_paso += f"1. Variable que entra: Se elige la columna con el valor más negativo en la fila Z (Fila 0).\n   -> Columna pivote: X{col_pivote}. (Valor: {self.tableau[0, col_pivote]:.2f})\n"

            fila_pivote = self._encontrar_fila_pivote(col_pivote)
            if fila_pivote == -1:
                descripcion_paso += "Error: Solución no acotada. No se puede encontrar una fila pivote válida."
                historial.append({"descripcion": descripcion_paso, "tableau": self.tableau.copy()})
                return self._interpretar_resultado_final(historial, no_acotado=True)

            descripcion_paso += f"2. Variable que sale: Se elige la fila con el cociente mínimo positivo (RHS / Columna Pivote).\n   -> Fila pivote: {fila_pivote}.\n"

            elemento_pivote = self.tableau[fila_pivote, col_pivote]
            descripcion_paso += f"3. El elemento pivote es {elemento_pivote:.2f}.\n"

            self._realizar_pivote(fila_pivote, col_pivote)
            descripcion_paso += "4. Se realizan operaciones de fila para generar el nuevo tableau."

            historial.append({"descripcion": descripcion_paso, "tableau": self.tableau.copy()})
            iteracion += 1
            if iteracion > 20:  # Salvavidas para ciclos
                historial.append({"descripcion": "Se detuvo por superar el límite de 20 iteraciones.",
                                  "tableau": self.tableau.copy()})
                break

        return self._interpretar_resultado_final(historial)

    def _crear_tableau_inicial(self, A, b):
        num_restricciones, num_variables = A.shape
        self.tableau = np.zeros((num_restricciones + 1, 1 + num_variables + num_restricciones + 1))

        self.tableau[0, 0] = 1
        self.tableau[0, 1:1 + num_variables] = -self.c
        self.tableau[1:, 1:1 + num_variables] = A
        self.tableau[1:, 1 + num_variables:-1] = np.eye(num_restricciones)
        self.tableau[1:, -1] = b

    def _condicion_de_parada(self):
        return np.all(self.tableau[0, 1:-1] >= 0)

    def _encontrar_columna_pivote(self):
        return np.argmin(self.tableau[0, 1:-1]) + 1

    def _encontrar_fila_pivote(self, col_pivote):
        columna = self.tableau[1:, col_pivote]
        rhs = self.tableau[1:, -1]
        ratios = np.full_like(rhs, np.inf)
        np.divide(rhs, columna, out=ratios, where=columna > 1e-6)  # Evitar división por cero/negativos

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

    def _interpretar_resultado_final(self, historial, no_acotado=False):
        if no_acotado:
            return {'solucion_optima': False, 'mensaje': 'Solución No Acotada.', 'historial_iteraciones': historial,
                    'metodo': 'Simplex'}

        num_variables_decision = len(self.c)
        solucion = {}
        for i in range(num_variables_decision):
            col_idx = i + 1
            columna = self.tableau[:, col_idx]
            if np.sum(columna) == 1 and np.count_nonzero(columna) == 1:
                fila_solucion = np.where(columna == 1)[0][0]
                solucion[f"X{i + 1}"] = self.tableau[fila_solucion, -1]
            else:
                solucion[f"X{i + 1}"] = 0

        historial.append({
            "descripcion": "\n--- RESULTADO FINAL ---\nEl algoritmo ha terminado porque no hay valores negativos en la fila Z.",
            "tableau": None
        })

        return {
            'solucion_optima': True,
            'valor_optimo': self.tableau[0, -1],
            'variables': solucion,
            'mensaje': 'Solución óptima encontrada.',
            'historial_iteraciones': historial,
            'metodo': 'Simplex'
        }