"""
GeoTherm - Modelo Térmico

Este módulo implementa o modelo térmico para simulação de fluxo de calor em intrusões ígneas.
"""

import numpy as np
from scipy.ndimage import convolve

class ThermalModel:
    """
    Classe principal para modelamento térmico 3D.
    
    Implementa a equação de difusão de calor em 3D usando o método de diferenças finitas.
    Suporta diferentes geometrias de intrusão, condução térmica, convecção hidrotermal
    e calor latente durante cristalização.
    """
    
    def __init__(self, nx=100, ny=100, nz=100, dx=10, dy=10, dz=10, diffusivity=1e-6, background_temperature=20):
        """
        Inicializa o modelo térmico.
        
        Parâmetros:
            nx, ny, nz (int): Dimensões do domínio em células
            dx, dy, dz (float): Tamanho das células em cada direção (m)
            diffusivity (float): Difusividade térmica (m²/s)
            background_temperature (float): Temperatura inicial do encaixante (°C)
        """
        # Dimensões do domínio
        self.nx = nx
        self.ny = ny
        self.nz = nz
        
        # Tamanho das células
        self.dx = dx
        self.dy = dy
        self.dz = dz
        
        # Propriedades térmicas
        self.diffusivity = diffusivity
        self.conductivity = 2.5  # W/(m·K)
        self.specific_heat = 1000  # J/(kg·K)
        self.density = 2700  # kg/m³
        
        # Temperaturas
        self.background_temperature = background_temperature
        self.magma_temperature = 1200  # °C
        
        # Calor latente
        self.use_latent_heat = False
        self.solidus_temperature = 700  # °C
        self.liquidus_temperature = 1200  # °C
        self.latent_heat = 400000  # J/kg
        
        # Convecção
        self.use_convection = False
        self.velocity_field = None
        
        # Inicializar campo de temperatura
        self.temperature = np.ones((nx, ny, nz)) * background_temperature
        
        # Criar grades para geometria
        x = np.arange(0, nx * dx, dx)
        y = np.arange(0, ny * dy, dy)
        z = np.arange(0, nz * dz, dz)
        
        self.x_grid, self.y_grid, self.z_grid = np.meshgrid(x, y, z, indexing='ij')
        
        # Tempo atual da simulação
        self.time = 0.0
        
        # Pontos para histórico de temperatura
        self.history_points = set()
        self.temperature_history = {}
    
    def set_temperature(self, mask, value):
        """
        Define a temperatura em uma região específica.
        
        Parâmetros:
            mask (ndarray): Máscara booleana 3D indicando a região
            value (float): Valor de temperatura a ser definido (°C)
        """
        self.temperature[mask] = value
    
    def add_history_point(self, point):
        """
        Adiciona um ponto para monitoramento de temperatura.
        
        Parâmetros:
            point (tuple): Coordenadas (i, j, k) do ponto
        """
        self.history_points.add(point)
        self.temperature_history[point] = [(self.time, self.temperature[point])]
    
    def simulate_step(self, dt):
        """
        Simula um passo de tempo.
        
        Parâmetros:
            dt (float): Passo de tempo (s)
        """
        # Verificar estabilidade numérica
        max_dt = 0.2 * min(self.dx, self.dy, self.dz)**2 / self.diffusivity
        if dt > max_dt:
            dt = max_dt
            print(f"Aviso: Passo de tempo reduzido para {dt:.2e} s para garantir estabilidade")
        
        # Criar kernel para difusão 3D
        kernel = np.zeros((3, 3, 3))
        kernel[1, 1, 0] = 1
        kernel[1, 0, 1] = 1
        kernel[0, 1, 1] = 1
        kernel[1, 1, 2] = 1
        kernel[1, 2, 1] = 1
        kernel[2, 1, 1] = 1
        kernel[1, 1, 1] = -6
        
        # Calcular laplaciano
        laplacian = convolve(self.temperature, kernel, mode='constant', cval=0)
        
        # Calcular termo de difusão
        diffusion_term = self.diffusivity * laplacian / (self.dx**2)
        
        # Inicializar termo de convecção
        convection_term = np.zeros_like(self.temperature)
        
        # Adicionar convecção se ativada
        if self.use_convection and self.velocity_field is not None:
            vx, vy, vz = self.velocity_field
            
            # Calcular gradientes de temperatura
            grad_x = np.zeros_like(self.temperature)
            grad_y = np.zeros_like(self.temperature)
            grad_z = np.zeros_like(self.temperature)
            
            # Diferenças centrais para gradientes
            grad_x[1:-1, :, :] = (self.temperature[2:, :, :] - self.temperature[:-2, :, :]) / (2 * self.dx)
            grad_y[:, 1:-1, :] = (self.temperature[:, 2:, :] - self.temperature[:, :-2, :]) / (2 * self.dy)
            grad_z[:, :, 1:-1] = (self.temperature[:, :, 2:] - self.temperature[:, :, :-2]) / (2 * self.dz)
            
            # Calcular termo de convecção
            convection_term = -(vx * grad_x + vy * grad_y + vz * grad_z)
        
        # Inicializar termo de calor latente
        latent_heat_term = np.zeros_like(self.temperature)
        
        # Adicionar calor latente se ativado
        if self.use_latent_heat:
            # Temperatura anterior
            temp_old = self.temperature.copy()
            
            # Calcular fração de cristalização
            def crystallization_fraction(temp):
                return np.clip((self.liquidus_temperature - temp) / 
                              (self.liquidus_temperature - self.solidus_temperature), 0, 1)
            
            # Fração de cristalização antes e depois
            frac_old = crystallization_fraction(temp_old)
            frac_new = crystallization_fraction(self.temperature + dt * (diffusion_term + convection_term))
            
            # Variação na fração de cristalização
            dfrac = frac_new - frac_old
            
            # Termo de calor latente
            latent_heat_term = self.latent_heat * self.density * dfrac / (self.specific_heat * self.density * dt)
        
        # Atualizar temperatura
        self.temperature += dt * (diffusion_term + convection_term + latent_heat_term)
        
        # Atualizar tempo
        self.time += dt
        
        # Atualizar histórico de temperatura
        for point in self.history_points:
            self.temperature_history[point].append((self.time, self.temperature[point]))
    
    def simulate_to(self, target_time):
        """
        Simula até um tempo específico.
        
        Parâmetros:
            target_time (float): Tempo alvo (s)
        """
        if target_time <= self.time:
            return
        
        # Calcular passo de tempo adaptativo
        dt = 0.1 * min(self.dx, self.dy, self.dz)**2 / self.diffusivity
        
        # Número de passos
        n_steps = int((target_time - self.time) / dt) + 1
        dt = (target_time - self.time) / n_steps
        
        # Simular passos
        for _ in range(n_steps):
            self.simulate_step(dt)
    
    def get_slice(self, axis, position):
        """
        Obtém uma fatia 2D do campo térmico.
        
        Parâmetros:
            axis (str): Eixo perpendicular à fatia ('x', 'y' ou 'z')
            position (int): Posição da fatia ao longo do eixo
        
        Retorna:
            ndarray: Fatia 2D do campo térmico
        """
        if axis == 'x':
            return self.temperature[position, :, :]
        elif axis == 'y':
            return self.temperature[:, position, :]
        elif axis == 'z':
            return self.temperature[:, :, position]
        else:
            raise ValueError("Eixo inválido. Use 'x', 'y' ou 'z'.")
    
    def set_convection_cell(self, max_velocity):
        """
        Define um campo de velocidade para célula de convecção.
        
        Parâmetros:
            max_velocity (float): Velocidade máxima (m/s)
        """
        # Criar campo de velocidade para célula de convecção
        vx = np.zeros((self.nx, self.ny, self.nz))
        vy = np.zeros((self.nx, self.ny, self.nz))
        vz = np.zeros((self.nx, self.ny, self.nz))
        
        # Centro do domínio
        cx = self.nx // 2
        cy = self.ny // 2
        cz = self.nz // 2
        
        # Raio da célula de convecção
        radius = min(self.nx, self.ny, self.nz) // 4
        
        # Criar célula de convecção
        for i in range(self.nx):
            for j in range(self.ny):
                for k in range(self.nz):
                    # Distância ao centro
                    dx = (i - cx) * self.dx
                    dy = (j - cy) * self.dy
                    dz = (k - cz) * self.dz
                    
                    # Distância radial
                    r = np.sqrt(dx**2 + dy**2)
                    
                    # Dentro da célula de convecção
                    if r < radius * self.dx and abs(dz) < radius * self.dz:
                        # Componente vertical
                        if dz < 0:
                            vz[i, j, k] = max_velocity * np.exp(-(r / (radius * self.dx))**2)
                        else:
                            vz[i, j, k] = -max_velocity * np.exp(-(r / (radius * self.dx))**2)
                        
                        # Componentes horizontais
                        if r > 0:
                            vx[i, j, k] = -max_velocity * dx / r * np.exp(-(r / (radius * self.dx))**2)
                            vy[i, j, k] = -max_velocity * dy / r * np.exp(-(r / (radius * self.dx))**2)
        
        # Definir campo de velocidade
        self.velocity_field = (vx, vy, vz)
        self.use_convection = True
    
    def set_upward_flow(self, max_velocity):
        """
        Define um campo de velocidade para fluxo ascendente.
        
        Parâmetros:
            max_velocity (float): Velocidade máxima (m/s)
        """
        # Criar campo de velocidade para fluxo ascendente
        vx = np.zeros((self.nx, self.ny, self.nz))
        vy = np.zeros((self.nx, self.ny, self.nz))
        vz = np.ones((self.nx, self.ny, self.nz)) * max_velocity
        
        # Definir campo de velocidade
        self.velocity_field = (vx, vy, vz)
        self.use_convection = True
    
    def set_lateral_flow(self, max_velocity):
        """
        Define um campo de velocidade para fluxo lateral.
        
        Parâmetros:
            max_velocity (float): Velocidade máxima (m/s)
        """
        # Criar campo de velocidade para fluxo lateral
        vx = np.ones((self.nx, self.ny, self.nz)) * max_velocity
        vy = np.zeros((self.nx, self.ny, self.nz))
        vz = np.zeros((self.nx, self.ny, self.nz))
        
        # Definir campo de velocidade
        self.velocity_field = (vx, vy, vz)
        self.use_convection = True
