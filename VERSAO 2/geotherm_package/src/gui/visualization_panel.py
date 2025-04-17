"""
GeoTherm - Painel de Visualização

Este módulo implementa o painel de visualização de resultados do programa GeoTherm.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QLabel, QComboBox, QSlider, QPushButton, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal

class MplCanvas(FigureCanvas):
    """Canvas para visualizações Matplotlib."""
    
    def __init__(self, width=5, height=4, dpi=100):
        """
        Inicializa o canvas.
        
        Parâmetros:
            width (float): Largura da figura em polegadas
            height (float): Altura da figura em polegadas
            dpi (int): Resolução da figura em pontos por polegada
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.fig.tight_layout()

class VisualizationPanel(QWidget):
    """
    Painel de visualização de resultados para o GeoTherm.
    
    Permite visualizar mapas de calor 2D, visualização 3D e gráficos de evolução.
    """
    
    def __init__(self):
        """Inicializa o painel de visualização."""
        super().__init__()
        
        # Dados para visualização
        self.temperature_data = []
        self.time_points = []
        self.temperature_history = {}
        self.current_time_index = 0
        
        # Criar layout principal
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Criar widget de abas
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Criar abas
        self.create_3d_view_tab()
        self.create_slices_tab()
        self.create_graphs_tab()
    
    def create_3d_view_tab(self):
        """Cria a aba de visualização 3D."""
        # Criar widget e layout
        self.view_3d_widget = QWidget()
        view_3d_layout = QVBoxLayout()
        self.view_3d_widget.setLayout(view_3d_layout)
        
        # Adicionar placeholder para visualização 3D
        self.view_3d_canvas = MplCanvas(width=8, height=6)
        view_3d_layout.addWidget(self.view_3d_canvas)
        
        # Adicionar controles para visualização 3D
        controls_layout = QHBoxLayout()
        view_3d_layout.addLayout(controls_layout)
        
        # Tipo de visualização
        view_type_group = QGroupBox("Tipo de Visualização")
        view_type_layout = QVBoxLayout()
        view_type_group.setLayout(view_type_layout)
        
        self.view_type_combo = QComboBox()
        self.view_type_combo.addItems([
            "Volume Completo",
            "Isosuperfícies",
            "Cortes"
        ])
        view_type_layout.addWidget(self.view_type_combo)
        
        controls_layout.addWidget(view_type_group)
        
        # Opacidade
        opacity_group = QGroupBox("Opacidade")
        opacity_layout = QVBoxLayout()
        opacity_group.setLayout(opacity_layout)
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        opacity_layout.addWidget(self.opacity_slider)
        
        controls_layout.addWidget(opacity_group)
        
        # Mostrar arestas
        edges_group = QGroupBox("Arestas")
        edges_layout = QVBoxLayout()
        edges_group.setLayout(edges_layout)
        
        self.show_edges_combo = QComboBox()
        self.show_edges_combo.addItems([
            "Ocultar Arestas",
            "Mostrar Arestas"
        ])
        edges_layout.addWidget(self.show_edges_combo)
        
        controls_layout.addWidget(edges_group)
        
        # Adicionar aba ao widget de abas
        self.tab_widget.addTab(self.view_3d_widget, "Visualização 3D")
    
    def create_slices_tab(self):
        """Cria a aba de cortes 2D."""
        # Criar widget e layout
        self.view_slices_widget = QWidget()
        view_slices_layout = QVBoxLayout()
        self.view_slices_widget.setLayout(view_slices_layout)
        
        # Criar widget de abas para cortes
        self.slices_tab = QTabWidget()
        view_slices_layout.addWidget(self.slices_tab)
        
        # Criar abas para cada plano
        self.create_slice_tab("xy", "Corte XY")
        self.create_slice_tab("xz", "Corte XZ")
        self.create_slice_tab("yz", "Corte YZ")
        
        # Adicionar aba ao widget de abas principal
        self.tab_widget.addTab(self.view_slices_widget, "Cortes 2D")
    
    def create_slice_tab(self, plane, title):
        """
        Cria uma aba para um plano de corte específico.
        
        Parâmetros:
            plane (str): Plano de corte ('xy', 'xz' ou 'yz')
            title (str): Título da aba
        """
        # Criar widget e layout
        slice_widget = QWidget()
        slice_layout = QVBoxLayout()
        slice_widget.setLayout(slice_layout)
        
        # Adicionar canvas para visualização
        canvas = MplCanvas(width=8, height=6)
        slice_layout.addWidget(canvas)
        
        # Adicionar controles para visualização
        controls_layout = QHBoxLayout()
        slice_layout.addLayout(controls_layout)
        
        # Posição do corte
        position_group = QGroupBox("Posição do Corte")
        position_layout = QVBoxLayout()
        position_group.setLayout(position_layout)
        
        position_slider = QSlider(Qt.Horizontal)
        position_slider.setRange(0, 100)
        position_slider.setValue(50)
        position_layout.addWidget(position_slider)
        
        controls_layout.addWidget(position_group)
        
        # Mostrar contornos
        contour_group = QGroupBox("Contornos")
        contour_layout = QVBoxLayout()
        contour_group.setLayout(contour_layout)
        
        contour_combo = QComboBox()
        contour_combo.addItems([
            "Sem Contornos",
            "Mostrar Contornos"
        ])
        contour_layout.addWidget(contour_combo)
        
        controls_layout.addWidget(contour_group)
        
        # Mapa de cores
        colormap_group = QGroupBox("Mapa de Cores")
        colormap_layout = QVBoxLayout()
        colormap_group.setLayout(colormap_layout)
        
        colormap_combo = QComboBox()
        colormap_combo.addItems([
            "Térmico (Azul-Branco-Vermelho)",
            "Viridis",
            "Plasma",
            "Inferno",
            "Magma"
        ])
        colormap_layout.addWidget(colormap_combo)
        
        controls_layout.addWidget(colormap_group)
        
        # Armazenar widgets
        setattr(self, f"{plane}_canvas", canvas)
        setattr(self, f"{plane}_position_slider", position_slider)
        setattr(self, f"{plane}_contour_combo", contour_combo)
        setattr(self, f"{plane}_colormap_combo", colormap_combo)
        
        # Adicionar aba ao widget de abas de cortes
        self.slices_tab.addTab(slice_widget, title)
    
    def create_graphs_tab(self):
        """Cria a aba de gráficos."""
        # Criar widget e layout
        self.view_graphs_widget = QWidget()
        view_graphs_layout = QVBoxLayout()
        self.view_graphs_widget.setLayout(view_graphs_layout)
        
        # Criar widget de abas para gráficos
        self.graphs_tab = QTabWidget()
        view_graphs_layout.addWidget(self.graphs_tab)
        
        # Criar aba para evolução de temperatura
        self.create_temperature_evolution_tab()
        
        # Criar aba para evolução de isotermas
        self.create_isotherm_evolution_tab()
        
        # Adicionar aba ao widget de abas principal
        self.tab_widget.addTab(self.view_graphs_widget, "Gráficos")
    
    def create_temperature_evolution_tab(self):
        """Cria a aba de evolução de temperatura."""
        # Criar widget e layout
        temp_evolution_widget = QWidget()
        temp_evolution_layout = QVBoxLayout()
        temp_evolution_widget.setLayout(temp_evolution_layout)
        
        # Adicionar canvas para visualização
        self.temp_evolution_canvas = MplCanvas(width=8, height=6)
        temp_evolution_layout.addWidget(self.temp_evolution_canvas)
        
        # Adicionar controles para visualização
        controls_layout = QHBoxLayout()
        temp_evolution_layout.addLayout(controls_layout)
        
        # Ponto de medição
        point_group = QGroupBox("Ponto de Medição")
        point_layout = QVBoxLayout()
        point_group.setLayout(point_layout)
        
        self.point_combo = QComboBox()
        self.point_combo.addItems([
            "Centro da Intrusão",
            "Borda da Intrusão",
            "Encaixante Próximo",
            "Encaixante Distante"
        ])
        point_layout.addWidget(self.point_combo)
        
        controls_layout.addWidget(point_group)
        
        # Escala de tempo
        time_scale_group = QGroupBox("Escala de Tempo")
        time_scale_layout = QVBoxLayout()
        time_scale_group.setLayout(time_scale_layout)
        
        self.time_scale_combo = QComboBox()
        self.time_scale_combo.addItems([
            "Linear",
            "Logarítmica"
        ])
        self.time_scale_combo.setCurrentIndex(1)  # Logarítmica por padrão
        time_scale_layout.addWidget(self.time_scale_combo)
        
        controls_layout.addWidget(time_scale_group)
        
        # Adicionar aba ao widget de abas de gráficos
        self.graphs_tab.addTab(temp_evolution_widget, "Evolução de Temperatura")
    
    def create_isotherm_evolution_tab(self):
        """Cria a aba de evolução de isotermas."""
        # Criar widget e layout
        isotherm_evolution_widget = QWidget()
        isotherm_evolution_layout = QVBoxLayout()
        isotherm_evolution_widget.setLayout(isotherm_evolution_layout)
        
        # Adicionar canvas para visualização
        self.isotherm_evolution_canvas = MplCanvas(width=8, height=6)
        isotherm_evolution_layout.addWidget(self.isotherm_evolution_canvas)
        
        # Adicionar controles para visualização
        controls_layout = QHBoxLayout()
        isotherm_evolution_layout.addLayout(controls_layout)
        
        # Valor da isoterma
        isotherm_group = QGroupBox("Valor da Isoterma")
        isotherm_layout = QVBoxLayout()
        isotherm_group.setLayout(isotherm_layout)
        
        self.isotherm_combo = QComboBox()
        self.isotherm_combo.addItems([
            "600 °C",
            "700 °C",
            "800 °C",
            "900 °C",
            "1000 °C"
        ])
        isotherm_layout.addWidget(self.isotherm_combo)
        
        controls_layout.addWidget(isotherm_group)
        
        # Plano de corte
        plane_group = QGroupBox("Plano de Corte")
        plane_layout = QVBoxLayout()
        plane_group.setLayout(plane_layout)
        
        self.isotherm_plane_combo = QComboBox()
        self.isotherm_plane_combo.addItems([
            "XY (Z central)",
            "XZ (Y central)",
            "YZ (X central)"
        ])
        plane_layout.addWidget(self.isotherm_plane_combo)
        
        controls_layout.addWidget(plane_group)
        
        # Adicionar aba ao widget de abas de gráficos
        self.graphs_tab.addTab(isotherm_evolution_widget, "Evolução de Isotermas")
    
    def set_data(self, temperature_data, time_points, temperature_history=None):
        """
        Define os dados para visualização.
        
        Parâmetros:
            temperature_data (list): Lista de arrays de temperatura
            time_points (list): Lista de pontos de tempo
            temperature_history (dict): Dicionário com histórico de temperatura
        """
        self.temperature_data = temperature_data
        self.time_points = time_points
        
        if temperature_history:
            self.temperature_history = temperature_history
        
        # Atualizar visualizações
        self.update_visualizations()
    
    def set_time_index(self, time_index):
        """
        Define o índice de tempo atual.
        
        Parâmetros:
            time_index (int): Índice do ponto de tempo
        """
        if 0 <= time_index < len(self.time_points):
            self.current_time_index = time_index
            self.update_visualizations()
    
    def update_visualizations(self):
        """Atualiza todas as visualizações com os dados atuais."""
        if not self.temperature_data or self.current_time_index >= len(self.temperature_data):
            return
        
        # Obter dados para o tempo atual
        current_temp = self.temperature_data[self.current_time_index]
        current_time = self.time_points[self.current_time_index]
        
        # Atualizar visualização 3D
        self.update_3d_view(current_temp, current_time)
        
        # Atualizar cortes 2D
        self.update_slices(current_temp, current_time)
        
        # Atualizar gráficos
        self.update_graphs()
    
    def update_3d_view(self, temperature, time):
        """
        Atualiza a visualização 3D.
        
        Parâmetros:
            temperature (ndarray): Array 3D de temperatura
            time (float): Tempo atual
        """
        # Limpar figura
        self.view_3d_canvas.axes.clear()
        
        # Obter dimensões
        nx, ny, nz = temperature.shape
        
        # Criar visualização 3D simplificada (projeção 2D)
        # Em uma implementação real, usaríamos PyVista para visualização 3D completa
        
        # Obter fatias centrais
        slice_xy = temperature[:, :, nz // 2]
        slice_xz = temperature[:, ny // 2, :]
        
        # Criar visualização composta
        self.view_3d_canvas.axes.imshow(slice_xy.T, origin='lower', cmap='coolwarm',
                                       extent=[0, nx, 0, ny], alpha=0.7)
        self.view_3d_canvas.axes.contour(slice_xy.T, origin='lower', cmap='coolwarm',
                                        extent=[0, nx, 0, ny], alpha=0.5)
        
        # Configurar gráfico
        self.view_3d_canvas.axes.set_title(f"Visualização 3D (Simplificada) - t = {time:.2e} s")
        self.view_3d_canvas.axes.set_xlabel("X")
        self.view_3d_canvas.axes.set_ylabel("Y")
        
        # Atualizar canvas
        self.view_3d_canvas.draw()
    
    def update_slices(self, temperature, time):
        """
        Atualiza os cortes 2D.
        
        Parâmetros:
            temperature (ndarray): Array 3D de temperatura
            time (float): Tempo atual
        """
        # Obter dimensões
        nx, ny, nz = temperature.shape
        
        # Obter fatias centrais
        slice_xy = temperature[:, :, nz // 2]
        slice_xz = temperature[:, ny // 2, :]
        slice_yz = temperature[nx // 2, :, :]
        
        # Configurar mapa de cores
        colors = [(0, 0, 1), (1, 1, 1), (1, 0, 0)]  # azul -> branco -> vermelho
        cmap = LinearSegmentedColormap.from_list('thermal', colors, N=256)
        
        # Atualizar corte XY
        self.xy_canvas.axes.clear()
        im = self.xy_canvas.axes.imshow(slice_xy.T, origin='lower', cmap=cmap)
        self.xy_canvas.fig.colorbar(im, ax=self.xy_canvas.axes, label='Temperatura (°C)')
        self.xy_canvas.axes.set_title(f"Corte XY (Z = {nz // 2}) - t = {time:.2e} s")
        self.xy_canvas.axes.set_xlabel("X")
        self.xy_canvas.axes.set_ylabel("Y")
        self.xy_canvas.draw()
        
        # Atualizar corte XZ
        self.xz_canvas.axes.clear()
        im = self.xz_canvas.axes.imshow(slice_xz.T, origin='lower', cmap=cmap)
        self.xz_canvas.fig.colorbar(im, ax=self.xz_canvas.axes, label='Temperatura (°C)')
        self.xz_canvas.axes.set_title(f"Corte XZ (Y = {ny // 2}) - t = {time:.2e} s")
        self.xz_canvas.axes.set_xlabel("X")
        self.xz_canvas.axes.set_ylabel("Z")
        self.xz_canvas.draw()
        
        # Atualizar corte YZ
        self.yz_canvas.axes.clear()
        im = self.yz_canvas.axes.imshow(slice_yz.T, origin='lower', cmap=cmap)
        self.yz_canvas.fig.colorbar(im, ax=self.yz_canvas.axes, label='Temperatura (°C)')
        self.yz_canvas.axes.set_title(f"Corte YZ (X = {nx // 2}) - t = {time:.2e} s")
        self.yz_canvas.axes.set_xlabel("Y")
        self.yz_canvas.axes.set_ylabel("Z")
        self.yz_canvas.draw()
    
    def update_graphs(self):
        """Atualiza os gráficos de evolução."""
        # Verificar se há dados de histórico
        if not self.temperature_history:
            return
        
        # Atualizar gráfico de evolução de temperatura
        self.temp_evolution_canvas.axes.clear()
        
        # Obter escala de tempo
        time_scale = self.time_scale_combo.currentText()
        log_scale = (time_scale == "Logarítmica")
        
        # Plotar histórico para cada ponto
        for i, (point, history) in enumerate(self.temperature_history.items()):
            times = [t for t, _ in history]
            temps = [temp for _, temp in history]
            
            label = f"Ponto {i+1}: {point}"
            self.temp_evolution_canvas.axes.plot(times, temps, '-o', label=label)
        
        # Configurar gráfico
        self.temp_evolution_canvas.axes.set_title("Evolução de Temperatura")
        self.temp_evolution_canvas.axes.set_xlabel("Tempo (s)")
        self.temp_evolution_canvas.axes.set_ylabel("Temperatura (°C)")
        
        if log_scale:
            self.temp_evolution_canvas.axes.set_xscale('log')
        
        self.temp_evolution_canvas.axes.grid(True)
        self.temp_evolution_canvas.axes.legend()
        
        # Atualizar canvas
        self.temp_evolution_canvas.draw()
        
        # Atualizar gráfico de evolução de isotermas
        self.isotherm_evolution_canvas.axes.clear()
        
        # Obter valor da isoterma
        isotherm_text = self.isotherm_combo.currentText()
        isotherm_value = float(isotherm_text.split()[0])
        
        # Obter plano de corte
        plane_text = self.isotherm_plane_combo.currentText()
        
        # Configurar mapa de cores
        cmap = plt.cm.viridis
        
        # Plotar contornos para cada ponto de tempo
        for i, temp in enumerate(self.temperature_data):
            if i % max(1, len(self.temperature_data) // 5) != 0:
                continue  # Plotar apenas alguns pontos de tempo
            
            # Obter fatia central
            if plane_text.startswith("XY"):
                slice_2d = temp[:, :, temp.shape[2] // 2]
            elif plane_text.startswith("XZ"):
                slice_2d = temp[:, temp.shape[1] // 2, :]
            else:  # YZ
                slice_2d = temp[temp.shape[0] // 2, :, :]
            
            # Plotar contorno da isoterma
            try:
                cs = self.isotherm_evolution_canvas.axes.contour(
                    slice_2d.T, levels=[isotherm_value], 
                    colors=[cmap(i / len(self.temperature_data))]
                )
                
                # Adicionar rótulo
                fmt = {cs.levels[0]: f't{i}'}
                self.isotherm_evolution_canvas.axes.clabel(cs, cs.levels, inline=True, fmt=fmt, fontsize=10)
            except:
                # Isoterma pode não existir neste ponto de tempo
                pass
        
        # Configurar gráfico
        self.isotherm_evolution_canvas.axes.set_title(f"Evolução da Isoterma {isotherm_value}°C")
        self.isotherm_evolution_canvas.axes.set_xlabel("X")
        self.isotherm_evolution_canvas.axes.set_ylabel("Y")
        self.isotherm_evolution_canvas.axes.grid(True)
        
        # Atualizar canvas
        self.isotherm_evolution_canvas.draw()
    
    def clear_visualizations(self):
        """Limpa todas as visualizações."""
        # Limpar dados
        self.temperature_data = []
        self.time_points = []
        self.temperature_history = {}
        self.current_time_index = 0
        
        # Limpar visualização 3D
        self.view_3d_canvas.axes.clear()
        self.view_3d_canvas.axes.set_title("Sem dados")
        self.view_3d_canvas.draw()
        
        # Limpar cortes 2D
        for plane in ['xy', 'xz', 'yz']:
            canvas = getattr(self, f"{plane}_canvas")
            canvas.axes.clear()
            canvas.axes.set_title("Sem dados")
            canvas.draw()
        
        # Limpar gráficos
        self.temp_evolution_canvas.axes.clear()
        self.temp_evolution_canvas.axes.set_title("Sem dados")
        self.temp_evolution_canvas.draw()
        
        self.isotherm_evolution_canvas.axes.clear()
        self.isotherm_evolution_canvas.axes.set_title("Sem dados")
        self.isotherm_evolution_canvas.draw()
