"""
GeoTherm - Controle de Simulação

Este módulo implementa o painel de controle de simulação do programa GeoTherm.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSlider, QPushButton, QProgressBar, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class SimulationControl(QWidget):
    """
    Painel de controle de simulação para o GeoTherm.
    
    Permite controlar a execução e visualização temporal da simulação.
    """
    
    # Sinal emitido quando o tempo é alterado
    time_changed = pyqtSignal(int)
    
    def __init__(self):
        """Inicializa o controle de simulação."""
        super().__init__()
        
        # Estado da simulação
        self.is_running = False
        self.is_paused = False
        self.is_completed = False
        self.time_points = []
        
        # Criar layout principal
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Criar controles de tempo
        self.create_time_controls()
        
        # Criar informações de simulação
        self.create_info_panel()
        
        # Criar barra de progresso
        self.create_progress_bar()
    
    def create_time_controls(self):
        """Cria os controles de tempo."""
        # Grupo de controles de tempo
        time_group = QGroupBox("Controle de Tempo")
        time_layout = QVBoxLayout()
        time_group.setLayout(time_layout)
        
        # Slider de tempo
        slider_layout = QHBoxLayout()
        time_layout.addLayout(slider_layout)
        
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)
        self.time_slider.setEnabled(False)
        
        self.current_time_label = QLabel("00:00:00")
        self.total_time_label = QLabel("00:00:00")
        
        slider_layout.addWidget(self.current_time_label)
        slider_layout.addWidget(self.time_slider)
        slider_layout.addWidget(self.total_time_label)
        
        # Botões de controle
        button_layout = QHBoxLayout()
        time_layout.addLayout(button_layout)
        
        self.start_button = QPushButton("Início")
        self.prev_button = QPushButton("Anterior")
        self.play_button = QPushButton("Reproduzir")
        self.next_button = QPushButton("Próximo")
        self.end_button = QPushButton("Fim")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.end_button)
        
        # Desabilitar botões inicialmente
        self.start_button.setEnabled(False)
        self.prev_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.end_button.setEnabled(False)
        
        # Adicionar grupo ao layout principal
        self.main_layout.addWidget(time_group)
        
        # Conectar sinais
        self.time_slider.valueChanged.connect(self.on_time_slider_changed)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.prev_button.clicked.connect(self.on_prev_button_clicked)
        self.play_button.clicked.connect(self.on_play_button_clicked)
        self.next_button.clicked.connect(self.on_next_button_clicked)
        self.end_button.clicked.connect(self.on_end_button_clicked)
    
    def create_info_panel(self):
        """Cria o painel de informações."""
        # Grupo de informações
        info_group = QGroupBox("Informações")
        info_layout = QHBoxLayout()
        info_group.setLayout(info_layout)
        
        # Temperatura
        temp_layout = QVBoxLayout()
        info_layout.addLayout(temp_layout)
        
        temp_layout.addWidget(QLabel("Temperatura:"))
        self.temperature_label = QLabel("0.0 °C")
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        temp_layout.addWidget(self.temperature_label)
        
        # Tempo de simulação
        sim_time_layout = QVBoxLayout()
        info_layout.addLayout(sim_time_layout)
        
        sim_time_layout.addWidget(QLabel("Tempo de Simulação:"))
        self.sim_time_label = QLabel("0.0 s")
        self.sim_time_label.setAlignment(Qt.AlignCenter)
        self.sim_time_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        sim_time_layout.addWidget(self.sim_time_label)
        
        # Tempo real
        real_time_layout = QVBoxLayout()
        info_layout.addLayout(real_time_layout)
        
        real_time_layout.addWidget(QLabel("Tempo Real:"))
        self.real_time_label = QLabel("00:00:00")
        self.real_time_label.setAlignment(Qt.AlignCenter)
        self.real_time_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        real_time_layout.addWidget(self.real_time_label)
        
        # Adicionar grupo ao layout principal
        self.main_layout.addWidget(info_group)
    
    def create_progress_bar(self):
        """Cria a barra de progresso."""
        # Grupo de progresso
        progress_group = QGroupBox("Progresso")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Pronto")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        # Adicionar grupo ao layout principal
        self.main_layout.addWidget(progress_group)
    
    def on_time_slider_changed(self, value):
        """
        Manipula a alteração do slider de tempo.
        
        Parâmetros:
            value (int): Valor do slider
        """
        if not self.time_points:
            return
        
        # Calcular índice de tempo
        time_index = min(value, len(self.time_points) - 1)
        
        # Atualizar label de tempo atual
        self.current_time_label.setText(self.format_time(self.time_points[time_index]))
        
        # Emitir sinal de alteração de tempo
        self.time_changed.emit(time_index)
    
    def on_start_button_clicked(self):
        """Manipula o clique no botão de início."""
        if not self.time_points:
            return
        
        # Ir para o primeiro ponto de tempo
        self.time_slider.setValue(0)
    
    def on_prev_button_clicked(self):
        """Manipula o clique no botão de anterior."""
        if not self.time_points:
            return
        
        # Ir para o ponto de tempo anterior
        current = self.time_slider.value()
        if current > 0:
            self.time_slider.setValue(current - 1)
    
    def on_play_button_clicked(self):
        """Manipula o clique no botão de reprodução."""
        if not self.time_points:
            return
        
        # Alternar entre reproduzir e pausar
        if self.play_button.text() == "Reproduzir":
            self.play_button.setText("Pausar")
            # TODO: Implementar reprodução automática
        else:
            self.play_button.setText("Reproduzir")
            # TODO: Implementar pausa
    
    def on_next_button_clicked(self):
        """Manipula o clique no botão de próximo."""
        if not self.time_points:
            return
        
        # Ir para o próximo ponto de tempo
        current = self.time_slider.value()
        if current < len(self.time_points) - 1:
            self.time_slider.setValue(current + 1)
    
    def on_end_button_clicked(self):
        """Manipula o clique no botão de fim."""
        if not self.time_points:
            return
        
        # Ir para o último ponto de tempo
        self.time_slider.setValue(len(self.time_points) - 1)
    
    def simulation_started(self):
        """Atualiza a interface quando a simulação é iniciada."""
        # Atualizar estado
        self.is_running = True
        self.is_paused = False
        self.is_completed = False
        
        # Atualizar controles
        self.time_slider.setEnabled(False)
        self.start_button.setEnabled(False)
        self.prev_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.end_button.setEnabled(False)
        
        # Atualizar status
        self.status_label.setText("Simulação em andamento...")
    
    def simulation_paused(self):
        """Atualiza a interface quando a simulação é pausada."""
        # Atualizar estado
        self.is_paused = not self.is_paused
        
        # Atualizar status
        if self.is_paused:
            self.status_label.setText("Simulação pausada")
        else:
            self.status_label.setText("Simulação em andamento...")
    
    def simulation_stopped(self):
        """Atualiza a interface quando a simulação é parada."""
        # Atualizar estado
        self.is_running = False
        self.is_paused = False
        
        # Atualizar status
        self.status_label.setText("Simulação parada")
    
    def simulation_completed(self, time_points):
        """
        Atualiza a interface quando a simulação é concluída.
        
        Parâmetros:
            time_points (list): Lista de pontos de tempo
        """
        # Atualizar estado
        self.is_running = False
        self.is_paused = False
        self.is_completed = True
        
        # Armazenar pontos de tempo
        self.set_time_points(time_points)
        
        # Atualizar status
        self.status_label.setText("Simulação concluída")
        
        # Atualizar progresso
        self.progress_bar.setValue(100)
    
    def set_time_points(self, time_points):
        """
        Define os pontos de tempo disponíveis.
        
        Parâmetros:
            time_points (list): Lista de pontos de tempo
        """
        self.time_points = time_points
        
        if not time_points:
            return
        
        # Configurar slider
        self.time_slider.setRange(0, len(time_points) - 1)
        self.time_slider.setValue(len(time_points) - 1)
        self.time_slider.setEnabled(True)
        
        # Configurar labels de tempo
        self.current_time_label.setText(self.format_time(time_points[-1]))
        self.total_time_label.setText(self.format_time(time_points[-1]))
        
        # Habilitar botões
        self.start_button.setEnabled(True)
        self.prev_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.end_button.setEnabled(True)
    
    def set_progress(self, progress):
        """
        Define o progresso da simulação.
        
        Parâmetros:
            progress (int): Valor do progresso (0-100)
        """
        self.progress_bar.setValue(progress)
    
    def set_temperature(self, temperature):
        """
        Define a temperatura atual.
        
        Parâmetros:
            temperature (float): Valor da temperatura
        """
        self.temperature_label.setText(f"{temperature:.1f} °C")
    
    def set_real_time(self, seconds):
        """
        Define o tempo real decorrido.
        
        Parâmetros:
            seconds (float): Tempo em segundos
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        self.real_time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def format_time(self, seconds):
        """
        Formata um valor de tempo em notação científica.
        
        Parâmetros:
            seconds (float): Tempo em segundos
        
        Retorna:
            str: Tempo formatado
        """
        if seconds < 60:
            return f"{seconds:.1f} s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} min"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} h"
        else:
            days = seconds / 86400
            return f"{days:.1f} dias"
