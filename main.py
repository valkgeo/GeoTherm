import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QAction, QLabel,
    QMessageBox, QDialog, QLineEdit, QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
from gt_data.input_module import GeometrySelectionDialog, ParameterInputDialog
from gt_data.thermal_model import ThermalModel
from gt_data.visualization import Visualization


class MethodSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Modeling Method")
        self.setGeometry(200, 200, 300, 150)

        self.radio_analytical = QRadioButton("Analytical Solution (Simple Geometries)")
        self.radio_numerical = QRadioButton("Numerical Modeling (Finite Element Method)")
        self.radio_analytical.setChecked(True)  # Default selection

        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.radio_analytical)
        self.button_group.addButton(self.radio_numerical)

        layout = QVBoxLayout()
        layout.addWidget(self.radio_analytical)
        layout.addWidget(self.radio_numerical)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_selected_method(self):
        if self.radio_analytical.isChecked():
            return "analytical"
        elif self.radio_numerical.isChecked():
            return "numerical"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thermal Modeling Software")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("gt_data/images/icon.png"))

        self.thermal_model = ThermalModel()
        self.visualization = Visualization()
        # Connect the next input signal (if the visualization window is used for that purpose)
        self.visualization.next_input_signal.connect(self.clear_inputs)

        self.initUI()
        self.createMenu()
        self.data = {}
        self.parameters = None
        self.results = None

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        self.logo_label = QLabel(self)
        pixmap = QPixmap("gt_data/images/logo.png")
        self.logo_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

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
        self.run_button.setStyleSheet("font-size: 18px; padding: 10px; color: gray;")
        self.run_button.setEnabled(False)
        layout.addWidget(self.run_button)

        self.visualize_button = QPushButton("Visualize Results")
        self.visualize_button.clicked.connect(self.visualizeResults)
        self.visualize_button.setStyleSheet("font-size: 18px; padding: 10px; color: gray;")
        self.visualize_button.setEnabled(False)
        layout.addWidget(self.visualize_button)

        self.clear_button = QPushButton("Clear Inputs")
        self.clear_button.clicked.connect(self.clear_inputs)
        self.clear_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.clear_button.setVisible(False)
        layout.addWidget(self.clear_button)

        # NEW: Status label at the bottom for progress messages.
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def createMenu(self):
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")

        help_action = QAction("View README on GitHub", self)
        help_action.triggered.connect(self.viewReadme)
        help_menu.addAction(help_action)

    def enterInputData(self):
        method_dialog = MethodSelectionDialog()
        if method_dialog.exec():
            selected_method = method_dialog.get_selected_method()
            self.data['method'] = selected_method

            if selected_method == "analytical":
                self.configure_analytical_input()
            elif selected_method == "numerical":
                QMessageBox.information(self, "Numerical Modeling",
                    "The method using numerical modeling is still in development.")
                # Additional handling for numerical modeling

    def configure_analytical_input(self):
        geometry_dialog = GeometrySelectionDialog()
        if geometry_dialog.exec():
            geometry, d, id_ = geometry_dialog.get_geometry_and_d()
            print("Geometry selected:", geometry, "d:", d, "ID:", id_)  # Debug print
            parameter_dialog = ParameterInputDialog(geometry)
            if parameter_dialog.exec():
                self.parameters = parameter_dialog.get_parameters()
                self.parameters["d"] = d
                self.parameters["id"] = id_
                self.data['geometry'] = geometry
                self.data['id'] = id_
                self.data['d'] = d
                self.data['time'] = self.parameters["time"]
                self.run_button.setEnabled(True)
                self.run_button.setStyleSheet("font-size: 18px; padding: 10px; color: black;")

    def viewReadme(self):
        import webbrowser
        webbrowser.open("https://github.com/valkgeo/GeoTherm/blob/main/README.md")

    def run_model(self):
        if self.parameters:
            try:
                if self.data['method'] == "analytical":
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
                    self.visualize_button.setStyleSheet("font-size: 18px; padding: 10px; color: red;")
                    self.clear_button.setVisible(True)
                    QMessageBox.information(self, "Model Ready", "Analytical model ready for visualization.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while running the model:\n{e}")
        else:
            QMessageBox.warning(self, "No Data", "Please enter input data before running the model.")

    def clear_inputs(self):
        """
        Clears all input data and displays a progress message in the status label.
        Shows "Clearing data input..." and then after 1 second "Data input cleared" for 1 second.
        """
        self.parameters = None
        self.data = {}
        self.results = None
        self.run_button.setEnabled(False)
        self.run_button.setStyleSheet("font-size: 18px; padding: 10px; color: gray;")
        self.visualize_button.setEnabled(False)
        self.visualize_button.setStyleSheet("font-size: 18px; padding: 10px; color: gray;")
        self.clear_button.setVisible(False)

        self.status_label.setText("Clearing data input...")
        QApplication.processEvents()  # Ensure the label updates immediately

        QTimer.singleShot(1000, self._clear_inputs_done)

    def _clear_inputs_done(self):
        self.status_label.setText("Data input cleared")
        QTimer.singleShot(1000, lambda: self.status_label.setText(""))

    def visualizeResults(self):
        if self.results:
            self.visualization.set_data(self.results, self.data.get("geometry", "Unknown"))
            self.visualization.set_id(self.data.get("id", "Unknown"))
            self.visualization.show()
        else:
            QMessageBox.warning(self, "No Results", "Run the thermal model before visualizing results.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
