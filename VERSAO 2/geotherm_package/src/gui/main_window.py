"""
GeoTherm - Janela Principal

Este módulo implementa a janela principal do programa GeoTherm.
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QDockWidget, QAction, QMenu, QToolBar, 
                            QStatusBar, QFileDialog, QMessageBox, QTabWidget)
from PyQt5.QtGui import QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QSize

from src.gui.parameter_panel import ParameterPanel
from src.gui.visualization_panel import VisualizationPanel
from src.gui.simulation_control import SimulationControl

class MainWindow(QMainWindow):
    """
    Janela principal do programa GeoTherm.
    
    Integra todos os componentes da interface gráfica e gerencia a interação entre eles.
    """
    
    def __init__(self):
        """Inicializa a janela principal."""
        super().__init__()
        
        # Configurar janela
        self.setWindowTitle("GeoTherm - Modelamento de Fluxo Térmico")
        self.setMinimumSize(1200, 800)
        
        # Configurar estilo
        self.setup_style()
        
        # Criar componentes da interface
        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()
        self.create_dock_widgets()
        self.create_central_widget()
        
        # Configurar estado inicial
        self.update_ui_state(False)
    
    def setup_style(self):
        """Configura o estilo da janela."""
        # Configurar paleta de cores
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(50, 50, 50))
        palette.setColor(QPalette.Text, QColor(50, 50, 50))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(180, 0, 0))  # Vermelho escuro
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Aplicar paleta
        self.setPalette(palette)
    
    def create_actions(self):
        """Cria as ações da janela principal."""
        # Ações do menu Arquivo
        self.new_action = QAction("&Novo", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.setStatusTip("Criar novo projeto")
        self.new_action.triggered.connect(self.new_project)
        
        self.open_action = QAction("&Abrir...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Abrir projeto existente")
        self.open_action.triggered.connect(self.open_project)
        
        self.save_action = QAction("&Salvar", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Salvar projeto atual")
        self.save_action.triggered.connect(self.save_project)
        
        self.save_as_action = QAction("Salvar &como...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setStatusTip("Salvar projeto com novo nome")
        self.save_as_action.triggered.connect(self.save_project_as)
        
        self.export_action = QAction("&Exportar resultados...", self)
        self.export_action.setStatusTip("Exportar resultados da simulação")
        self.export_action.triggered.connect(self.export_results)
        
        self.exit_action = QAction("Sai&r", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Sair do programa")
        self.exit_action.triggered.connect(self.close)
        
        # Ações do menu Editar
        self.undo_action = QAction("&Desfazer", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setStatusTip("Desfazer última ação")
        
        self.redo_action = QAction("&Refazer", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setStatusTip("Refazer última ação")
        
        self.preferences_action = QAction("&Preferências...", self)
        self.preferences_action.setStatusTip("Configurar preferências do programa")
        
        # Ações do menu Visualização
        self.view_3d_action = QAction("Visualização &3D", self)
        self.view_3d_action.setCheckable(True)
        self.view_3d_action.setChecked(True)
        self.view_3d_action.setStatusTip("Mostrar/ocultar visualização 3D")
        
        self.view_slices_action = QAction("&Cortes 2D", self)
        self.view_slices_action.setCheckable(True)
        self.view_slices_action.setChecked(True)
        self.view_slices_action.setStatusTip("Mostrar/ocultar cortes 2D")
        
        self.view_graphs_action = QAction("&Gráficos", self)
        self.view_graphs_action.setCheckable(True)
        self.view_graphs_action.setChecked(True)
        self.view_graphs_action.setStatusTip("Mostrar/ocultar gráficos")
        
        # Ações do menu Simulação
        self.start_action = QAction("&Iniciar", self)
        self.start_action.setShortcut("F5")
        self.start_action.setStatusTip("Iniciar simulação")
        
        self.pause_action = QAction("&Pausar", self)
        self.pause_action.setShortcut("F6")
        self.pause_action.setStatusTip("Pausar/retomar simulação")
        
        self.stop_action = QAction("&Parar", self)
        self.stop_action.setShortcut("F7")
        self.stop_action.setStatusTip("Parar simulação")
        
        # Ações do menu Ajuda
        self.help_action = QAction("&Ajuda", self)
        self.help_action.setShortcut("F1")
        self.help_action.setStatusTip("Mostrar ajuda")
        
        self.about_action = QAction("&Sobre", self)
        self.about_action.setStatusTip("Mostrar informações sobre o programa")
        self.about_action.triggered.connect(self.show_about)
    
    def create_menus(self):
        """Cria os menus da janela principal."""
        # Menu Arquivo
        self.file_menu = self.menuBar().addMenu("&Arquivo")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.export_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Menu Editar
        self.edit_menu = self.menuBar().addMenu("&Editar")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.preferences_action)
        
        # Menu Visualização
        self.view_menu = self.menuBar().addMenu("&Visualização")
        self.view_menu.addAction(self.view_3d_action)
        self.view_menu.addAction(self.view_slices_action)
        self.view_menu.addAction(self.view_graphs_action)
        
        # Menu Simulação
        self.simulation_menu = self.menuBar().addMenu("&Simulação")
        self.simulation_menu.addAction(self.start_action)
        self.simulation_menu.addAction(self.pause_action)
        self.simulation_menu.addAction(self.stop_action)
        
        # Menu Ajuda
        self.help_menu = self.menuBar().addMenu("A&juda")
        self.help_menu.addAction(self.help_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)
    
    def create_toolbars(self):
        """Cria as barras de ferramentas da janela principal."""
        # Barra de ferramentas principal
        self.main_toolbar = self.addToolBar("Principal")
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(24, 24))
        
        # Adicionar ações
        self.main_toolbar.addAction(self.new_action)
        self.main_toolbar.addAction(self.open_action)
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.start_action)
        self.main_toolbar.addAction(self.pause_action)
        self.main_toolbar.addAction(self.stop_action)
    
    def create_status_bar(self):
        """Cria a barra de status da janela principal."""
        self.statusBar().showMessage("Pronto")
    
    def create_dock_widgets(self):
        """Cria os widgets de dock da janela principal."""
        # Dock para painel de parâmetros
        self.parameter_dock = QDockWidget("Parâmetros", self)
        self.parameter_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.parameter_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # Criar painel de parâmetros
        self.parameter_panel = ParameterPanel()
        self.parameter_dock.setWidget(self.parameter_panel)
        
        # Adicionar dock à janela
        self.addDockWidget(Qt.LeftDockWidgetArea, self.parameter_dock)
        
        # Dock para controle de simulação
        self.simulation_dock = QDockWidget("Controle de Simulação", self)
        self.simulation_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.simulation_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # Criar controle de simulação
        self.simulation_control = SimulationControl()
        self.simulation_dock.setWidget(self.simulation_control)
        
        # Adicionar dock à janela
        self.addDockWidget(Qt.BottomDockWidgetArea, self.simulation_dock)
    
    def create_central_widget(self):
        """Cria o widget central da janela principal."""
        # Criar painel de visualização
        self.visualization_panel = VisualizationPanel()
        
        # Definir como widget central
        self.setCentralWidget(self.visualization_panel)
    
    def update_ui_state(self, simulation_running):
        """
        Atualiza o estado da interface com base no estado da simulação.
        
        Parâmetros:
            simulation_running (bool): Se a simulação está em execução
        """
        # Atualizar ações
        self.start_action.setEnabled(not simulation_running)
        self.pause_action.setEnabled(simulation_running)
        self.stop_action.setEnabled(simulation_running)
        
        # Atualizar menus
        self.file_menu.setEnabled(not simulation_running)
        self.edit_menu.setEnabled(not simulation_running)
    
    def new_project(self):
        """Cria um novo projeto."""
        # Verificar se há alterações não salvas
        # TODO: Implementar verificação de alterações
        
        # Redefinir parâmetros
        self.parameter_panel.reset_parameters()
        
        # Limpar visualizações
        self.visualization_panel.clear_visualizations()
        
        # Atualizar status
        self.statusBar().showMessage("Novo projeto criado", 3000)
    
    def open_project(self):
        """Abre um projeto existente."""
        # Abrir diálogo de arquivo
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Projeto", "", "Arquivos GeoTherm (*.geo);;Todos os Arquivos (*)"
        )
        
        if file_path:
            # TODO: Implementar carregamento de projeto
            self.statusBar().showMessage(f"Projeto aberto: {file_path}", 3000)
    
    def save_project(self):
        """Salva o projeto atual."""
        # TODO: Implementar salvamento de projeto
        self.statusBar().showMessage("Projeto salvo", 3000)
    
    def save_project_as(self):
        """Salva o projeto com um novo nome."""
        # Abrir diálogo de arquivo
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Projeto Como", "", "Arquivos GeoTherm (*.geo);;Todos os Arquivos (*)"
        )
        
        if file_path:
            # TODO: Implementar salvamento de projeto
            self.statusBar().showMessage(f"Projeto salvo como: {file_path}", 3000)
    
    def export_results(self):
        """Exporta os resultados da simulação."""
        # Abrir diálogo de diretório
        dir_path = QFileDialog.getExistingDirectory(
            self, "Exportar Resultados", "", QFileDialog.ShowDirsOnly
        )
        
        if dir_path:
            # TODO: Implementar exportação de resultados
            self.statusBar().showMessage(f"Resultados exportados para: {dir_path}", 3000)
    
    def show_about(self):
        """Mostra informações sobre o programa."""
        QMessageBox.about(
            self,
            "Sobre o GeoTherm",
            "<h3>GeoTherm</h3>"
            "<p>Versão 1.0.0</p>"
            "<p>Programa para modelamento de fluxo térmico em intrusões ígneas.</p>"
            "<p>Desenvolvido como suplemento para publicação científica.</p>"
            "<p>&copy; 2025 GeoTherm Team</p>"
        )
    
    def closeEvent(self, event):
        """
        Manipula o evento de fechamento da janela.
        
        Parâmetros:
            event: Evento de fechamento
        """
        # Verificar se há alterações não salvas
        # TODO: Implementar verificação de alterações
        
        # Confirmar fechamento
        reply = QMessageBox.question(
            self,
            "Confirmar Saída",
            "Tem certeza que deseja sair?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
