import numpy as np
import matplotlib.pyplot as plt
from math import erf, sqrt, pi, exp

class ThermalModel:
    def run(self, data, geometry, T0, K1, k, K, k1, g, l, d=None, time=None):
        method = data.get("method", "analytical")  # Default to analytical
        if method == "numerical":
            return self.run_numerical(data, T0, K1, k, K, k1, g, l)
        elif geometry == "Tabular-like body":
            return self.run_tabular(data, T0, K1, k, K, k1, g, l)
        elif geometry == "Spheric-like body":
            return self.run_spheric(data, T0, K1, k, K, k1, g, l, d, time)
        elif geometry == "Plug-like body":
            return self.run_plug(data, T0, K1, k, K, k1, g, l)

    # ========================
    # SOLUÇÃO ANALÍTICA
    # ========================
    def run_tabular(self, data, T0, K1, k, K, k1, g, l):
        # Implementação futura para corpos tabulares
        pass

    def run_spheric(self, data, T0, K1, k, K, k1, g, l, d, time):
        # Equation (27) of Jaeger (1964)
        alpha = ((2.2) * (0.43**0.5)) / ((2.59) * (0.34**0.5))

        # Equation (28) of Jaeger (1964)
        Tc = alpha * T0 / (1 + alpha) + g * l

        results = {}

        for t in time:
            x = [n for n in range(-2*int(d), 2*int(d), 1) if n != 0]
            
            # Dimensionless parameters
            epsilon = [xi / d for xi in x]
            tau = (k * t) / d**2  # dimensionless parameter tau

            # Psi calculation
            Psi = [
                1/2 * (erf((epsilon_i + 1) / (2 * sqrt(tau))) -
                       erf((epsilon_i - 1) / (2 * sqrt(tau))) -
                       (2 * sqrt(tau) / (epsilon_i * sqrt(pi))) *
                       (exp(-((epsilon_i - 1)**2) / (4 * tau)) -
                        exp(-((epsilon_i + 1)**2) / (4 * tau))))
                for epsilon_i in epsilon
            ]

            # Temperature calculation
            T = [psi * T0 for psi in Psi]

            # Store results
            results[t] = (x, T)

        return results

    def run_plug(self, data, T0, K1, k, K, k1, g, l):
        # Implementação futura para corpos cilíndricos
        pass

    # ========================
    # SOLUÇÃO NUMÉRICA (FEM)
    # ========================
    def run_numerical(self, data, T0, K1, k, K, k1, g, l):
        grid = data.get("grid", None)
        if grid is None:
            grid = self.generate_default_grid()
        
        parameters = data.get("parameters", {})
        matrix, rhs = self.assemble_fem_system(grid, parameters, T0, K1, k, K, k1, g, l)
        solution = self.solve_system(matrix, rhs)
        
        return solution

    def generate_default_grid(self, nx=50, ny=50):
        """Gera um grid padrão 2D para modelagem numérica."""
        x = np.linspace(0, 1, nx)
        y = np.linspace(0, 1, ny)
        xv, yv = np.meshgrid(x, y)
        return {"x": xv, "y": yv}

    def assemble_fem_system(self, grid, parameters, T0, K1, k, K, k1, g, l):
        """Monta a matriz de rigidez e o vetor de carga para o FEM."""
        nx, ny = grid["x"].shape
        matrix = np.zeros((nx * ny, nx * ny))  # Matriz de rigidez
        rhs = np.zeros(nx * ny)  # Vetor de carga

        # Exemplo simples de preenchimento (implementação real seria mais complexa)
        for i in range(nx * ny):
            matrix[i, i] = 1  # Elemento diagonal
            rhs[i] = T0  # Fonte de calor

        return matrix, rhs

    def solve_system(self, matrix, rhs):
        """Resolve o sistema linear Ax = b."""
        from scipy.sparse.linalg import spsolve
        solution = np.linalg.solve(matrix, rhs)  # Use solução densa para simplificar
        return solution.reshape((int(sqrt(len(rhs))), int(sqrt(len(rhs)))))