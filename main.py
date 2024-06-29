import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QAction, QFileDialog, QLabel, QMenuBar, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from gt_data.input_module import GeometrySelectionDialog, ParameterInputDialog
from gt_data.thermal_model import ThermalModel
from gt_data.visualization import Visualization

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thermal Modeling Software")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("gt_data/images/icon.png"))

        self.thermal_model = ThermalModel()
        self.visualization = Visualization()

        self.initUI()
        self.createMenu()
        self.data = {}  # Inicializa os dados como um dicionário
        self.parameters = None
        self.results = None  # Armazena os resultados da modelagem

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Adicionar imagem central
        self.logo_label = QLabel(self)
        pixmap = QPixmap("gt_data/images/logo.png")
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
        self.run_button.setEnabled(False)
        layout.addWidget(self.run_button)

        self.visualize_button = QPushButton("Visualize Results")
        self.visualize_button.clicked.connect(self.visualizeResults)
        self.visualize_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.visualize_button.setEnabled(False)
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

        resume_action = QAction("Resume", self)
        resume_action.triggered.connect(self.show_resume)
        file_menu.addAction(resume_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_action = QAction("View README on GitHub", self)
        help_action.triggered.connect(self.viewReadme)
        help_menu.addAction(help_action)

    def enterInputData(self):
        geometry_dialog = GeometrySelectionDialog()
        if geometry_dialog.exec():
            geometry, d, id_ = geometry_dialog.get_geometry_and_d()
            parameter_dialog = ParameterInputDialog(geometry)
            if parameter_dialog.exec():
                self.parameters = parameter_dialog.get_parameters()
                self.parameters["d"] = d
                self.parameters["id"] = id_
                self.data['geometry'] = geometry  # Definindo a geometria no self.data
                self.data['id'] = id_
                self.run_button.setEnabled(True)

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Model", "", "Model Files (*.mdl);;All Files (*)", options=options)
        if fileName:
            pass

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Model", "", "Model Files (*.mdl);;All Files (*)", options=options)
        if fileName:
            pass

    def viewReadme(self):
        import webbrowser
        webbrowser.open("https://github.com/valkgeo/GeoTherm/blob/main/README.md")

    def run_model(self):
        if self.parameters:
            try:
                geometry = self.parameters["geometry"]
                T0 = self.parameters["T0"]
                K1 = self.parameters["K1"]
                k = self.parameters["k"]
                K = self.parameters["K"]
                k1 = self.parameters["k1"]
                g = self.parameters["g"]
                l = self.parameters["l"]
                d = self.parameters.get("d", None)
                time = self.parameters["time"]
                self.results = self.thermal_model.run(self.data, geometry, T0, K1, k, K, k1, g, l, d, time)
                self.visualize_button.setEnabled(True)
                QMessageBox.information(self, "Model Ready", "The thermal model is ready for visualization.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while running the model:\n{e}")
        else:
            QMessageBox.warning(self, "No Data", "Please enter input data before running the model.")

    def visualizeResults(self):
        if self.results:
            self.visualization.set_data(self.results)
            self.visualization.set_id(self.parameters.get("id", ""))
            self.visualization.show()
        else:
            QMessageBox.warning(self, "No Results", "Run the thermal model before visualizing results.")

    def show_resume(self):
        if not self.parameters:
            QMessageBox.warning(self, "No Data", "No input data available.")
        else:
            resume_message = "\n".join([f"{key}: {value}" for key, value in self.parameters.items()])
            QMessageBox.information(self, "Input Data Resume", resume_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())