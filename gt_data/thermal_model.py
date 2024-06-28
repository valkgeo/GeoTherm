import numpy as np

class ThermalModel:
    def run(self, data):
        geometry = data['geometry']
        k = data['k']
        L = data['L']
        A = data['A']
        T0 = data['T0']
        T1 = data['T1']
        
        if geometry == "Tabular-like body":
            return self.tabular_model(k, L, A, T0, T1)
        elif geometry == "Plug-like body":
            return self.plug_model(k, L, A, T0, T1)
        elif geometry == "Spheric-like body":
            return self.spheric_model(k, L, A, T0, T1)
    
    def tabular_model(self, k, L, A, T0, T1):
        n = 10
        dx = L / (n - 1)
        x = np.linspace(0, L, n)
        
        A_matrix = np.zeros((n, n))
        b = np.zeros(n)
        
        for i in range(1, n-1):
            A_matrix[i, i-1] = k / dx**2
            A_matrix[i, i] = -2 * k / dx**2
            A_matrix[i, i+1] = k / dx**2
        
        A_matrix[0, 0] = 1
        A_matrix[-1, -1] = 1
        b[0] = T0
        b[-1] = T1
        
        T = np.linalg.solve(A_matrix, b)
        
        return x, T
    
    def plug_model(self, k, L, A, T0, T1):
        # Implementação do modelo plug
        pass
    
    def spheric_model(self, k, L, A, T0, T1):
        # Implementação do modelo esférico
        pass
