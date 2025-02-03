import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, pi, exp
from scipy.special import jn_zeros, j0, j1, erf  # Use vectorized erf from scipy.special

class ThermalModel:
    def run(self, data, geometry, T0, K1, k, K, k1, g, l, d=None, time=None):
        """
        Main entry point for running the thermal model.
        
        Parameters:
            data    : dictionary containing additional data (e.g., 'method', 'time', 'd')
            geometry: string indicating the geometry ("Tabular-like body", 
                      "Spheric-like body", "Plug-like body", or "Cylindrical-like body")
            T0      : initial temperature of the intrusion
            K1      : thermal conductivity of magma
            k       : thermal diffusivity of country rock (κ)
            K       : thermal conductivity of country rock
            k1      : thermal diffusivity of magma
            g       : geothermal gradient (if used)
            l       : depth (or a parameter related to cover)
            d       : characteristic dimension (e.g., half-thickness, radius)
            time    : list or array of times at which to evaluate the solution
        """
        method = data.get("method", "analytical")  # Default to analytical
        if method == "numerical":
            return self.run_numerical(data, T0, K1, k, K, k1, g, l)
        elif geometry == "Tabular-like body":
            return self.run_tabular(data, T0, K1, k, K, k1, g, l)
        elif geometry == "Spheric-like body":
            return self.run_spheric(data, T0, K1, k, K, k1, g, l, d, time)
        elif geometry == "Cylindrical-like body" or geometry == "Plug-like body":
            # Here, 'Plug-like body' is interpreted as a cylindrical intrusion.
            return self.run_plug(data, T0, K1, k, K, k1, g, l, d, time)
        else:
            raise ValueError("Unknown geometry specified.")

    # ========================
    # ANALYTICAL SOLUTION
    # ========================
    def run_tabular(self, data, T0, K1, k, K, k1, g, l):
        """
        Analytical solution for an infinite sheet (tabular body):
        
        T(x,t) = (T0/2) * { erf((x+d)/(2*sqrt(k*t))) - erf((x-d)/(2*sqrt(k*t))) }
        
        where:
          - T0 is the initial temperature for -d < x < d,
          - d is half the width of the initially heated sheet,
          - k is the thermal diffusivity (κ),
          - t is time, and
          - x is the spatial coordinate.
        """
        # Retrieve 'd' and 'time' from the data dictionary
        d_value = data.get("d", None)
        if d_value is None:
            raise ValueError("Parameter 'd' is required for Tabular-like body.")
        time = data.get("time", None)
        if time is None:
            raise ValueError("Parameter 'time' (list of times) is required for Tabular-like body.")
        
        # Calculate the horst rock temperature
        Tecx = g * l

        results = {}
        # Define a spatial grid for x, e.g., from -3*d to 3*d with 100 points.
        x_values = np.linspace(-3 * d_value, 3 * d_value, 100)
        
        for t in time:
            # Calculate the temperature T(x,t) using the vectorized erf from scipy.special
            factor = 2.0 * sqrt(k * t)
            T_profile = ((T0 - Tecx) / 2.0) * (
                erf((x_values + d_value) / factor) - erf((x_values - d_value) / factor)
            ) + Tecx
            results[t] = (x_values, T_profile)
        
        return results

    def run_spheric(self, data, T0, K1, k, K, k1, g, l, d, time):
        """
        Analytical solution for a spherical-like body, following Jaeger (1964).

        Calculates the parameter sigma from the thermal conductivities and diffusivities:
            sigma = (K1 * sqrt(k)) / (K * sqrt(k1))    # Equation (27) of Jaeger (1964)
            
        And the initial contact temperature:
            Tc = sigma * T0 / (1 + sigma) + g * l      # Equation (28) of Jaeger (1964)
            
        For each time instant t, calculates the dimensionless solution ψ(ξ,τ) and
        the temperature T = ψ * T0.
        
        Parameters:
            - d: characteristic dimension (e.g., radius or diameter)
            - time: list of times at which the solution is computed
        """
        # Calculate the parameter sigma as per Equation (27) of Jaeger (1964)
        sigma = (K1 * sqrt(k)) / (K * sqrt(k1))
        # Calculate the initial contact temperature (including a geothermal term)
        Tc = sigma * T0 / (1 + sigma) + g * l
        # Calculate the horst rock temperature
        Tecx = g * l

        results = {}
        for t in time:
            # Create a spatial grid for x; using integer steps (you might use np.linspace for higher resolution)
            x = [n for n in range(-2 * int(d), 2 * int(d), 1) if n != 0]
            
            # Compute dimensionless spatial coordinate ε = x/d
            epsilon = [xi / d for xi in x]
            # Compute dimensionless time τ = (κ * t) / d²
            tau = (k * t) / (d ** 2)
            
            # Calculate ψ(ξ,τ) using the expression from Jaeger (1964)
            # (See Equation (16) of Jaeger (1964), using standard error functions and exponentials)
            Psi = [
                0.5 * (
                    erf((epsilon_i + 1) / (2 * sqrt(tau))) -
                    erf((epsilon_i - 1) / (2 * sqrt(tau))) -
                    (2 * sqrt(tau) / (epsilon_i * sqrt(pi))) *
                    (
                        exp(-((epsilon_i - 1) ** 2) / (4 * tau)) -
                        exp(-((epsilon_i + 1) ** 2) / (4 * tau))
                    )
                )
                for epsilon_i in epsilon
            ]
            
            # Compute the temperature profile T(x,t)
            T_profile = [(T0 - Tecx) * psi + Tecx  for psi in Psi]
            
            results[t] = (x, T_profile)
        
        return results

    def run_plug(self, data, T0, K1, k, K, k1, g, l, d, time):
        """
        Analytical solution for a plug-like (pipe-like) body with a rectangular cross section.
        
        This solution corresponds to an infinite cylinder (pipe-like intrusion) with a rectangular
        cross section defined by -d1 < x < d1 and -d2 < y < d2. The initial temperature is T0
        inside and zero outside. The temperature distribution is given by Carslaw & Jaeger (1959, §2.2 (9)):
        
            T = T0 * φ(ξ₁, τ₁) * φ(ξ₂, τ₂)
        
        where:
            φ(ξ, τ) = 1/2 [erf((ξ+1)/(2√τ)) - erf((ξ-1)/(2√τ))]
            ξ₁ = x / d₁,   τ₁ = κ t / d₁²,
            ξ₂ = y / d₂,   τ₂ = κ t / d₂²,
            with κ given by parameter k.
        
        Parameters:
            T0   : Initial temperature inside the intrusion.
            k    : Thermal diffusivity (κ).
            d    : Either a single value (then d1 = d2 = d) or a tuple/list (d1, d2).
            time : List or array of times at which to compute the solution.
            
        Returns:
            results : A dictionary where each key is a time t and the corresponding value is
                    a tuple (X, Y, T) with the spatial grid (X, Y) and the temperature distribution T.
        """
        # Check for the time parameter (if not provided via data)
        if time is None:
            time = data.get("time", None)
            if time is None:
                raise ValueError("Parameter 'time' (list of times) is required for Plug-like body.")
        
        # Determine d1 and d2
        if isinstance(d, (list, tuple)):
            if len(d) < 2:
                raise ValueError("For a plug-like body, d should be provided as a tuple/list with two elements (d1, d2).")
            d1, d2 = d[0], d[1]
        else:
            d1 = d2 = d
        
        # Calculate the horst rock temperature
        Tecx = g * l

        results = {}
        # Define a spatial grid for x and y: for example, from -3*d1 to 3*d1 for x and -3*d2 to 3*d2 for y.
        x_values = np.linspace(-3*d1, 3*d1, 100)
        y_values = np.linspace(-3*d2, 3*d2, 100)
        X, Y = np.meshgrid(x_values, y_values)
        
        for t in time:
            # Compute dimensionless times
            tau1 = k * t / (d1**2)
            tau2 = k * t / (d2**2)
            # Compute dimensionless spatial coordinates
            xi1 = X / d1
            xi2 = Y / d2

            # Compute φ for each coordinate direction:
            phi1 = 0.5 * (erf((xi1 + 1) / (2 * np.sqrt(tau1))) - erf((xi1 - 1) / (2 * np.sqrt(tau1))))
            phi2 = 0.5 * (erf((xi2 + 1) / (2 * np.sqrt(tau2))) - erf((xi2 - 1) / (2 * np.sqrt(tau2))))
            
            # The temperature distribution is the product multiplied by T0
            T_profile = (T0 - Tecx) * phi1 * phi2 + Tecx
            
            results[t] = (X, Y, T_profile)
        
        return results

    # ========================
    # NUMERICAL SOLUTION (FEM)
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
        """Generates a default 2D grid for numerical modeling."""
        x = np.linspace(0, 1, nx)
        y = np.linspace(0, 1, ny)
        xv, yv = np.meshgrid(x, y)
        return {"x": xv, "y": yv}

    def assemble_fem_system(self, grid, parameters, T0, K1, k, K, k1, g, l):
        """Assembles the stiffness matrix and load vector for the FEM."""
        nx, ny = grid["x"].shape
        matrix = np.zeros((nx * ny, nx * ny))  # Stiffness matrix
        rhs = np.zeros(nx * ny)  # Load vector

        # Simple example: fill the diagonal and set a constant heat source T0
        for i in range(nx * ny):
            matrix[i, i] = 1
            rhs[i] = T0

        return matrix, rhs

    def solve_system(self, matrix, rhs):
        """Solves the linear system Ax = b."""
        from scipy.sparse.linalg import spsolve
        solution = np.linalg.solve(matrix, rhs)  # Using dense solver for simplicity
        size = int(sqrt(len(rhs)))
        return solution.reshape((size, size))
