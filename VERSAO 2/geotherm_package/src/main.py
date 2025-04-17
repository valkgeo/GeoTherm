"""
GeoTherm - Versão Final

Este módulo implementa a versão final do GeoTherm, combinando todas as funcionalidades
avançadas com a estabilidade e compatibilidade necessárias.
"""
import sys
import os
import time
import traceback
import numpy as np
import threading

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QSplitter, QDoubleSpinBox,
                            QMessageBox, QApplication, QFileDialog, QComboBox, 
                            QGroupBox, QFormLayout, QCheckBox, QSlider, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QColor, QPalette, QFont, QIcon

# Adicionar diretório pai ao path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


# Importar módulos do GeoTherm
from src.gui.splash_screen import show_splash_screen
from src.gui.main_window import MainWindow
from src.integrator import ModelIntegrator



# Importar módulos para visualização
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    print("Aviso: Matplotlib não encontrado. Visualização 2D será limitada.")
    HAS_MATPLOTLIB = False

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    HAS_PYVISTA = True
except ImportError:
    print("Aviso: PyVista não encontrado. Visualização 3D será limitada.")
    HAS_PYVISTA = False

# Classe para modelo térmico
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
        # Verificar se o ponto está dentro do domínio
        x, y, z = point
        if 0 <= x < self.nx and 0 <= y < self.ny and 0 <= z < self.nz:
            self.history_points.add(point)
            self.temperature_history[point] = [(self.time, self.temperature[point])]
        else:
            print(f"Aviso: Ponto {point} está fora do domínio e será ignorado.")
    
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
        
        # Calcular laplaciano usando convolução
        from scipy.ndimage import convolve
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
    
    def create_intrusion(self, geometry_type, params):
        """
        Cria uma intrusão com a geometria especificada.
        
        Parâmetros:
            geometry_type (str): Tipo de geometria ('planar', 'cylindrical', 'spherical')
            params (dict): Parâmetros da geometria
        
        Retorna:
            ndarray: Máscara booleana 3D indicando a região da intrusão
        """
        # Centro do domínio
        cx = self.nx // 2
        cy = self.ny // 2
        cz = self.nz // 2
        
        # Criar máscara
        mask = np.zeros((self.nx, self.ny, self.nz), dtype=bool)
        
        if geometry_type == 'planar':
            # Intrusão planar (sill)
            thickness = params.get('thickness', 50)
            width = params.get('width', 500)
            height = params.get('height', 500)
            
            # Converter para células
            thickness_cells = int(thickness / self.dz)
            width_cells = int(width / self.dx)
            height_cells = int(height / self.dy)
            
            # Posição da intrusão
            x0 = cx - width_cells // 2
            y0 = cy - height_cells // 2
            z0 = cz - thickness_cells // 2
            
            # Criar máscara
            for i in range(x0, x0 + width_cells):
                for j in range(y0, y0 + height_cells):
                    for k in range(z0, z0 + thickness_cells):
                        if 0 <= i < self.nx and 0 <= j < self.ny and 0 <= k < self.nz:
                            mask[i, j, k] = True
        
        elif geometry_type == 'cylindrical':
            # Intrusão cilíndrica (dique)
            radius = params.get('radius', 100)
            height = params.get('height', 500)
            
            # Converter para células
            radius_cells = int(radius / self.dx)
            height_cells = int(height / self.dz)
            
            # Posição da intrusão
            z0 = cz - height_cells // 2
            
            # Criar máscara
            for i in range(self.nx):
                for j in range(self.ny):
                    for k in range(z0, z0 + height_cells):
                        # Distância ao centro
                        dist = np.sqrt((i - cx)**2 + (j - cy)**2)
                        
                        # Dentro do cilindro
                        if dist <= radius_cells and 0 <= k < self.nz:
                            mask[i, j, k] = True
        
        elif geometry_type == 'spherical':
            # Intrusão esférica (plúton)
            radius = params.get('radius', 100)
            
            # Converter para células
            radius_cells = int(radius / self.dx)
            
            # Criar máscara
            for i in range(self.nx):
                for j in range(self.ny):
                    for k in range(self.nz):
                        # Distância ao centro
                        dist = np.sqrt((i - cx)**2 + (j - cy)**2 + (k - cz)**2)
                        
                        # Dentro da esfera
                        if dist <= radius_cells:
                            mask[i, j, k] = True
        
        return mask

# Classe para tela de carregamento
class SplashScreen(QWidget):
    """Tela de carregamento personalizada em tons de vermelho."""
    
    def __init__(self):
        """Inicializa a tela de carregamento."""
        super().__init__()
        
        # Configurar janela
        self.setWindowTitle("GeoTherm")
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setFixedSize(400, 300)
        
        # Centralizar na tela
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Configurar layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Espaçador superior
        layout.addStretch(1)
        
        # Logo GT
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_label = QLabel()
        logo_label.setFixedSize(100, 100)
        logo_label.setStyleSheet("background-color: white; border-radius: 10px;")
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Texto GT
        logo_text = QLabel("GT")
        logo_text.setStyleSheet("font-size: 48pt; font-weight: bold; color: #990000;")
        logo_text.setAlignment(Qt.AlignCenter)
        
        logo_label.setLayout(QVBoxLayout())
        logo_label.layout().addWidget(logo_text)
        logo_label.layout().setContentsMargins(0, 0, 0, 0)
        
        logo_layout.addStretch(1)
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch(1)
        
        layout.addWidget(logo_container)
        
        # Nome do programa
        name_label = QLabel("GeoTherm")
        name_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: white;")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 100);
                border-radius: 5px;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: white;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Espaçador inferior
        layout.addStretch(1)
        
        # Configurar estilo
        self.setStyleSheet("""
            SplashScreen {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #990000, stop:1 #ff3333);
            }
        """)
        
        # Timer para atualizar progresso
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)
        
        # Valor atual do progresso
        self.current_progress = 0
    
    def update_progress(self):
        """Atualiza o progresso da barra."""
        if self.current_progress < 100:
            self.current_progress += 1
            self.progress_bar.setValue(self.current_progress)
        else:
            self.timer.stop()
            self.close()
    
    def set_progress(self, value):
        """Define o valor do progresso."""
        self.current_progress = value
        self.progress_bar.setValue(value)

# Classe para painel de parâmetros
class ParameterPanel(QWidget):
    """Painel para configuração de parâmetros."""
    
    # Sinal para notificar alteração de parâmetros
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Inicializa o painel de parâmetros."""
        super().__init__(parent)
        
        # Dicionário de parâmetros
        self.parameters = {
            'geometry': {
                'geometry_type': 'Planar (Sill)',
                'domain': {
                    'nx': 100,
                    'ny': 100,
                    'nz': 100,
                    'cell_size': 10
                },
                'intrusion': {
                    'thickness': 50,
                    'width': 500,
                    'height': 500,
                    'radius': 100
                }
            },
            'thermal': {
                'properties': {
                    'diffusivity': 1e-6,
                    'conductivity': 2.5,
                    'specific_heat': 1000,
                    'density': 2700
                },
                'temperatures': {
                    'background': 20,
                    'magma': 1200
                },
                'latent_heat': {
                    'use_latent_heat': False,
                    'solidus': 700,
                    'liquidus': 1200,
                    'latent_heat': 400000
                }
            },
            'simulation': {
                'time': {
                    'duration': 1e6,
                    'save_interval': 1e5
                },
                'modules': {
                    'convection': False
                },
                'convection': {
                    'flow_type': 'Célula de Convecção',
                    'max_velocity': 1e-6
                }
            }
        }
        
        # Configurar layout
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do usuário."""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Abas
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Aba de geometria
        geometry_tab = QWidget()
        tabs.addTab(geometry_tab, "Geometria")
        self.create_geometry_tab(geometry_tab)
        
        # Aba de propriedades térmicas
        thermal_tab = QWidget()
        tabs.addTab(thermal_tab, "Propriedades Térmicas")
        self.create_thermal_tab(thermal_tab)
        
        # Aba de simulação
        simulation_tab = QWidget()
        tabs.addTab(simulation_tab, "Simulação")
        self.create_simulation_tab(simulation_tab)
        
        # Botões
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        # Botão para aplicar parâmetros
        apply_button = QPushButton("Aplicar Parâmetros")
        apply_button.clicked.connect(self.apply_parameters)
        button_layout.addWidget(apply_button)
        
        # Botão para redefinir parâmetros
        reset_button = QPushButton("Redefinir")
        reset_button.clicked.connect(self.reset_parameters)
        button_layout.addWidget(reset_button)
    
    def create_geometry_tab(self, tab):
        """Cria a aba de geometria."""
        # Layout principal
        layout = QVBoxLayout(tab)
        
        # Grupo de tipo de geometria
        geometry_group = QGroupBox("Tipo de Geometria")
        layout.addWidget(geometry_group)
        
        geometry_layout = QFormLayout(geometry_group)
        
        # Combobox para tipo de geometria
        self.geometry_type_combo = QComboBox()
        self.geometry_type_combo.addItems([
            "Planar (Sill)",
            "Cilíndrica (Dique)",
            "Esférica (Plúton)"
        ])
        self.geometry_type_combo.currentTextChanged.connect(self.on_geometry_type_changed)
        geometry_layout.addRow("Tipo:", self.geometry_type_combo)
        
        # Grupo de domínio
        domain_group = QGroupBox("Domínio")
        layout.addWidget(domain_group)
        
        domain_layout = QFormLayout(domain_group)
        
        # Spinboxes para dimensões do domínio
        self.nx_spin = QDoubleSpinBox()
        self.nx_spin.setRange(10, 500)
        self.nx_spin.setValue(self.parameters['geometry']['domain']['nx'])
        self.nx_spin.setDecimals(0)
        domain_layout.addRow("Nx:", self.nx_spin)
        
        self.ny_spin = QDoubleSpinBox()
        self.ny_spin.setRange(10, 500)
        self.ny_spin.setValue(self.parameters['geometry']['domain']['ny'])
        self.ny_spin.setDecimals(0)
        domain_layout.addRow("Ny:", self.ny_spin)
        
        self.nz_spin = QDoubleSpinBox()
        self.nz_spin.setRange(10, 500)
        self.nz_spin.setValue(self.parameters['geometry']['domain']['nz'])
        self.nz_spin.setDecimals(0)
        domain_layout.addRow("Nz:", self.nz_spin)
        
        self.cell_size_spin = QDoubleSpinBox()
        self.cell_size_spin.setRange(1, 100)
        self.cell_size_spin.setValue(self.parameters['geometry']['domain']['cell_size'])
        self.cell_size_spin.setSuffix(" m")
        domain_layout.addRow("Tamanho da Célula:", self.cell_size_spin)
        
        # Grupo de intrusão
        self.intrusion_group = QGroupBox("Intrusão")
        layout.addWidget(self.intrusion_group)
        
        self.intrusion_layout = QFormLayout(self.intrusion_group)
        
        # Spinboxes para parâmetros da intrusão
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(1, 1000)
        self.thickness_spin.setValue(self.parameters['geometry']['intrusion']['thickness'])
        self.thickness_spin.setSuffix(" m")
        self.intrusion_layout.addRow("Espessura:", self.thickness_spin)
        
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(self.parameters['geometry']['intrusion']['width'])
        self.width_spin.setSuffix(" m")
        self.intrusion_layout.addRow("Largura:", self.width_spin)
        
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(self.parameters['geometry']['intrusion']['height'])
        self.height_spin.setSuffix(" m")
        self.intrusion_layout.addRow("Altura:", self.height_spin)
        
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(1, 5000)
        self.radius_spin.setValue(self.parameters['geometry']['intrusion']['radius'])
        self.radius_spin.setSuffix(" m")
        self.radius_label = self.intrusion_layout.addRow("Raio:", self.radius_spin)
        
        # Atualizar visibilidade dos campos
        self.update_intrusion_fields()
        
        # Espaçador
        layout.addStretch(1)
    
    def create_thermal_tab(self, tab):
        """Cria a aba de propriedades térmicas."""
        # Layout principal
        layout = QVBoxLayout(tab)
        
        # Grupo de propriedades térmicas
        properties_group = QGroupBox("Propriedades Térmicas")
        layout.addWidget(properties_group)
        
        properties_layout = QFormLayout(properties_group)
        
        # Spinboxes para propriedades térmicas
        self.diffusivity_spin = QDoubleSpinBox()
        self.diffusivity_spin.setRange(1e-8, 1e-4)
        self.diffusivity_spin.setValue(self.parameters['thermal']['properties']['diffusivity'])
        self.diffusivity_spin.setDecimals(8)
        self.diffusivity_spin.setSingleStep(1e-7)
        properties_layout.addRow("Difusividade (m²/s):", self.diffusivity_spin)
        
        self.conductivity_spin = QDoubleSpinBox()
        self.conductivity_spin.setRange(0.1, 10)
        self.conductivity_spin.setValue(self.parameters['thermal']['properties']['conductivity'])
        self.conductivity_spin.setSuffix(" W/(m·K)")
        properties_layout.addRow("Condutividade:", self.conductivity_spin)
        
        self.specific_heat_spin = QDoubleSpinBox()
        self.specific_heat_spin.setRange(100, 5000)
        self.specific_heat_spin.setValue(self.parameters['thermal']['properties']['specific_heat'])
        self.specific_heat_spin.setSuffix(" J/(kg·K)")
        properties_layout.addRow("Calor Específico:", self.specific_heat_spin)
        
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(1000, 5000)
        self.density_spin.setValue(self.parameters['thermal']['properties']['density'])
        self.density_spin.setSuffix(" kg/m³")
        properties_layout.addRow("Densidade:", self.density_spin)
        
        # Grupo de temperaturas
        temperatures_group = QGroupBox("Temperaturas")
        layout.addWidget(temperatures_group)
        
        temperatures_layout = QFormLayout(temperatures_group)
        
        # Spinboxes para temperaturas
        self.background_temp_spin = QDoubleSpinBox()
        self.background_temp_spin.setRange(0, 100)
        self.background_temp_spin.setValue(self.parameters['thermal']['temperatures']['background'])
        self.background_temp_spin.setSuffix(" °C")
        temperatures_layout.addRow("Temperatura do Encaixante:", self.background_temp_spin)
        
        self.magma_temp_spin = QDoubleSpinBox()
        self.magma_temp_spin.setRange(600, 1500)
        self.magma_temp_spin.setValue(self.parameters['thermal']['temperatures']['magma'])
        self.magma_temp_spin.setSuffix(" °C")
        temperatures_layout.addRow("Temperatura do Magma:", self.magma_temp_spin)
        
        # Grupo de calor latente
        latent_heat_group = QGroupBox("Calor Latente")
        layout.addWidget(latent_heat_group)
        
        latent_heat_layout = QFormLayout(latent_heat_group)
        
        # Checkbox para ativar calor latente
        self.use_latent_heat_check = QCheckBox()
        self.use_latent_heat_check.setChecked(self.parameters['thermal']['latent_heat']['use_latent_heat'])
        self.use_latent_heat_check.stateChanged.connect(self.on_latent_heat_changed)
        latent_heat_layout.addRow("Usar Calor Latente:", self.use_latent_heat_check)
        
        # Spinboxes para parâmetros de calor latente
        self.solidus_spin = QDoubleSpinBox()
        self.solidus_spin.setRange(500, 1000)
        self.solidus_spin.setValue(self.parameters['thermal']['latent_heat']['solidus'])
        self.solidus_spin.setSuffix(" °C")
        latent_heat_layout.addRow("Temperatura Solidus:", self.solidus_spin)
        
        self.liquidus_spin = QDoubleSpinBox()
        self.liquidus_spin.setRange(800, 1500)
        self.liquidus_spin.setValue(self.parameters['thermal']['latent_heat']['liquidus'])
        self.liquidus_spin.setSuffix(" °C")
        latent_heat_layout.addRow("Temperatura Liquidus:", self.liquidus_spin)
        
        self.latent_heat_spin = QDoubleSpinBox()
        self.latent_heat_spin.setRange(100000, 1000000)
        self.latent_heat_spin.setValue(self.parameters['thermal']['latent_heat']['latent_heat'])
        self.latent_heat_spin.setSuffix(" J/kg")
        latent_heat_layout.addRow("Calor Latente:", self.latent_heat_spin)
        
        # Atualizar visibilidade dos campos
        self.update_latent_heat_fields()
        
        # Espaçador
        layout.addStretch(1)
    
    def create_simulation_tab(self, tab):
        """Cria a aba de simulação."""
        # Layout principal
        layout = QVBoxLayout(tab)
        
        # Grupo de tempo
        time_group = QGroupBox("Tempo")
        layout.addWidget(time_group)
        
        time_layout = QFormLayout(time_group)
        
        # Spinboxes para parâmetros de tempo
        # Criar primeiro os objetos
        self.duration_spin = QDoubleSpinBox()
        self.save_interval_spin = QDoubleSpinBox()
        
        # Configurar duration_spin
        self.duration_spin.setRange(1, 1e10)
        self.duration_spin.setValue(self.parameters['simulation']['time']['duration'])
        self.duration_spin.setDecimals(1)
        self.duration_spin.setSingleStep(1e5)
        try:
            self.duration_spin.setNotation(QDoubleSpinBox.ScientificNotation)
        except AttributeError:
            pass
        time_layout.addRow("Duração da Simulação (s):", self.duration_spin)
        
        # Configurar save_interval_spin
        self.save_interval_spin.setRange(1, 1e9)
        self.save_interval_spin.setValue(self.parameters['simulation']['time']['save_interval'])
        self.save_interval_spin.setDecimals(1)
        self.save_interval_spin.setSingleStep(1e4)
        try:
            self.save_interval_spin.setNotation(QDoubleSpinBox.ScientificNotation)
        except AttributeError:
            pass
        time_layout.addRow("Intervalo de Salvamento (s):", self.save_interval_spin)
        
        # Grupo de módulos
        modules_group = QGroupBox("Módulos")
        layout.addWidget(modules_group)
        
        modules_layout = QFormLayout(modules_group)
        
        # Checkbox para ativar convecção
        self.use_convection_check = QCheckBox()
        self.use_convection_check.setChecked(self.parameters['simulation']['modules']['convection'])
        self.use_convection_check.stateChanged.connect(self.on_convection_changed)
        modules_layout.addRow("Usar Convecção:", self.use_convection_check)
        
        # Grupo de convecção
        self.convection_group = QGroupBox("Convecção")
        layout.addWidget(self.convection_group)
        
        convection_layout = QFormLayout(self.convection_group)
        
        # Combobox para tipo de fluxo
        self.flow_type_combo = QComboBox()
        self.flow_type_combo.addItems([
            "Célula de Convecção",
            "Fluxo Ascendente",
            "Fluxo Lateral"
        ])
        self.flow_type_combo.setCurrentText(self.parameters['simulation']['convection']['flow_type'])
        convection_layout.addRow("Tipo de Fluxo:", self.flow_type_combo)
        
        # Spinbox para velocidade máxima
        self.max_velocity_spin = QDoubleSpinBox()
        self.max_velocity_spin.setRange(1e-8, 1e-4)
        self.max_velocity_spin.setValue(self.parameters['simulation']['convection']['max_velocity'])
        self.max_velocity_spin.setDecimals(8)
        self.max_velocity_spin.setSingleStep(1e-7)
        self.max_velocity_spin.setSuffix(" m/s")
        convection_layout.addRow("Velocidade Máxima:", self.max_velocity_spin)
        
        # Atualizar visibilidade dos campos
        self.update_convection_fields()
        
        # Espaçador
        layout.addStretch(1)
    
    def on_geometry_type_changed(self, text):
        """Manipula a alteração do tipo de geometria."""
        self.parameters['geometry']['geometry_type'] = text
        self.update_intrusion_fields()
    
    def update_intrusion_fields(self):
        """Atualiza os campos de intrusão com base no tipo de geometria."""
        geometry_type = self.parameters['geometry']['geometry_type']
        
        # Mostrar/ocultar campos com base no tipo de geometria
        if geometry_type == "Planar (Sill)":
            self.thickness_spin.setVisible(True)
            self.intrusion_layout.labelForField(self.thickness_spin).setVisible(True)
            self.width_spin.setVisible(True)
            self.intrusion_layout.labelForField(self.width_spin).setVisible(True)
            self.height_spin.setVisible(True)
            self.intrusion_layout.labelForField(self.height_spin).setVisible(True)
            self.radius_spin.setVisible(False)
            self.intrusion_layout.labelForField(self.radius_spin).setVisible(False)
        
        elif geometry_type == "Cilíndrica (Dique)":
            self.thickness_spin.setVisible(False)
            self.intrusion_layout.labelForField(self.thickness_spin).setVisible(False)
            self.width_spin.setVisible(False)
            self.intrusion_layout.labelForField(self.width_spin).setVisible(False)
            self.height_spin.setVisible(True)
            self.intrusion_layout.labelForField(self.height_spin).setVisible(True)
            self.radius_spin.setVisible(True)
            self.intrusion_layout.labelForField(self.radius_spin).setVisible(True)
        
        elif geometry_type == "Esférica (Plúton)":
            self.thickness_spin.setVisible(False)
            self.intrusion_layout.labelForField(self.thickness_spin).setVisible(False)
            self.width_spin.setVisible(False)
            self.intrusion_layout.labelForField(self.width_spin).setVisible(False)
            self.height_spin.setVisible(False)
            self.intrusion_layout.labelForField(self.height_spin).setVisible(False)
            self.radius_spin.setVisible(True)
            self.intrusion_layout.labelForField(self.radius_spin).setVisible(True)
    
    def on_latent_heat_changed(self, state):
        """Manipula a alteração do uso de calor latente."""
        self.parameters['thermal']['latent_heat']['use_latent_heat'] = bool(state)
        self.update_latent_heat_fields()
    
    def update_latent_heat_fields(self):
        """Atualiza os campos de calor latente com base no estado do checkbox."""
        use_latent_heat = self.parameters['thermal']['latent_heat']['use_latent_heat']
        
        # Habilitar/desabilitar campos com base no estado do checkbox
        self.solidus_spin.setEnabled(use_latent_heat)
        self.liquidus_spin.setEnabled(use_latent_heat)
        self.latent_heat_spin.setEnabled(use_latent_heat)
    
    def on_convection_changed(self, state):
        """Manipula a alteração do uso de convecção."""
        self.parameters['simulation']['modules']['convection'] = bool(state)
        self.update_convection_fields()
    
    def update_convection_fields(self):
        """Atualiza os campos de convecção com base no estado do checkbox."""
        use_convection = self.parameters['simulation']['modules']['convection']
        
        # Mostrar/ocultar grupo de convecção com base no estado do checkbox
        self.convection_group.setVisible(use_convection)
    
    def apply_parameters(self):
        """Aplica os parâmetros configurados."""
        try:
            # Atualizar parâmetros de geometria
            self.parameters['geometry']['geometry_type'] = self.geometry_type_combo.currentText()
            self.parameters['geometry']['domain']['nx'] = int(self.nx_spin.value())
            self.parameters['geometry']['domain']['ny'] = int(self.ny_spin.value())
            self.parameters['geometry']['domain']['nz'] = int(self.nz_spin.value())
            self.parameters['geometry']['domain']['cell_size'] = self.cell_size_spin.value()
            self.parameters['geometry']['intrusion']['thickness'] = self.thickness_spin.value()
            self.parameters['geometry']['intrusion']['width'] = self.width_spin.value()
            self.parameters['geometry']['intrusion']['height'] = self.height_spin.value()
            self.parameters['geometry']['intrusion']['radius'] = self.radius_spin.value()
            
            # Atualizar parâmetros térmicos
            self.parameters['thermal']['properties']['diffusivity'] = self.diffusivity_spin.value()
            self.parameters['thermal']['properties']['conductivity'] = self.conductivity_spin.value()
            self.parameters['thermal']['properties']['specific_heat'] = self.specific_heat_spin.value()
            self.parameters['thermal']['properties']['density'] = self.density_spin.value()
            self.parameters['thermal']['temperatures']['background'] = self.background_temp_spin.value()
            self.parameters['thermal']['temperatures']['magma'] = self.magma_temp_spin.value()
            self.parameters['thermal']['latent_heat']['use_latent_heat'] = self.use_latent_heat_check.isChecked()
            self.parameters['thermal']['latent_heat']['solidus'] = self.solidus_spin.value()
            self.parameters['thermal']['latent_heat']['liquidus'] = self.liquidus_spin.value()
            self.parameters['thermal']['latent_heat']['latent_heat'] = self.latent_heat_spin.value()
            
            # Atualizar parâmetros de simulação
            self.parameters['simulation']['time']['duration'] = self.duration_spin.value()
            self.parameters['simulation']['time']['save_interval'] = self.save_interval_spin.value()
            self.parameters['simulation']['modules']['convection'] = self.use_convection_check.isChecked()
            self.parameters['simulation']['convection']['flow_type'] = self.flow_type_combo.currentText()
            self.parameters['simulation']['convection']['max_velocity'] = self.max_velocity_spin.value()
            
            # Emitir sinal de alteração de parâmetros
            self.parameters_changed.emit(self.parameters)
            
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao aplicar parâmetros: {str(e)}")
            traceback.print_exc()
            return False
    
    def reset_parameters(self):
        """Redefine os parâmetros para valores padrão."""
        try:
            # Redefinir parâmetros de geometria
            self.geometry_type_combo.setCurrentText("Planar (Sill)")
            self.nx_spin.setValue(100)
            self.ny_spin.setValue(100)
            self.nz_spin.setValue(100)
            self.cell_size_spin.setValue(10)
            self.thickness_spin.setValue(50)
            self.width_spin.setValue(500)
            self.height_spin.setValue(500)
            self.radius_spin.setValue(100)
            
            # Redefinir parâmetros térmicos
            self.diffusivity_spin.setValue(1e-6)
            self.conductivity_spin.setValue(2.5)
            self.specific_heat_spin.setValue(1000)
            self.density_spin.setValue(2700)
            self.background_temp_spin.setValue(20)
            self.magma_temp_spin.setValue(1200)
            self.use_latent_heat_check.setChecked(False)
            self.solidus_spin.setValue(700)
            self.liquidus_spin.setValue(1200)
            self.latent_heat_spin.setValue(400000)
            
            # Redefinir parâmetros de simulação
            self.duration_spin.setValue(1e6)
            self.save_interval_spin.setValue(1e5)
            self.use_convection_check.setChecked(False)
            self.flow_type_combo.setCurrentText("Célula de Convecção")
            self.max_velocity_spin.setValue(1e-6)
            
            # Atualizar visibilidade dos campos
            self.update_intrusion_fields()
            self.update_latent_heat_fields()
            self.update_convection_fields()
            
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao redefinir parâmetros: {str(e)}")
            traceback.print_exc()
            return False

# Classe para painel de visualização
class VisualizationPanel(QWidget):
    """Painel para visualização dos resultados."""
    
    def __init__(self, parent=None):
        """Inicializa o painel de visualização."""
        super().__init__(parent)
        
        # Dados
        self.temperature_data = None
        self.time_points = None
        self.temperature_history = None
        
        # Índice de tempo atual
        self.time_index = 0
        
        # Configurar layout
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do usuário."""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Abas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Aba de visualização 3D
        self.viz_3d_tab = QWidget()
        self.tabs.addTab(self.viz_3d_tab, "Visualização 3D")
        self.create_3d_tab(self.viz_3d_tab)
        
        # Aba de cortes 2D
        self.slices_tab = QWidget()
        self.tabs.addTab(self.slices_tab, "Cortes 2D")
        self.create_slices_tab(self.slices_tab)
        
        # Aba de gráficos de temperatura
        self.graphs_tab = QWidget()
        self.tabs.addTab(self.graphs_tab, "Gráficos de Temperatura")
        self.create_graphs_tab(self.graphs_tab)
    
    def create_3d_tab(self, tab):
        """Cria a aba de visualização 3D."""
        # Layout principal
        layout = QVBoxLayout(tab)
        
        if HAS_PYVISTA:
            # Criar widget de visualização 3D
            self.plotter = QtInteractor(tab)
            layout.addWidget(self.plotter)
            
            # Adicionar controles
            controls_layout = QHBoxLayout()
            layout.addLayout(controls_layout)
            
            # Slider para isosuperfície
            iso_layout = QVBoxLayout()
            controls_layout.addLayout(iso_layout)
            
            iso_label = QLabel("Isosuperfície (°C):")
            iso_layout.addWidget(iso_label)
            
            self.iso_slider = QSlider(Qt.Horizontal)
            self.iso_slider.setRange(0, 1200)
            self.iso_slider.setValue(600)
            self.iso_slider.valueChanged.connect(self.update_isosurface)
            iso_layout.addWidget(self.iso_slider)
            
            # Botão para alternar entre isosuperfície e volume
            self.viz_mode_button = QPushButton("Alternar para Volume")
            self.viz_mode_button.clicked.connect(self.toggle_viz_mode)
            controls_layout.addWidget(self.viz_mode_button)
            
            # Modo de visualização atual
            self.viz_mode = "isosurface"
        else:
            # Mensagem de erro
            error_label = QLabel("PyVista não encontrado. Visualização 3D não disponível.")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
    
    def create_slices_tab(self, tab):
        """Cria a aba de cortes 2D."""
        # Layout principal
        layout = QVBoxLayout(tab)
        
        if HAS_MATPLOTLIB:
            # Criar widget de visualização 2D
            self.slice_figure = Figure(figsize=(5, 4), dpi=100)
            self.slice_canvas = FigureCanvas(self.slice_figure)
            layout.addWidget(self.slice_canvas)
            
            # Adicionar controles
            controls_layout = QHBoxLayout()
            layout.addLayout(controls_layout)
            
            # Combobox para eixo
            axis_layout = QVBoxLayout()
            controls_layout.addLayout(axis_layout)
            
            axis_label = QLabel("Eixo:")
            axis_layout.addWidget(axis_label)
            
            self.axis_combo = QComboBox()
            self.axis_combo.addItems(["X", "Y", "Z"])
            self.axis_combo.currentTextChanged.connect(self.update_slice)
            axis_layout.addWidget(self.axis_combo)
            
            # Slider para posição
            position_layout = QVBoxLayout()
            controls_layout.addLayout(position_layout)
            
            position_label = QLabel("Posição:")
            position_layout.addWidget(position_label)
            
            self.position_slider = QSlider(Qt.Horizontal)
            self.position_slider.setRange(0, 99)
            self.position_slider.setValue(50)
            self.position_slider.valueChanged.connect(self.update_slice)
            position_layout.addWidget(self.position_slider)
        else:
            # Mensagem de erro
            error_label = QLabel("Matplotlib não encontrado. Visualização 2D não disponível.")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
    
    def create_graphs_tab(self, tab):
        """Cria a aba de gráficos de temperatura."""
        # Layout principal
        layout = QVBoxLayout(tab)
        
        if HAS_MATPLOTLIB:
            # Criar widget de visualização de gráficos
            self.graph_figure = Figure(figsize=(5, 4), dpi=100)
            self.graph_canvas = FigureCanvas(self.graph_figure)
            layout.addWidget(self.graph_canvas)
        else:
            # Mensagem de erro
            error_label = QLabel("Matplotlib não encontrado. Gráficos não disponíveis.")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
    
    def set_data(self, temperature_data, time_points, temperature_history):
        """
        Define os dados para visualização.
        
        Parâmetros:
            temperature_data (list): Lista de arrays 3D de temperatura
            time_points (list): Lista de pontos de tempo
            temperature_history (dict): Dicionário com histórico de temperatura
        """
        self.temperature_data = temperature_data
        self.time_points = time_points
        self.temperature_history = temperature_history
        
        # Atualizar visualizações
        self.update_visualizations()
    
    def set_time_index(self, index):
        """
        Define o índice de tempo atual.
        
        Parâmetros:
            index (int): Índice do ponto de tempo
        """
        if self.temperature_data and 0 <= index < len(self.temperature_data):
            self.time_index = index
            
            # Atualizar visualizações
            self.update_visualizations()
    
    def update_visualizations(self):
        """Atualiza todas as visualizações."""
        if not self.temperature_data:
            return
        
        # Atualizar visualização 3D
        self.update_3d_visualization()
        
        # Atualizar cortes 2D
        self.update_slice()
        
        # Atualizar gráficos de temperatura
        self.update_graphs()
    
    def update_3d_visualization(self):
        """Atualiza a visualização 3D."""
        if not HAS_PYVISTA or not self.temperature_data:
            return
        
        try:
            # Limpar visualização anterior
            self.plotter.clear()
            
            # Obter dados de temperatura
            temperature = self.temperature_data[self.time_index]
            
            # Criar grid 3D
            grid = pv.UniformGrid()
            grid.dimensions = np.array(temperature.shape) + 1
            grid.origin = (0, 0, 0)
            grid.spacing = (1, 1, 1)
            
            # Adicionar dados de temperatura
            grid.cell_data["temperature"] = temperature.flatten(order="F")
            
            # Adicionar visualização
            if self.viz_mode == "isosurface":
                # Isosuperfície
                iso_value = self.iso_slider.value()
                self.plotter.add_mesh(grid.contour([iso_value]), cmap="hot", clim=[0, 1200])
            else:
                # Volume
                self.plotter.add_volume(grid, cmap="hot", clim=[0, 1200])
            
            # Adicionar escala de cores
            self.plotter.add_scalar_bar("Temperatura (°C)")
            
            # Atualizar visualização
            self.plotter.reset_camera()
            self.plotter.update()
        except Exception as e:
            print(f"Erro ao atualizar visualização 3D: {str(e)}")
            traceback.print_exc()
    
    def update_isosurface(self):
        """Atualiza a isosuperfície."""
        if self.viz_mode == "isosurface":
            self.update_3d_visualization()
    
    def toggle_viz_mode(self):
        """Alterna entre isosuperfície e volume."""
        if self.viz_mode == "isosurface":
            self.viz_mode = "volume"
            self.viz_mode_button.setText("Alternar para Isosuperfície")
        else:
            self.viz_mode = "isosurface"
            self.viz_mode_button.setText("Alternar para Volume")
        
        # Atualizar visualização
        self.update_3d_visualization()
    
    def update_slice(self):
        """Atualiza o corte 2D."""
        if not HAS_MATPLOTLIB or not self.temperature_data:
            return
        
        try:
            # Limpar figura anterior
            self.slice_figure.clear()
            
            # Obter dados de temperatura
            temperature = self.temperature_data[self.time_index]
            
            # Obter eixo e posição
            axis = self.axis_combo.currentText()
            position = self.position_slider.value()
            
            # Ajustar posição para o tamanho do array
            if axis == "X":
                max_pos = temperature.shape[0] - 1
                position = min(position, max_pos)
                slice_data = temperature[position, :, :]
                xlabel, ylabel = "Y", "Z"
            elif axis == "Y":
                max_pos = temperature.shape[1] - 1
                position = min(position, max_pos)
                slice_data = temperature[:, position, :]
                xlabel, ylabel = "X", "Z"
            else:  # Z
                max_pos = temperature.shape[2] - 1
                position = min(position, max_pos)
                slice_data = temperature[:, :, position]
                xlabel, ylabel = "X", "Y"
            
            # Atualizar range do slider
            self.position_slider.setRange(0, max_pos)
            
            # Criar subplot
            ax = self.slice_figure.add_subplot(111)
            
            # Plotar corte
            im = ax.imshow(slice_data, cmap="hot", origin="lower")
            
            # Adicionar barra de cores
            cbar = self.slice_figure.colorbar(im, ax=ax)
            cbar.set_label("Temperatura (°C)")
            
            # Adicionar rótulos
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(f"Corte {axis} = {position}")
            
            # Atualizar canvas
            self.slice_canvas.draw()
        except Exception as e:
            print(f"Erro ao atualizar corte 2D: {str(e)}")
            traceback.print_exc()
    
    def update_graphs(self):
        """Atualiza os gráficos de temperatura."""
        if not HAS_MATPLOTLIB or not self.temperature_data or not self.temperature_history:
            return
        
        try:
            # Limpar figura anterior
            self.graph_figure.clear()
            
            # Criar subplot
            ax = self.graph_figure.add_subplot(111)
            
            # Plotar histórico de temperatura para cada ponto
            for point, history in self.temperature_history.items():
                times = [t for t, _ in history]
                temps = [temp for _, temp in history]
                ax.plot(times, temps, label=f"Ponto {point}")
            
            # Adicionar linha vertical para o tempo atual
            if self.time_points and self.time_index < len(self.time_points):
                current_time = self.time_points[self.time_index]
                ax.axvline(x=current_time, color="r", linestyle="--")
            
            # Adicionar rótulos
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Temperatura (°C)")
            ax.set_title("Evolução da Temperatura")
            
            # Adicionar legenda
            ax.legend()
            
            # Atualizar canvas
            self.graph_canvas.draw()
        except Exception as e:
            print(f"Erro ao atualizar gráficos: {str(e)}")
            traceback.print_exc()

# Classe para controle de simulação
class SimulationControl(QWidget):
    """Controle de simulação."""
    
    # Sinal para notificar alteração de tempo
    time_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Inicializa o controle de simulação."""
        super().__init__(parent)
        
        # Estado da simulação
        self.is_running = False
        self.is_paused = False
        
        # Pontos de tempo
        self.time_points = []
        
        # Configurar layout
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do usuário."""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Controle de Simulação")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Controle de tempo
        time_group = QGroupBox("Controle de Tempo")
        layout.addWidget(time_group)
        
        time_layout = QVBoxLayout(time_group)
        
        # Layout para tempo atual
        time_info_layout = QHBoxLayout()
        time_layout.addLayout(time_info_layout)
        
        # Label para tempo atual
        self.time_label = QLabel("00:00:00")
        time_info_layout.addWidget(self.time_label)
        
        # Slider para tempo
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 0)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self.on_time_changed)
        time_layout.addWidget(self.time_slider)
        
        # Botões de controle
        button_layout = QHBoxLayout()
        time_layout.addLayout(button_layout)
        
        # Botão de início
        self.start_button = QPushButton("Início")
        self.start_button.clicked.connect(self.on_start_clicked)
        button_layout.addWidget(self.start_button)
        
        # Botão de pausa
        self.pause_button = QPushButton("Pausa")
        self.pause_button.clicked.connect(self.on_pause_clicked)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        # Botão de parada
        self.stop_button = QPushButton("Parar")
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        # Informações
        info_group = QGroupBox("Informações")
        layout.addWidget(info_group)
        
        info_layout = QFormLayout(info_group)
        
        # Label para temperatura
        self.temperature_label = QLabel("--")
        info_layout.addRow("Temperatura:", self.temperature_label)
        
        # Barra de progresso
        progress_layout = QVBoxLayout()
        layout.addLayout(progress_layout)
        
        progress_label = QLabel("Progresso:")
        progress_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
    
    def on_time_changed(self, value):
        """
        Manipula a alteração do tempo.
        
        Parâmetros:
            value (int): Valor do slider
        """
        # Atualizar label de tempo
        if self.time_points and value < len(self.time_points):
            time_value = self.time_points[value]
            
            # Converter para formato hh:mm:ss
            hours = int(time_value / 3600)
            minutes = int((time_value % 3600) / 60)
            seconds = int(time_value % 60)
            
            self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Emitir sinal de alteração de tempo
        self.time_changed.emit(value)
    
    def on_start_clicked(self):
        """Manipula o clique no botão de início."""
        # Atualizar estado
        self.is_running = True
        self.is_paused = False
        
        # Atualizar botões
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        # Emitir sinal de início
        self.parent().parent().start_simulation()
    
    def on_pause_clicked(self):
        """Manipula o clique no botão de pausa."""
        # Atualizar estado
        self.is_paused = not self.is_paused
        
        # Atualizar botão
        self.pause_button.setText("Retomar" if self.is_paused else "Pausa")
        
        # Emitir sinal de pausa
        self.parent().parent().pause_simulation()
    
    def on_stop_clicked(self):
        """Manipula o clique no botão de parada."""
        # Atualizar estado
        self.is_running = False
        self.is_paused = False
        
        # Atualizar botões
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pausa")
        self.stop_button.setEnabled(False)
        
        # Emitir sinal de parada
        self.parent().parent().stop_simulation()
    
    def simulation_started(self):
        """Atualiza a interface quando a simulação é iniciada."""
        # Atualizar estado
        self.is_running = True
        self.is_paused = False
        
        # Atualizar botões
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
    
    def simulation_paused(self):
        """Atualiza a interface quando a simulação é pausada."""
        # Atualizar botão
        self.pause_button.setText("Retomar" if self.is_paused else "Pausa")
    
    def simulation_stopped(self):
        """Atualiza a interface quando a simulação é parada."""
        # Atualizar estado
        self.is_running = False
        self.is_paused = False
        
        # Atualizar botões
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pausa")
        self.stop_button.setEnabled(False)
    
    def simulation_completed(self, time_points):
        """
        Atualiza a interface quando a simulação é concluída.
        
        Parâmetros:
            time_points (list): Lista de pontos de tempo
        """
        # Atualizar estado
        self.is_running = False
        self.is_paused = False
        
        # Atualizar botões
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pausa")
        self.stop_button.setEnabled(False)
        
        # Atualizar pontos de tempo
        self.time_points = time_points
        
        # Atualizar slider
        self.time_slider.setRange(0, len(time_points) - 1)
        self.time_slider.setValue(len(time_points) - 1)
        
        # Atualizar barra de progresso
        self.progress_bar.setValue(100)
    
    def set_progress(self, value):
        """
        Define o valor do progresso.
        
        Parâmetros:
            value (int): Valor do progresso (0-100)
        """
        self.progress_bar.setValue(value)
    
    def set_temperature(self, value):
        """
        Define o valor da temperatura.
        
        Parâmetros:
            value (float): Valor da temperatura
        """
        self.temperature_label.setText(f"{value:.2f} °C")

# Classe para integrador do modelo
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
        try:
            # Conectar painel de parâmetros
            self.main_window.parameter_panel.parameters_changed.connect(self.on_parameters_changed)
            
            # Conectar controle de simulação
            self.main_window.simulation_control.time_changed.connect(self.on_time_changed)
            
            # Conectar sinais do integrador
            self.simulation_progress.connect(self.main_window.simulation_control.set_progress)
            self.simulation_completed.connect(self.main_window.simulation_control.simulation_completed)
            self.temperature_updated.connect(self.main_window.simulation_control.set_temperature)
        except Exception as e:
            print(f"Erro ao conectar sinais: {str(e)}")
            traceback.print_exc()
    
    def on_parameters_changed(self, params):
        """
        Manipula a alteração de parâmetros.
        
        Parâmetros:
            params (dict): Dicionário com os parâmetros
        """
        try:
            # Criar novo modelo térmico
            self.create_model(params)
            
            # Atualizar status
            self.main_window.statusBar().showMessage("Parâmetros aplicados", 3000)
        except Exception as e:
            error_msg = f"Erro ao aplicar parâmetros: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self.main_window, "Erro", error_msg)
            self.main_window.statusBar().showMessage(f"Erro: {str(e)}", 5000)
    
    def create_model(self, params):
        """
        Cria um novo modelo térmico com os parâmetros especificados.
        
        Parâmetros:
            params (dict): Dicionário com os parâmetros
        """
        try:
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
            
            # Adicionar pontos para histórico de temperatura
            self.add_history_points()
            
            # Limpar dados anteriores
            self.temperature_data = []
            self.time_points = []
            
            # Adicionar estado inicial
            self.temperature_data.append(self.model.temperature.copy())
            self.time_points.append(self.model.time)
            
            # Atualizar visualizações
            self.update_visualizations()
        except Exception as e:
            print(f"Erro ao criar modelo: {str(e)}")
            traceback.print_exc()
            raise
    
    def add_intrusion(self, geometry_params):
        """
        Adiciona uma intrusão ao modelo.
        
        Parâmetros:
            geometry_params (dict): Parâmetros de geometria
        """
        if not self.model:
            return
        
        try:
            # Extrair parâmetros
            geometry_type = geometry_params.get('geometry_type', 'Planar (Sill)')
            intrusion = geometry_params.get('intrusion', {})
            
            # Mapear tipo de geometria
            if geometry_type == "Planar (Sill)":
                geom_type = "planar"
            elif geometry_type == "Cilíndrica (Dique)":
                geom_type = "cylindrical"
            elif geometry_type == "Esférica (Plúton)":
                geom_type = "spherical"
            else:
                geom_type = "planar"
            
            # Criar máscara para intrusão
            mask = self.model.create_intrusion(geom_type, intrusion)
            
            # Definir temperatura da intrusão
            self.model.set_temperature(mask, self.model.magma_temperature)
        except Exception as e:
            print(f"Erro ao adicionar intrusão: {str(e)}")
            traceback.print_exc()
    
    def add_history_points(self):
        """Adiciona pontos para monitoramento de temperatura."""
        if not self.model:
            return
        
        try:
            # Centro do domínio
            cx = self.model.nx // 2
            cy = self.model.ny // 2
            cz = self.model.nz // 2
            
            # Adicionar pontos com verificação de limites
            self.model.add_history_point((cx, cy, cz))  # Centro
            
            # Verificar se cx + 10 está dentro dos limites
            if cx + 10 < self.model.nx:
                self.model.add_history_point((cx + 10, cy, cz))  # Próximo ao centro
            
            # Verificar se cx + 20 está dentro dos limites
            if cx + 20 < self.model.nx:
                self.model.add_history_point((cx + 20, cy, cz))  # Mais afastado
            
            # Verificar se cx + 50 está dentro dos limites
            if cx + 50 < self.model.nx:
                self.model.add_history_point((cx + 50, cy, cz))  # Distante
            else:
                # Adicionar um ponto alternativo se cx + 50 estiver fora dos limites
                self.model.add_history_point((self.model.nx - 1, cy, cz))  # Borda
        except Exception as e:
            print(f"Erro ao adicionar pontos de histórico: {str(e)}")
            traceback.print_exc()
    
    def on_time_changed(self, time_index):
        """
        Manipula a alteração do tempo na interface.
        
        Parâmetros:
            time_index (int): Índice do ponto de tempo
        """
        if not self.temperature_data or time_index >= len(self.temperature_data):
            return
        
        try:
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
        except Exception as e:
            print(f"Erro ao atualizar tempo: {str(e)}")
            traceback.print_exc()
    
    def start_simulation(self):
        """Inicia a simulação."""
        if not self.model or self.is_running:
            return
        
        try:
            # Obter parâmetros
            params = self.main_window.parameter_panel.parameters
            
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
        except Exception as e:
            error_msg = f"Erro ao iniciar simulação: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self.main_window, "Erro", error_msg)
            self.main_window.statusBar().showMessage(f"Erro: {str(e)}", 5000)
    
    def run_simulation(self, duration, save_interval):
        """
        Executa a simulação.
        
        Parâmetros:
            duration (float): Duração da simulação (s)
            save_interval (float): Intervalo de salvamento (s)
        """
        try:
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
        except Exception as e:
            print(f"Erro ao executar simulação: {str(e)}")
            traceback.print_exc()
            
            # Atualizar estado
            self.is_running = False
            
            # Mostrar mensagem de erro
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao executar simulação: {str(e)}")
    
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
        
        try:
            # Atualizar painel de visualização
            self.main_window.visualization_panel.set_data(
                self.temperature_data,
                self.time_points,
                self.model.temperature_history if self.model else None
            )
        except Exception as e:
            print(f"Erro ao atualizar visualizações: {str(e)}")
            traceback.print_exc()

# Classe para janela principal
class MainWindow(QMainWindow):
    """Janela principal do GeoTherm."""
    
    def __init__(self):
        """Inicializa a janela principal."""
        super().__init__()
        
        # Configurar janela
        self.setWindowTitle("GeoTherm - Modelamento de Fluxo Térmico")
        self.setGeometry(100, 100, 1200, 800)
        
        # Criar componentes
        self.setup_ui()
        
        # Criar integrador
        self.integrator = ModelIntegrator(self)
        
        # Configurar barra de status
        self.statusBar().showMessage("Pronto")
    
    def setup_ui(self):
        """Configura a interface do usuário."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Painel de parâmetros (esquerda)
        self.parameter_panel = ParameterPanel()
        main_splitter.addWidget(self.parameter_panel)
        
        # Painel direito
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_splitter.addWidget(right_panel)
        
        # Painel de visualização
        self.visualization_panel = VisualizationPanel()
        right_layout.addWidget(self.visualization_panel)
        
        # Controle de simulação
        self.simulation_control = SimulationControl()
        right_layout.addWidget(self.simulation_control)
        
        # Configurar proporção do splitter
        main_splitter.setSizes([300, 900])
        
        # Adicionar menu
        self.create_menus()
    
    def create_menus(self):
        """Cria os menus da aplicação."""
        # Menu Arquivo
        file_menu = self.menuBar().addMenu("Arquivo")
        
        # Ação Novo
        new_action = file_menu.addAction("Novo")
        new_action.triggered.connect(self.new_project)
        
        # Ação Abrir
        open_action = file_menu.addAction("Abrir")
        open_action.triggered.connect(self.open_project)
        
        # Ação Salvar
        save_action = file_menu.addAction("Salvar")
        save_action.triggered.connect(self.save_project)
        
        # Separador
        file_menu.addSeparator()
        
        # Ação Sair
        exit_action = file_menu.addAction("Sair")
        exit_action.triggered.connect(self.close)
        
        # Menu Ajuda
        help_menu = self.menuBar().addMenu("Ajuda")
        
        # Ação Sobre
        about_action = help_menu.addAction("Sobre")
        about_action.triggered.connect(self.show_about)
    
    def new_project(self):
        """Cria um novo projeto."""
        try:
            # Confirmar com o usuário
            reply = QMessageBox.question(self, "Novo Projeto", 
                                        "Deseja criar um novo projeto? Todas as alterações não salvas serão perdidas.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Redefinir parâmetros
                self.parameter_panel.reset_parameters()
                
                # Aplicar parâmetros
                self.parameter_panel.apply_parameters()
                
                # Atualizar status
                self.statusBar().showMessage("Novo projeto criado", 3000)
        except Exception as e:
            error_msg = f"Erro ao criar novo projeto: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erro", error_msg)
            self.statusBar().showMessage(f"Erro: {str(e)}", 5000)
    
    def open_project(self):
        """Abre um projeto existente."""
        try:
            # Abrir diálogo de arquivo
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Abrir Projeto", "", "Arquivos GeoTherm (*.geo);;Todos os Arquivos (*)")
            
            if file_path:
                # TODO: Implementar carregamento de projeto
                
                # Atualizar status
                self.statusBar().showMessage(f"Projeto aberto: {file_path}", 3000)
        except Exception as e:
            error_msg = f"Erro ao abrir projeto: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erro", error_msg)
            self.statusBar().showMessage(f"Erro: {str(e)}", 5000)
    
    def save_project(self):
        """Salva o projeto atual."""
        try:
            # Abrir diálogo de arquivo
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Salvar Projeto", "", "Arquivos GeoTherm (*.geo);;Todos os Arquivos (*)")
            
            if file_path:
                # TODO: Implementar salvamento de projeto
                
                # Atualizar status
                self.statusBar().showMessage(f"Projeto salvo: {file_path}", 3000)
        except Exception as e:
            error_msg = f"Erro ao salvar projeto: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erro", error_msg)
            self.statusBar().showMessage(f"Erro: {str(e)}", 5000)
    
    def show_about(self):
        """Mostra informações sobre o programa."""
        about_text = """
        <h1>GeoTherm</h1>
        <p>Programa para Modelamento de Fluxo Térmico</p>
        <p>Versão 1.0</p>
        <p>Desenvolvido como suplemento para publicação científica.</p>
        """
        
        QMessageBox.about(self, "Sobre o GeoTherm", about_text)
    
    def start_simulation(self):
        """Inicia a simulação."""
        self.integrator.start_simulation()
    
    def pause_simulation(self):
        """Pausa ou retoma a simulação."""
        self.integrator.pause_simulation()
    
    def stop_simulation(self):
        """Para a simulação."""
        self.integrator.stop_simulation()

def main():
    """Função principal que inicia o programa GeoTherm."""
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    app.setApplicationName("GeoTherm")
    app.setOrganizationName("GeoTherm")
    
    # Definir estilo da aplicação
    app.setStyle("Fusion")
    
    # Mostrar tela de carregamento
    splash = show_splash_screen()
    
    # Simular carregamento (em uma aplicação real, isso seria o carregamento real)
    for i in range(1, 101):
        time.sleep(0.03)  # Simular trabalho
        app.processEvents()  # Manter a interface responsiva
    
    # Criar e mostrar a janela principal
    main_window = MainWindow()
    
    # Criar integrador
    integrator = ModelIntegrator(main_window)
    
    # Fechar a tela de carregamento e mostrar a janela principal
    splash.finish_splash(main_window)
    main_window.show()
    
    # Executar loop de eventos
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
