import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QAction, QFileDialog, QLabel, QMenuBar, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from gt_data.input_module import InputModule
from gt_data.thermal_model import ThermalModel
from gt_data.visualization import Visualization

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thermal Modeling Software")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("gt_data/images/icon.png"))

        self.input_module = InputModule()
        self.thermal_model = ThermalModel()
        self.visualization = Visualization()

        self.initUI()
        self.createMenu()
        self.data = None  # Inicializa os dados como None

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Adicionar imagem central
        self.logo_label = QLabel(self)
        pixmap = QPixmap("gt_data/images/logo.png")  # Substitua por sua nova imagem central
        self.logo_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Título centralizado
        title_label = QLabel("GEOTHERM v1.0", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: orange;")
        layout.addWidget(title_label)

        input_button = QPushButton("Enter Input Data")
        input_button.clicked.connect(self.enterInputData)
        input_button.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(input_button)

        self.run_button = QPushButton("Run Thermal Model")
        self.run_button.clicked.connect(self.run_model)
        self.run_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.run_button.setEnabled(False)  # Desativa o botão inicialmente
        layout.addWidget(self.run_button)

        self.visualize_button = QPushButton("Visualize Results")
        self.visualize_button.clicked.connect(self.visualizeResults)
        self.visualize_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.visualize_button.setEnabled(False)  # Desativa o botão inicialmente
        layout.addWidget(self.visualize_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def createMenu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        help_menu = menubar.addMenu("Help")

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.saveFile)
        file_menu.addAction(save_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)

        help_action = QAction("View README on GitHub", self)
        help_action.triggered.connect(self.viewReadme)
        help_menu.addAction(help_action)

    def enterInputData(self):
        self.input_module.exec()
        self.data = self.input_module.get_data()
        if self.data:
            self.run_button.setEnabled(True)

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Model", "", "Model Files (*.mdl);;All Files (*)", options=options)
        if fileName:
            # Implementar funcionalidade de salvar dados
            pass

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Model", "", "Model Files (*.mdl);;All Files (*)", options=options)
        if fileName:
            # Implementar funcionalidade de abrir dados
            pass

    def viewReadme(self):
        import webbrowser
        webbrowser.open("https://github.com/seu-usuario/seu-repositorio/blob/main/README.md")

    def run_model(self):
        if self.data:
            try:
                results = self.thermal_model.run(self.data)
                self.visualization.set_data(results)
                self.visualize_button.setEnabled(True)  # Ativa o botão após o modelo ser executado
                QMessageBox.information(self, "Model Ready", "The thermal model is ready for visualization.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while running the model:\n{e}")
        else:
            QMessageBox.warning(self, "No Data", "Please enter input data before running the model.")

    def visualizeResults(self):
        if self.visualization.data:
            self.visualization.show()
        else:
            QMessageBox.warning(self, "No Results", "Run the thermal model before visualizing results.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())