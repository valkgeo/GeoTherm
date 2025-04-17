"""
GeoTherm - Painel de Parâmetros

Este módulo implementa o painel de configuração de parâmetros do programa GeoTherm.
"""

from PyQt5.QtWidgets import (QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
                            QPushButton, QGroupBox, QRadioButton, QSlider, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal

class ParameterPanel(QWidget):
    """
    Painel de configuração de parâmetros para o GeoTherm.
    
    Permite ao usuário definir todos os parâmetros da simulação térmica.
    """
    
    # Sinal emitido quando os parâmetros são alterados
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self):
        """Inicializa o painel de parâmetros."""
        super().__init__()
        
        # Criar layout principal
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Criar widget de abas
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Criar abas
        self.create_geometry_tab()
        self.create_thermal_tab()
        self.create_simulation_tab()
        
        # Adicionar botões
        self.create_buttons()
        
        # Configurar valores padrão
        self.reset_parameters()
        
        # Conectar sinais
        self.connect_signals()
    
    def create_geometry_tab(self):
        """Cria a aba de geometria."""
        # Criar widget e layout
        geometry_widget = QWidget()
        geometry_layout = QVBoxLayout()
        geometry_widget.setLayout(geometry_layout)
        
        # Grupo de tipo de geometria
        geometry_type_group = QGroupBox("Tipo de Geometria")
        geometry_type_layout = QVBoxLayout()
        geometry_type_group.setLayout(geometry_type_layout)
        
        # Combobox para tipo de geometria
        self.geometry_type_combo = QComboBox()
        self.geometry_type_combo.addItems([
            "Planar (Sill)",
            "Cilíndrica (Dique)",
            "Esférica (Plúton)",
            "Complexa"
        ])
        geometry_type_layout.addWidget(self.geometry_type_combo)
        
        # Adicionar grupo ao layout
        geometry_layout.addWidget(geometry_type_group)
        
        # Grupo de dimensões da intrusão
        intrusion_group = QGroupBox("Dimensões da Intrusão")
        intrusion_layout = QFormLayout()
        intrusion_group.setLayout(intrusion_layout)
        
        # Controles para dimensões da intrusão
        self.thickness_label = QLabel("Espessura (m):")
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(1, 1000)
        self.thickness_spin.setValue(50)
        self.thickness_spin.setSingleStep(10)
        intrusion_layout.addRow(self.thickness_label, self.thickness_spin)
        
        self.width_label = QLabel("Largura (m):")
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(500)
        self.width_spin.setSingleStep(100)
        intrusion_layout.addRow(self.width_label, self.width_spin)
        
        self.height_label = QLabel("Comprimento (m):")
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(500)
        self.height_spin.setSingleStep(100)
        intrusion_layout.addRow(self.height_label, self.height_spin)
        
        self.radius_label = QLabel("Raio (m):")
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(1, 5000)
        self.radius_spin.setValue(100)
        self.radius_spin.setSingleStep(50)
        intrusion_layout.addRow(self.radius_label, self.radius_spin)
        
        # Adicionar grupo ao layout
        geometry_layout.addWidget(intrusion_group)
        
        # Grupo de dimensões do domínio
        domain_group = QGroupBox("Dimensões do Domínio")
        domain_layout = QFormLayout()
        domain_group.setLayout(domain_layout)
        
        # Controles para dimensões do domínio
        self.domain_x_label = QLabel("Nx (células):")
        self.domain_x_spin = QSpinBox()
        self.domain_x_spin.setRange(10, 500)
        self.domain_x_spin.setValue(100)
        self.domain_x_spin.setSingleStep(10)
        domain_layout.addRow(self.domain_x_label, self.domain_x_spin)
        
        self.domain_y_label = QLabel("Ny (células):")
        self.domain_y_spin = QSpinBox()
        self.domain_y_spin.setRange(10, 500)
        self.domain_y_spin.setValue(100)
        self.domain_y_spin.setSingleStep(10)
        domain_layout.addRow(self.domain_y_label, self.domain_y_spin)
        
        self.domain_z_label = QLabel("Nz (células):")
        self.domain_z_spin = QSpinBox()
        self.domain_z_spin.setRange(10, 500)
        self.domain_z_spin.setValue(100)
        self.domain_z_spin.setSingleStep(10)
        domain_layout.addRow(self.domain_z_label, self.domain_z_spin)
        
        self.cell_size_label = QLabel("Tamanho da célula (m):")
        self.cell_size_spin = QDoubleSpinBox()
        self.cell_size_spin.setRange(1, 100)
        self.cell_size_spin.setValue(10)
        self.cell_size_spin.setSingleStep(1)
        domain_layout.addRow(self.cell_size_label, self.cell_size_spin)
        
        # Adicionar grupo ao layout
        geometry_layout.addWidget(domain_group)
        
        # Adicionar espaçador
        geometry_layout.addStretch()
        
        # Adicionar aba ao widget de abas
        self.tab_widget.addTab(geometry_widget, "Geometria")
    
    def create_thermal_tab(self):
        """Cria a aba de propriedades térmicas."""
        # Criar widget e layout
        thermal_widget = QWidget()
        thermal_layout = QVBoxLayout()
        thermal_widget.setLayout(thermal_layout)
        
        # Grupo de temperaturas
        temp_group = QGroupBox("Temperaturas")
        temp_layout = QFormLayout()
        temp_group.setLayout(temp_layout)
        
        # Controles para temperaturas
        self.magma_temp_label = QLabel("Temperatura do Magma (°C):")
        self.magma_temp_spin = QDoubleSpinBox()
        self.magma_temp_spin.setRange(500, 2000)
        self.magma_temp_spin.setValue(1200)
        self.magma_temp_spin.setSingleStep(50)
        temp_layout.addRow(self.magma_temp_label, self.magma_temp_spin)
        
        self.background_temp_label = QLabel("Temperatura do Encaixante (°C):")
        self.background_temp_spin = QDoubleSpinBox()
        self.background_temp_spin.setRange(0, 500)
        self.background_temp_spin.setValue(20)
        self.background_temp_spin.setSingleStep(10)
        temp_layout.addRow(self.background_temp_label, self.background_temp_spin)
        
        # Adicionar grupo ao layout
        thermal_layout.addWidget(temp_group)
        
        # Grupo de propriedades térmicas
        properties_group = QGroupBox("Propriedades Térmicas")
        properties_layout = QFormLayout()
        properties_group.setLayout(properties_layout)
        
        # Controles para propriedades térmicas
        self.diffusivity_label = QLabel("Difusividade Térmica (m²/s):")
        self.diffusivity_spin = QDoubleSpinBox()
        self.diffusivity_spin.setRange(1e-8, 1e-4)
        self.diffusivity_spin.setValue(1e-6)
        self.diffusivity_spin.setDecimals(8)
        self.diffusivity_spin.setSingleStep(1e-7)
        properties_layout.addRow(self.diffusivity_label, self.diffusivity_spin)
        
        self.conductivity_label = QLabel("Condutividade Térmica (W/(m·K)):")
        self.conductivity_spin = QDoubleSpinBox()
        self.conductivity_spin.setRange(0.1, 10)
        self.conductivity_spin.setValue(2.5)
        self.conductivity_spin.setSingleStep(0.1)
        properties_layout.addRow(self.conductivity_label, self.conductivity_spin)
        
        self.specific_heat_label = QLabel("Calor Específico (J/(kg·K)):")
        self.specific_heat_spin = QDoubleSpinBox()
        self.specific_heat_spin.setRange(500, 2000)
        self.specific_heat_spin.setValue(1000)
        self.specific_heat_spin.setSingleStep(100)
        properties_layout.addRow(self.specific_heat_label, self.specific_heat_spin)
        
        self.density_label = QLabel("Densidade (kg/m³):")
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(2000, 3500)
        self.density_spin.setValue(2700)
        self.density_spin.setSingleStep(100)
        properties_layout.addRow(self.density_label, self.density_spin)
        
        # Adicionar grupo ao layout
        thermal_layout.addWidget(properties_group)
        
        # Grupo de calor latente
        latent_group = QGroupBox("Calor Latente")
        latent_layout = QVBoxLayout()
        latent_group.setLayout(latent_layout)
        
        # Checkbox para ativar calor latente
        self.latent_heat_check = QCheckBox("Considerar calor latente durante cristalização")
        latent_layout.addWidget(self.latent_heat_check)
        
        # Layout para controles de calor latente
        latent_form = QFormLayout()
        latent_layout.addLayout(latent_form)
        
        # Controles para calor latente
        self.solidus_label = QLabel("Temperatura Solidus (°C):")
        self.solidus_spin = QDoubleSpinBox()
        self.solidus_spin.setRange(500, 1500)
        self.solidus_spin.setValue(700)
        self.solidus_spin.setSingleStep(50)
        latent_form.addRow(self.solidus_label, self.solidus_spin)
        
        self.liquidus_label = QLabel("Temperatura Liquidus (°C):")
        self.liquidus_spin = QDoubleSpinBox()
        self.liquidus_spin.setRange(500, 1500)
        self.liquidus_spin.setValue(1200)
        self.liquidus_spin.setSingleStep(50)
        latent_form.addRow(self.liquidus_label, self.liquidus_spin)
        
        self.latent_heat_label = QLabel("Calor Latente (J/kg):")
        self.latent_heat_spin = QDoubleSpinBox()
        self.latent_heat_spin.setRange(100000, 1000000)
        self.latent_heat_spin.setValue(400000)
        self.latent_heat_spin.setSingleStep(50000)
        latent_form.addRow(self.latent_heat_label, self.latent_heat_spin)
        
        # Adicionar grupo ao layout
        thermal_layout.addWidget(latent_group)
        
        # Adicionar espaçador
        thermal_layout.addStretch()
        
        # Adicionar aba ao widget de abas
        self.tab_widget.addTab(thermal_widget, "Propriedades Térmicas")
    
    def create_simulation_tab(self):
        """Cria a aba de simulação."""
        # Criar widget e layout
        simulation_widget = QWidget()
        simulation_layout = QVBoxLayout()
        simulation_widget.setLayout(simulation_layout)
        
        # Grupo de tempo
        time_group = QGroupBox("Configurações de Tempo")
        time_layout = QFormLayout()
        time_group.setLayout(time_layout)
        
        # Controles para tempo - CORRIGIDO: Criar todos os objetos primeiro
        self.duration_label = QLabel("Duração da Simulação (s):")
        self.duration_spin = QDoubleSpinBox()
        
        self.save_interval_label = QLabel("Intervalo de Salvamento (s):")
        self.save_interval_spin = QDoubleSpinBox()
        
        # Configurar os objetos depois de criá-los
        self.duration_spin.setRange(1, 1e10)
        self.duration_spin.setValue(1e6)
        self.duration_spin.setDecimals(1)
        self.duration_spin.setSingleStep(1e5)
        # Compatibilidade com diferentes versões do PyQt5
        try:
            self.duration_spin.setNotation(QDoubleSpinBox.ScientificNotation)
        except AttributeError:
            # Alternativa para versões mais antigas do PyQt5
            pass
        
        self.save_interval_spin.setRange(1, 1e9)
        self.save_interval_spin.setValue(1e5)
        self.save_interval_spin.setDecimals(1)
        self.save_interval_spin.setSingleStep(1e4)
        # Compatibilidade com diferentes versões do PyQt5
        try:
            self.save_interval_spin.setNotation(QDoubleSpinBox.ScientificNotation)
        except AttributeError:
            # Alternativa para versões mais antigas do PyQt5
            pass
        
        # Adicionar ao layout
        time_layout.addRow(self.duration_label, self.duration_spin)
        time_layout.addRow(self.save_interval_label, self.save_interval_spin)
        
        # Adicionar grupo ao layout
        simulation_layout.addWidget(time_group)
        
        # Grupo de módulos
        modules_group = QGroupBox("Módulos Ativos")
        modules_layout = QVBoxLayout()
        modules_group.setLayout(modules_layout)
        
        # Checkboxes para módulos
        self.conduction_check = QCheckBox("Condução Térmica")
        self.conduction_check.setChecked(True)
        self.conduction_check.setEnabled(False)  # Sempre ativo
        modules_layout.addWidget(self.conduction_check)
        
        self.convection_check = QCheckBox("Convecção Hidrotermal")
        modules_layout.addWidget(self.convection_check)
        
        self.latent_heat_module_check = QCheckBox("Calor Latente")
        modules_layout.addWidget(self.latent_heat_module_check)
        
        # Adicionar grupo ao layout
        simulation_layout.addWidget(modules_group)
        
        # Grupo de convecção (inicialmente oculto)
        self.convection_group = QGroupBox("Configurações de Convecção")
        convection_layout = QVBoxLayout()
        self.convection_group.setLayout(convection_layout)
        
        # Tipo de fluxo
        flow_layout = QFormLayout()
        convection_layout.addLayout(flow_layout)
        
        self.flow_type_label = QLabel("Tipo de Fluxo:")
        self.flow_type_combo = QComboBox()
        self.flow_type_combo.addItems([
            "Célula de Convecção",
            "Fluxo Ascendente",
            "Fluxo Lateral"
        ])
        flow_layout.addRow(self.flow_type_label, self.flow_type_combo)
        
        self.max_velocity_label = QLabel("Velocidade Máxima (m/s):")
        self.max_velocity_spin = QDoubleSpinBox()
        self.max_velocity_spin.setRange(1e-10, 1e-3)
        self.max_velocity_spin.setValue(1e-6)
        self.max_velocity_spin.setDecimals(10)
        self.max_velocity_spin.setSingleStep(1e-7)
        flow_layout.addRow(self.max_velocity_label, self.max_velocity_spin)
        
        # Adicionar grupo ao layout
        simulation_layout.addWidget(self.convection_group)
        self.convection_group.setVisible(False)
        
        # Adicionar espaçador
        simulation_layout.addStretch()
        
        # Adicionar aba ao widget de abas
        self.tab_widget.addTab(simulation_widget, "Simulação")
    
    def create_buttons(self):
        """Cria os botões do painel."""
        # Layout para botões
        button_layout = QHBoxLayout()
        self.main_layout.addLayout(button_layout)
        
        # Botão para aplicar parâmetros
        self.apply_button = QPushButton("Aplicar Parâmetros")
        button_layout.addWidget(self.apply_button)
        
        # Botão para redefinir parâmetros
        self.reset_button = QPushButton("Redefinir")
        button_layout.addWidget(self.reset_button)
    
    def connect_signals(self):
        """Conecta os sinais dos controles."""
        # Conectar botões
        self.apply_button.clicked.connect(self.apply_parameters)
        self.reset_button.clicked.connect(self.reset_parameters)
        
        # Conectar tipo de geometria
        self.geometry_type_combo.currentIndexChanged.connect(self.update_geometry_controls)
        
        # Conectar checkbox de calor latente
        self.latent_heat_check.toggled.connect(self.update_latent_heat_controls)
        self.latent_heat_module_check.toggled.connect(self.latent_heat_check.setChecked)
        self.latent_heat_check.toggled.connect(self.latent_heat_module_check.setChecked)
        
        # Conectar checkbox de convecção
        self.convection_check.toggled.connect(self.convection_group.setVisible)
    
    def update_geometry_controls(self):
        """Atualiza os controles de geometria com base no tipo selecionado."""
        geometry_type = self.geometry_type_combo.currentText()
        
        # Ocultar todos os controles específicos
        self.thickness_label.setVisible(False)
        self.thickness_spin.setVisible(False)
        self.width_label.setVisible(False)
        self.width_spin.setVisible(False)
        self.height_label.setVisible(False)
        self.height_spin.setVisible(False)
        self.radius_label.setVisible(False)
        self.radius_spin.setVisible(False)
        
        # Mostrar controles específicos para o tipo selecionado
        if geometry_type == "Planar (Sill)":
            self.thickness_label.setVisible(True)
            self.thickness_spin.setVisible(True)
            self.width_label.setVisible(True)
            self.width_spin.setVisible(True)
            self.height_label.setVisible(True)
            self.height_spin.setVisible(True)
        elif geometry_type == "Cilíndrica (Dique)":
            self.radius_label.setVisible(True)
            self.radius_spin.setVisible(True)
            self.height_label.setVisible(True)
            self.height_spin.setVisible(True)
        elif geometry_type == "Esférica (Plúton)":
            self.radius_label.setVisible(True)
            self.radius_spin.setVisible(True)
        else:  # Complexa
            self.thickness_label.setVisible(True)
            self.thickness_spin.setVisible(True)
            self.width_label.setVisible(True)
            self.width_spin.setVisible(True)
            self.height_label.setVisible(True)
            self.height_spin.setVisible(True)
            self.radius_label.setVisible(True)
            self.radius_spin.setVisible(True)
    
    def update_latent_heat_controls(self, checked):
        """Atualiza os controles de calor latente com base no estado do checkbox."""
        self.solidus_label.setEnabled(checked)
        self.solidus_spin.setEnabled(checked)
        self.liquidus_label.setEnabled(checked)
        self.liquidus_spin.setEnabled(checked)
        self.latent_heat_label.setEnabled(checked)
        self.latent_heat_spin.setEnabled(checked)
    
    def apply_parameters(self):
        """Aplica os parâmetros configurados."""
        # Obter parâmetros
        params = self.get_parameters()
        
        # Emitir sinal
        self.parameters_changed.emit(params)
    
    def get_parameters(self):
        """
        Obtém os parâmetros configurados.
        
        Retorna:
            dict: Dicionário com os parâmetros
        """
        # Criar dicionário de parâmetros
        params = {
            'geometry': {
                'geometry_type': self.geometry_type_combo.currentText(),
                'domain': {
                    'nx': self.domain_x_spin.value(),
                    'ny': self.domain_y_spin.value(),
                    'nz': self.domain_z_spin.value(),
                    'cell_size': self.cell_size_spin.value()
                },
                'intrusion': {}
            },
            'thermal': {
                'temperatures': {
                    'magma': self.magma_temp_spin.value(),
                    'background': self.background_temp_spin.value()
                },
                'properties': {
                    'diffusivity': self.diffusivity_spin.value(),
                    'conductivity': self.conductivity_spin.value(),
                    'specific_heat': self.specific_heat_spin.value(),
                    'density': self.density_spin.value()
                },
                'latent_heat': {
                    'use_latent_heat': self.latent_heat_check.isChecked(),
                    'solidus': self.solidus_spin.value(),
                    'liquidus': self.liquidus_spin.value(),
                    'latent_heat': self.latent_heat_spin.value()
                }
            },
            'simulation': {
                'time': {
                    'duration': self.duration_spin.value(),
                    'save_interval': self.save_interval_spin.value()
                },
                'modules': {
                    'conduction': self.conduction_check.isChecked(),
                    'convection': self.convection_check.isChecked(),
                    'latent_heat': self.latent_heat_module_check.isChecked()
                }
            }
        }
        
        # Adicionar parâmetros específicos de geometria
        geometry_type = self.geometry_type_combo.currentText()
        
        if geometry_type == "Planar (Sill)":
            params['geometry']['intrusion'].update({
                'thickness': self.thickness_spin.value(),
                'width': self.width_spin.value(),
                'height': self.height_spin.value()
            })
        elif geometry_type == "Cilíndrica (Dique)":
            params['geometry']['intrusion'].update({
                'radius': self.radius_spin.value(),
                'height': self.height_spin.value()
            })
        elif geometry_type == "Esférica (Plúton)":
            params['geometry']['intrusion'].update({
                'radius': self.radius_spin.value()
            })
        else:  # Complexa
            params['geometry']['intrusion'].update({
                'thickness': self.thickness_spin.value(),
                'width': self.width_spin.value(),
                'height': self.height_spin.value(),
                'radius': self.radius_spin.value()
            })
        
        # Adicionar parâmetros de convecção se ativada
        if self.convection_check.isChecked():
            params['simulation']['convection'] = {
                'flow_type': self.flow_type_combo.currentText(),
                'max_velocity': self.max_velocity_spin.value()
            }
        
        return params
    
    def set_parameters(self, params):
        """
        Define os parâmetros a partir de um dicionário.
        
        Parâmetros:
            params (dict): Dicionário com os parâmetros
        """
        # Verificar se o dicionário é válido
        if not params:
            return
        
        # Definir parâmetros de geometria
        if 'geometry' in params:
            geometry = params['geometry']
            
            if 'geometry_type' in geometry:
                index = self.geometry_type_combo.findText(geometry['geometry_type'])
                if index >= 0:
                    self.geometry_type_combo.setCurrentIndex(index)
            
            if 'domain' in geometry:
                domain = geometry['domain']
                if 'nx' in domain:
                    self.domain_x_spin.setValue(domain['nx'])
                if 'ny' in domain:
                    self.domain_y_spin.setValue(domain['ny'])
                if 'nz' in domain:
                    self.domain_z_spin.setValue(domain['nz'])
                if 'cell_size' in domain:
                    self.cell_size_spin.setValue(domain['cell_size'])
            
            if 'intrusion' in geometry:
                intrusion = geometry['intrusion']
                if 'thickness' in intrusion:
                    self.thickness_spin.setValue(intrusion['thickness'])
                if 'width' in intrusion:
                    self.width_spin.setValue(intrusion['width'])
                if 'height' in intrusion:
                    self.height_spin.setValue(intrusion['height'])
                if 'radius' in intrusion:
                    self.radius_spin.setValue(intrusion['radius'])
        
        # Definir parâmetros térmicos
        if 'thermal' in params:
            thermal = params['thermal']
            
            if 'temperatures' in thermal:
                temperatures = thermal['temperatures']
                if 'magma' in temperatures:
                    self.magma_temp_spin.setValue(temperatures['magma'])
                if 'background' in temperatures:
                    self.background_temp_spin.setValue(temperatures['background'])
            
            if 'properties' in thermal:
                properties = thermal['properties']
                if 'diffusivity' in properties:
                    self.diffusivity_spin.setValue(properties['diffusivity'])
                if 'conductivity' in properties:
                    self.conductivity_spin.setValue(properties['conductivity'])
                if 'specific_heat' in properties:
                    self.specific_heat_spin.setValue(properties['specific_heat'])
                if 'density' in properties:
                    self.density_spin.setValue(properties['density'])
            
            if 'latent_heat' in thermal:
                latent_heat = thermal['latent_heat']
                if 'use_latent_heat' in latent_heat:
                    self.latent_heat_check.setChecked(latent_heat['use_latent_heat'])
                if 'solidus' in latent_heat:
                    self.solidus_spin.setValue(latent_heat['solidus'])
                if 'liquidus' in latent_heat:
                    self.liquidus_spin.setValue(latent_heat['liquidus'])
                if 'latent_heat' in latent_heat:
                    self.latent_heat_spin.setValue(latent_heat['latent_heat'])
        
        # Definir parâmetros de simulação
        if 'simulation' in params:
            simulation = params['simulation']
            
            if 'time' in simulation:
                time = simulation['time']
                if 'duration' in time:
                    self.duration_spin.setValue(time['duration'])
                if 'save_interval' in time:
                    self.save_interval_spin.setValue(time['save_interval'])
            
            if 'modules' in simulation:
                modules = simulation['modules']
                if 'conduction' in modules:
                    self.conduction_check.setChecked(modules['conduction'])
                if 'convection' in modules:
                    self.convection_check.setChecked(modules['convection'])
                if 'latent_heat' in modules:
                    self.latent_heat_module_check.setChecked(modules['latent_heat'])
            
            if 'convection' in simulation and self.convection_check.isChecked():
                convection = simulation['convection']
                if 'flow_type' in convection:
                    index = self.flow_type_combo.findText(convection['flow_type'])
                    if index >= 0:
                        self.flow_type_combo.setCurrentIndex(index)
                if 'max_velocity' in convection:
                    self.max_velocity_spin.setValue(convection['max_velocity'])
    
    def reset_parameters(self):
        """Redefine os parâmetros para valores padrão."""
        # Geometria
        self.geometry_type_combo.setCurrentIndex(0)
        self.domain_x_spin.setValue(100)
        self.domain_y_spin.setValue(100)
        self.domain_z_spin.setValue(100)
        self.cell_size_spin.setValue(10)
        self.thickness_spin.setValue(50)
        self.width_spin.setValue(500)
        self.height_spin.setValue(500)
        self.radius_spin.setValue(100)
        
        # Propriedades térmicas
        self.magma_temp_spin.setValue(1200)
        self.background_temp_spin.setValue(20)
        self.diffusivity_spin.setValue(1e-6)
        self.conductivity_spin.setValue(2.5)
        self.specific_heat_spin.setValue(1000)
        self.density_spin.setValue(2700)
        self.latent_heat_check.setChecked(False)
        self.solidus_spin.setValue(700)
        self.liquidus_spin.setValue(1200)
        self.latent_heat_spin.setValue(400000)
        
        # Simulação
        self.duration_spin.setValue(1e6)
        self.save_interval_spin.setValue(1e5)
        self.conduction_check.setChecked(True)
        self.convection_check.setChecked(False)
        self.latent_heat_module_check.setChecked(False)
        self.flow_type_combo.setCurrentIndex(0)
        self.max_velocity_spin.setValue(1e-6)
        
        # Atualizar controles
        self.update_geometry_controls()
        self.update_latent_heat_controls(False)
