import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QAction, QLabel,
    QMessageBox, QDialog, QLineEdit, QRadioButton, QButtonGroup, QFileDialog, QFormLayout, QCheckBox, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
from gt_data.input_module import GeometrySelectionDialog, ParameterInputDialog
from gt_data.thermal_model import ThermalModel
from gt_data.visualization import Visualization
from gt_data.data_manager import data_manager   # Import the global DataManager instance


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
        # Connect the next input signal from visualization to clear_inputs.
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

        # "Enter Input Data" button
        self.input_button = QPushButton("Enter Input Data")
        self.input_button.clicked.connect(self.enterInputData)
        self.input_button.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(self.input_button)

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

        # Status label for progress messages
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def createMenu(self):
        menubar = self.menuBar()

        # File menu with Open, Save, and Exit actions.
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.load_data)
        file_menu.addAction(open_action)

        self.save_action = QAction("Save", self)
        # Enable Save only if there is at least one stored input
        self.save_action.setEnabled(bool(data_manager.get_ids()))
        self.save_action.triggered.connect(self.save_data)
        file_menu.addAction(self.save_action)

        # Enable setting plot configuration default
        set_plot_defaults_action = QAction("Set Plot Configuration Defaults", self)
        set_plot_defaults_action.triggered.connect(self.set_plot_defaults)
        file_menu.addAction(set_plot_defaults_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_action = QAction("View README on GitHub", self)
        help_action.triggered.connect(self.viewReadme)
        help_menu.addAction(help_action)
    
    def set_plot_defaults(self):
        """
        Opens a dialog to set default plot configuration values.
        These values are stored in the DataManager.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Plot Configuration Defaults")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QFormLayout()
        
        # Auto-plot checkbox
        auto_plot_checkbox = QCheckBox("Auto-plot configuration")
        auto_plot_checkbox.setChecked(data_manager.get_plot_defaults().get("auto_plot", True))
        layout.addRow("Enable Auto-Plot:", auto_plot_checkbox)
        
        # Custom x value input
        x_custom_input = QLineEdit()
        x_custom_input.setText(str(data_manager.get_plot_defaults().get("x_custom", "")))
        x_custom_input.setPlaceholderText("Enter custom -x to +x range")
        layout.addRow("Custom X Value:", x_custom_input)
        
        # Tmin input
        Tmin_input = QLineEdit()
        Tmin_input.setText(str(data_manager.get_plot_defaults().get("Tmin", "")))
        Tmin_input.setPlaceholderText("Enter minimum Y value")
        layout.addRow("Minimum Y value (Tmin):", Tmin_input)
        
        # Tmax input
        Tmax_input = QLineEdit()
        Tmax_input.setText(str(data_manager.get_plot_defaults().get("Tmax", "")))
        Tmax_input.setPlaceholderText("Enter maximum Y value")
        layout.addRow("Maximum Y value (Tmax):", Tmax_input)
        
        # OK and Cancel buttons
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        
        def toggle_fields(checked):
            if checked:
                x_custom_input.setEnabled(False)
                Tmin_input.setEnabled(False)
                Tmax_input.setEnabled(False)
            else:
                x_custom_input.setEnabled(True)
                Tmin_input.setEnabled(True)
                Tmax_input.setEnabled(True)
        
        auto_plot_checkbox.toggled.connect(toggle_fields)
        toggle_fields(auto_plot_checkbox.isChecked())
        
        def save_defaults():
            try:
                if not auto_plot_checkbox.isChecked():
                    float(x_custom_input.text())
                    float(Tmin_input.text())
                    float(Tmax_input.text())
                data_manager.set_plot_defaults({
                    "auto_plot": auto_plot_checkbox.isChecked(),
                    "x_custom": float(x_custom_input.text()) if x_custom_input.text() else None,
                    "Tmin": float(Tmin_input.text()) if Tmin_input.text() else None,
                    "Tmax": float(Tmax_input.text()) if Tmax_input.text() else None
                })
                QMessageBox.information(dialog, "Success", "Default plot configuration saved successfully.")
                dialog.accept()
            except ValueError:
                QMessageBox.warning(dialog, "Invalid Input", "Please enter valid numeric values for custom inputs.")
        
        ok_button.clicked.connect(save_defaults)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec_()


    def save_data(self):
        """
        Saves the stored input data (data_manager.data_store) to a text file in JSON format.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save Input Data", "", "Text Files (*.txt)")
        if not filename:
            return
        if not filename.lower().endswith(".txt"):
            filename += ".txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data_manager.data_store, f, indent=4)
            QMessageBox.information(self, "Save Successful", f"Input data saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data:\n{e}")

    def load_data(self):
        """
        Loads stored input data from a JSON text file and updates the DataManager.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Open Input Data", "", "Text Files (*.txt)")
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            data_manager.data_store = data
            QMessageBox.information(self, "Load Successful", f"Input data loaded from {filename}")
            # Update Save action
            self.save_action.setEnabled(bool(data_manager.get_ids()))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{e}")

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

    def configure_analytical_input(self):
        geometry_dialog = GeometrySelectionDialog()
        if geometry_dialog.exec():
            geometry, d, id_ = geometry_dialog.get_geometry_and_d()
            if geometry is None:
                return
            print("Geometry selected:", geometry, "d:", d, "ID:", id_)  # Debug print
            parameter_dialog = ParameterInputDialog(geometry)
            
            # Se o ID já existir, pré-preenche os parâmetros.
            stored = data_manager.get_data(id_)
            if stored:
                if "parameters" in stored:
                    parameter_dialog.set_parameters(stored["parameters"])
                else:
                    parameter_dialog.set_parameters(stored)
            else:
                # Para novo ID, forçamos a carregar os defaults de plot do DataManager
                # (passando um dicionário vazio para set_parameters, assim ele ignorará os parâmetros e
                # buscará os defaults do DataManager).
                parameter_dialog.set_parameters({})
            
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

                    # Armazena ou atualiza os dados usando o DataManager, armazenando o dicionário completo.
                    data_manager.add_or_update_data(self.parameters["id"], self.data['geometry'], self.data['d'], self.parameters)
                    print(f"Model with ID '{self.parameters['id']}' stored successfully.")
                    self.save_action.setEnabled(True)
                # Outros métodos, se houver...
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while running the model:\n{e}")
        else:
            QMessageBox.warning(self, "No Data", "Please enter input data before running the model.")

    def clear_inputs(self):
        self.parameters = None
        self.data = {}
        self.results = None
        self.run_button.setEnabled(False)
        self.run_button.setStyleSheet("font-size: 18px; padding: 10px; color: gray;")
        self.visualize_button.setEnabled(False)
        self.visualize_button.setStyleSheet("font-size: 18px; padding: 10px; color: gray;")
        self.clear_button.setVisible(False)
        self.input_button.setEnabled(False)

        self.status_label.setText("Clearing data input...")
        QApplication.processEvents()
        QTimer.singleShot(1000, self._clear_inputs_done)

    def _clear_inputs_done(self):
        self.status_label.setText("Data input cleared")
        self.input_button.setEnabled(True)
        QTimer.singleShot(1000, lambda: self.status_label.setText(""))

    def visualizeResults(self):
        if self.results:
            self.visualization.set_data(self.results, self.data.get("geometry", "Unknown"))
            self.visualization.set_id(self.data.get("id", "Unknown"))
            
            # Define the graph configuration (manual or automatic)
            self.visualization.plot_config = {
                "auto_plot": self.parameters.get("auto_plot", True),
                "x_custom": self.parameters.get("x_custom", None),
                "Tmin": self.parameters.get("Tmin", None),
                "Tmax": self.parameters.get("Tmax", None)
            }
            
            self.visualization.show()
        else:
            QMessageBox.warning(self, "No Results", "Run the thermal model before visualizing results.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
