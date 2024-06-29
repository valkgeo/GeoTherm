import numpy as np
import matplotlib.pyplot as plt
from math import erf, sqrt, pi, exp

class ThermalModel:
    def run(self, data, geometry, T0, K1, k, K, k1, g, l, d=None, time=None):
        if geometry == "Tabular-like body":
            return self.run_tabular(data, T0, K1, k, K, k1, g, l)
        elif geometry == "Spheric-like body":
            return self.run_spheric(data, T0, K1, k, K, k1, g, l, d, time)
        elif geometry == "Plug-like body":
            return self.run_plug(data, T0, K1, k, K, k1, g, l)

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
            x = [n for n in range(-199, 200, 1) if n != 0]
            
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
