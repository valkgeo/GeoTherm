"""
GeoTherm - Módulo de Interface Gráfica

Este módulo implementa a tela de carregamento do programa GeoTherm.
"""

import sys
import os
from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtCore import Qt, QTimer, QSize

class SplashScreen(QSplashScreen):
    """
    Tela de carregamento personalizada para o GeoTherm.
    
    Exibe um logo "GT GeoTherm" em tons de vermelho com uma barra de progresso.
    """
    
    def __init__(self):
        """Inicializa a tela de carregamento."""
        # Criar pixmap para a tela de carregamento
        pixmap = QPixmap(QSize(500, 500))
        super().__init__(pixmap)
        
        # Configurar layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Criar widget para conteúdo
        self.content = QWidget(self)
        self.content.setGeometry(0, 0, 500, 500)
        
        # Criar gradiente de fundo
        self.gradient = QLinearGradient(0, 0, 0, 500)
        self.gradient.setColorAt(0, QColor(180, 0, 0))  # Vermelho escuro
        self.gradient.setColorAt(1, QColor(120, 0, 0))  # Vermelho mais escuro
        
        # Criar logo GT
        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(150, 150)
        self.logo_label.setStyleSheet("""
            background-color: white;
            border-radius: 20px;
            margin: 20px;
        """)
        
        # Criar texto GT no logo
        self.logo_text = QLabel("GT", self.logo_label)
        self.logo_text.setAlignment(Qt.AlignCenter)
        self.logo_text.setGeometry(0, 0, 150, 150)
        self.logo_text.setStyleSheet("""
            color: #b00000;
            font-size: 80px;
            font-weight: bold;
            font-family: Arial;
        """)
        
        # Criar texto GeoTherm
        self.name_label = QLabel("GeoTherm", self)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
            font-family: Arial;
            margin: 10px;
        """)
        
        # Criar barra de progresso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 100);
                color: white;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: white;
                width: 10px;
                margin: 0.5px;
            }
        """)
        
        # Criar label para mensagens de status
        self.status_label = QLabel("Inicializando...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-family: Arial;
            margin: 5px;
        """)
        
        # Posicionar elementos
        self.logo_label.move(175, 100)
        self.name_label.move(0, 270)
        self.name_label.setFixedSize(500, 50)
        self.progress_bar.move(100, 350)
        self.progress_bar.setFixedSize(300, 20)
        self.status_label.move(0, 380)
        self.status_label.setFixedSize(500, 30)
        
        # Iniciar animação de progresso
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.progress = 0
        
        # Renderizar tela
        self.draw_splash()
    
    def draw_splash(self):
        """Renderiza a tela de carregamento."""
        # Criar pixmap para desenho
        pixmap = QPixmap(QSize(500, 500))
        pixmap.fill(Qt.transparent)
        
        # Criar painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Desenhar fundo com gradiente
        painter.setBrush(self.gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 500, 500)
        
        # Finalizar painter
        painter.end()
        
        # Definir pixmap
        self.setPixmap(pixmap)
    
    def update_progress(self):
        """Atualiza o progresso da barra."""
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        
        # Atualizar mensagem de status
        if self.progress < 20:
            self.status_label.setText("Inicializando componentes...")
        elif self.progress < 40:
            self.status_label.setText("Carregando modelo térmico...")
        elif self.progress < 60:
            self.status_label.setText("Preparando interface gráfica...")
        elif self.progress < 80:
            self.status_label.setText("Configurando visualizações...")
        else:
            self.status_label.setText("Finalizando carregamento...")
        
        # Parar timer quando atingir 100%
        if self.progress >= 100:
            self.timer.stop()
    
    def start_progress(self, interval=30):
        """
        Inicia a animação de progresso.
        
        Parâmetros:
            interval (int): Intervalo entre atualizações (ms)
        """
        self.timer.start(interval)
    
    def finish_splash(self, main_window):
        """
        Finaliza a tela de carregamento e exibe a janela principal.
        
        Parâmetros:
            main_window: Janela principal a ser exibida
        """
        # Garantir que o progresso chegue a 100%
        self.progress_bar.setValue(100)
        self.status_label.setText("Carregamento concluído!")
        
        # Finalizar splash screen
        self.finish(main_window)

def show_splash_screen():
    """
    Cria e exibe a tela de carregamento.
    
    Retorna:
        SplashScreen: Tela de carregamento
    """
    # Criar tela de carregamento
    splash = SplashScreen()
    
    # Exibir tela
    splash.show()
    
    # Iniciar animação de progresso
    splash.start_progress()
    
    return splash
