"""
GeoTherm - Módulo Integrador

Este módulo integra o modelo térmico com a interface gráfica.
"""

import numpy as np
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from src.thermal_model.thermal_model import ThermalModel
import src.thermal_model.geometry as geometry
import src.thermal_model.visualization as visualization

class ModelIntegrator(QObject):
    """
    Integrador entre o modelo térmico e a interface gráfica.
    
    Gerencia a comunicação entre os componentes do programa.
    """
    
    # Sinais para comunicação com a interface
    simulation_progress = pyqtSignal(int)
    simulation_completed = pyqtSignal(list)
    temperature_updated = pyqtSignal(float)
    
    def __init__(self, main_window):
        """
        Inicializa o integrador.
        
        Parâmetros:
            main_window: Janela principal do programa
        """
        super().__init__()
        
        # Referência à janela principal
        self.main_window = main_window
        
        # Modelo térmico
        self.model = None
        
        # Dados da simulação
        self.temperature_data = []
        self.time_points = []
        
        # Estado da simulação
        self.is_running = False
        self.is_paused = False
        self.start_time = 0
        
        # Conectar sinais
        self.connect_signals()
    
    def connect_signals(self):
        """Conecta os sinais entre os componentes."""
        # Conectar painel de parâmetros
        self.main_window.parameter_panel.parameters_changed.connect(self.on_parameters_changed)
        
        # Conectar controle de simulação
        self.main_window.simulation_control.time_changed.connect(self.on_time_changed)
        
        # Conectar sinais do integrador
        self.simulation_progress.connect(self.main_window.simulation_control.set_progress)
        self.simulation_completed.connect(self.main_window.simulation_control.simulation_completed)
        self.temperature_updated.connect(self.main_window.simulation_control.set_temperature)
    
    def on_parameters_changed(self, params):
        """
        Manipula a alteração de parâmetros.
        
        Parâmetros:
            params (dict): Dicionário com os parâmetros
        """
        # Criar novo modelo térmico
        self.create_model(params)
        
        # Atualizar status
        self.main_window.statusBar().showMessage("Parâmetros aplicados", 3000)
    
    def create_model(self, params):
        """
        Cria um novo modelo térmico com os parâmetros especificados.
        
        Parâmetros:
            params (dict): Dicionário com os parâmetros
        """
        # Extrair parâmetros
        geometry_params = params.get('geometry', {})
        thermal_params = params.get('thermal', {})
        
        # Dimensões do domínio
        domain = geometry_params.get('domain', {})
        nx = domain.get('nx', 100)
        ny = domain.get('ny', 100)
        nz = domain.get('nz', 100)
        dx = domain.get('cell_size', 10)
        dy = domain.get('cell_size', 10)
        dz = domain.get('cell_size', 10)
        
        # Propriedades térmicas
        properties = thermal_params.get('properties', {})
        diffusivity = properties.get('diffusivity', 1e-6)
        
        temperatures = thermal_params.get('temperatures', {})
        background_temperature = temperatures.get('background', 20)
        
        # Criar modelo
        self.model = ThermalModel(nx, ny, nz, dx, dy, dz, diffusivity, background_temperature)
        
        # Configurar propriedades térmicas
        self.model.conductivity = properties.get('conductivity', 2.5)
        self.model.specific_heat = properties.get('specific_heat', 1000)
        self.model.density = properties.get('density', 2700)
        
        # Configurar temperaturas
        self.model.magma_temperature = temperatures.get('magma', 1200)
        
        # Configurar calor latente
        latent_heat = thermal_params.get('latent_heat', {})
        self.model.use_latent_heat = latent_heat.get('use_latent_heat', False)
        self.model.solidus_temperature = latent_heat.get('solidus', 700)
        self.model.liquidus_temperature = latent_heat.get('liquidus', 1200)
        self.model.latent_heat = latent_heat.get('latent_heat', 400000)
        
        # Adicionar intrusão
        self.add_intrusion(geometry_params)
        
        # Configurar convecção
        simulation_params = params.get('simulation', {})
        modules = simulation_params.get('modules', {})
        
        if modules.get('convection', False):
            convection = simulation_params.get('convection', {})
            flow_type = convection.get('flow_type', 'Célula de Convecção')
            max_velocity = convection.get('max_velocity', 1e-6)
            
            if flow_type == 'Célula de Convecção':
                self.model.set_convection_cell(max_velocity)
            elif flow_type == 'Fluxo Ascendente':
                self.model.set_upward_flow(max_velocity)
            elif flow_type == 'Fluxo Lateral':
                self.model.set_lateral_flow(max_velocity)
            
            self.model.use_convection = True
        else:
            self.model.use_convection = False
        
        # Adicionar pontos para histórico de temperatura
        self.add_history_points()
        
        # Limpar dados anteriores
        self.temperature_data = []
        self.time_points = []
        
        # Atualizar visualizações
        self.update_visualizations()
    
    def add_intrusion(self, geometry_params):
        """
        Adiciona uma intrusão ao modelo.
        
        Parâmetros:
            geometry_params (dict): Parâmetros de geometria
        """
        if not self.model:
            return
        
        # Extrair parâmetros
        geometry_type = geometry_params.get('geometry_type', 'Planar (Sill)')
        intrusion = geometry_params.get('intrusion', {})
        
        # Criar máscara para intrusão
        mask = None
        
        # Centro do domínio
        cx = self.model.nx // 2
        cy = self.model.ny // 2
        cz = self.model.nz // 2
        
        if geometry_type == 'Planar (Sill)':
            # Intrusão planar (sill)
            thickness = intrusion.get('thickness', 50)
            width = intrusion.get('width', 500)
            height = intrusion.get('height', 500)
            
            # Converter para células
            thickness_cells = int(thickness / self.model.dz)
            width_cells = int(width / self.model.dx)
            height_cells = int(height / self.model.dy)
            
            # Posição da intrusão
            x0 = cx - width_cells // 2
            y0 = cy - height_cells // 2
            z0 = cz - thickness_cells // 2
            
            # Criar máscara
            mask = geometry.create_planar_intrusion(
                self.model.x_grid, self.model.y_grid, self.model.z_grid,
                x0 * self.model.dx, y0 * self.model.dy, z0 * self.model.dz,
                width, height, thickness
            )
        
        elif geometry_type == 'Cilíndrica (Dique)':
            # Intrusão cilíndrica (dique)
            radius = intrusion.get('radius', 100)
            height = intrusion.get('height', 500)
            
            # Converter para células
            height_cells = int(height / self.model.dz)
            
            # Posição da intrusão
            z0 = cz - height_cells // 2
            
            # Criar máscara
            mask = geometry.create_cylindrical_intrusion(
                self.model.x_grid, self.model.y_grid, self.model.z_grid,
                cx * self.model.dx, cy * self.model.dy, z0 * self.model.dz,
                radius, height
            )
        
        elif geometry_type == 'Esférica (Plúton)':
            # Intrusão esférica (plúton)
            radius = intrusion.get('radius', 100)
            
            # Criar máscara
            mask = geometry.create_spherical_intrusion(
                self.model.x_grid, self.model.y_grid, self.model.z_grid,
                cx * self.model.dx, cy * self.model.dy, cz * self.model.dz,
                radius
            )
        
        else:  # Complexa
            # Intrusão complexa
            components = []
            
            # Adicionar componente planar
            if 'thickness' in intrusion and 'width' in intrusion and 'height' in intrusion:
                thickness = intrusion.get('thickness', 50)
                width = intrusion.get('width', 500)
                height = intrusion.get('height', 500)
                
                # Converter para células
                thickness_cells = int(thickness / self.model.dz)
                width_cells = int(width / self.model.dx)
                height_cells = int(height / self.model.dy)
                
                # Posição da intrusão
                x0 = cx - width_cells // 2
                y0 = cy - height_cells // 2
                z0 = cz - thickness_cells // 2
                
                components.append({
                    'type': 'planar',
                    'x0': x0 * self.model.dx,
                    'y0': y0 * self.model.dy,
                    'z0': z0 * self.model.dz,
                    'width': width,
                    'height': height,
                    'thickness': thickness
                })
            
            # Adicionar componente esférica
            if 'radius' in intrusion:
                radius = intrusion.get('radius', 100)
                
                components.append({
                    'type': 'spherical',
                    'x0': cx * self.model.dx,
                    'y0': cy * self.model.dy,
                    'z0': cz * self.model.dz,
                    'radius': radius
                })
            
            # Criar máscara
            mask = geometry.create_complex_intrusion(
                self.model.x_grid, self.model.y_grid, self.model.z_grid,
                components
            )
        
        # Definir temperatura da intrusão
        if mask is not None:
            self.model.set_temperature(mask, self.model.magma_temperature)
    
    def add_history_points(self):
        """Adiciona pontos para monitoramento de temperatura."""
        if not self.model:
            return
        
        # Centro do domínio
        cx = self.model.nx // 2
        cy = self.model.ny // 2
        cz = self.model.nz // 2
        
        # Adicionar pontos
        self.model.add_history_point((cx, cy, cz))  # Centro
        self.model.add_history_point((cx + 10, cy, cz))  # Próximo ao centro
        self.model.add_history_point((cx + 20, cy, cz))  # Mais afastado
        self.model.add_history_point((cx + 50, cy, cz))  # Distante
    
    def on_time_changed(self, time_index):
        """
        Manipula a alteração do tempo na interface.
        
        Parâmetros:
            time_index (int): Índice do ponto de tempo
        """
        if not self.temperature_data or time_index >= len(self.temperature_data):
            return
        
        # Atualizar visualizações
        self.main_window.visualization_panel.set_time_index(time_index)
        
        # Atualizar temperatura
        if self.model and time_index < len(self.time_points):
            # Obter temperatura no centro
            cx = self.model.nx // 2
            cy = self.model.ny // 2
            cz = self.model.nz // 2
            
            temperature = self.temperature_data[time_index][cx, cy, cz]
            self.temperature_updated.emit(temperature)
    
    def start_simulation(self, params):
        """
        Inicia a simulação.
        
        Parâmetros:
            params (dict): Parâmetros da simulação
        """
        if not self.model or self.is_running:
            return
        
        # Extrair parâmetros
        simulation_params = params.get('simulation', {})
        time_params = simulation_params.get('time', {})
        
        duration = time_params.get('duration', 1e6)
        save_interval = time_params.get('save_interval', 1e5)
        
        # Atualizar estado
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        
        # Atualizar interface
        self.main_window.simulation_control.simulation_started()
        
        # Iniciar simulação em thread separada
        thread = threading.Thread(target=self.run_simulation, args=(duration, save_interval))
        thread.daemon = True
        thread.start()
    
    def run_simulation(self, duration, save_interval):
        """
        Executa a simulação.
        
        Parâmetros:
            duration (float): Duração da simulação (s)
            save_interval (float): Intervalo de salvamento (s)
        """
        # Limpar dados anteriores
        self.temperature_data = []
        self.time_points = []
        
        # Adicionar estado inicial
        self.temperature_data.append(self.model.temperature.copy())
        self.time_points.append(self.model.time)
        
        # Calcular número de passos
        n_steps = int(duration / save_interval)
        
        # Executar simulação
        for i in range(n_steps):
            # Verificar se a simulação foi parada
            if not self.is_running:
                break
            
            # Verificar se a simulação foi pausada
            while self.is_paused:
                time.sleep(0.1)
                
                # Verificar se a simulação foi parada durante a pausa
                if not self.is_running:
                    break
            
            # Simular até o próximo ponto de salvamento
            target_time = (i + 1) * save_interval
            self.model.simulate_to(target_time)
            
            # Salvar estado
            self.temperature_data.append(self.model.temperature.copy())
            self.time_points.append(self.model.time)
            
            # Atualizar progresso
            progress = int((i + 1) / n_steps * 100)
            self.simulation_progress.emit(progress)
        
        # Atualizar estado
        self.is_running = False
        
        # Atualizar interface
        self.simulation_completed.emit(self.time_points)
        
        # Atualizar visualizações
        self.update_visualizations()
    
    def pause_simulation(self):
        """Pausa ou retoma a simulação."""
        if not self.is_running:
            return
        
        # Alternar estado de pausa
        self.is_paused = not self.is_paused
        
        # Atualizar interface
        self.main_window.simulation_control.simulation_paused()
    
    def stop_simulation(self):
        """Para a simulação."""
        # Atualizar estado
        self.is_running = False
        self.is_paused = False
        
        # Atualizar interface
        self.main_window.simulation_control.simulation_stopped()
    
    def update_visualizations(self):
        """Atualiza as visualizações com os dados atuais."""
        # Verificar se há dados
        if not self.temperature_data:
            return
        
        # Atualizar painel de visualização
        self.main_window.visualization_panel.set_data(
            self.temperature_data,
            self.time_points,
            self.model.temperature_history if self.model else None
        )
