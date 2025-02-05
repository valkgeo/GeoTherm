from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, 
    QInputDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
from gt_data.data_manager import data_manager  

class GeometrySelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Geometry and Parameters")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QFormLayout()

        # Create an editable QComboBox for IDs.
        self.id_input = QComboBox()
        self.id_input.setEditable(True)
        # Add the default option and the stored IDs.
        self.id_input.addItem("<NEW ID>")
        self.id_input.addItems(data_manager.get_ids())
        # Initially, the field is empty.
        self.id_input.setCurrentText("")
        self.id_input.currentTextChanged.connect(self.on_id_changed)
        self.id_input.lineEdit().textEdited.connect(self.on_text_edited)

        self.geometry_input = QComboBox()
        self.geometry_input.addItems(["Tabular-like body", "Spheric-like body", "Plug-like body"])
        self.geometry_input.currentIndexChanged.connect(self.update_d_visibility)

        self.d_label = QLabel()
        self.d_input = QLineEdit()
        self.d_input.textChanged.connect(self.check_inputs)

        self.layout.addRow("Select or Enter ID:", self.id_input)
        self.layout.addRow("Select the geometry:", self.geometry_input)
        self.layout.addRow(self.d_label, self.d_input)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)
        self.update_d_visibility()

    def update_id_list(self):
        """
        Updates the ID combo box with the latest IDs from data_manager.
        The first item remains "<NEW ID>".
        """
        current_text = self.id_input.currentText()
        self.id_input.clear()
        self.id_input.addItem("<NEW ID>")
        for stored_id in data_manager.get_ids():
            self.id_input.addItem(stored_id)
        if current_text and current_text != "<NEW ID>":
            index = self.id_input.findText(current_text, Qt.MatchFixedString)
            if index >= 0:
                self.id_input.setCurrentIndex(index)
            else:
                self.id_input.setCurrentText("")
        else:
            self.id_input.setCurrentText("")

    def on_id_changed(self, selected_id):
        """
        If the user selects "<NEW ID>", clear the field so a new ID can be entered.
        Otherwise, load the stored data for the selected ID to pre-populate the fields.
        """
        if selected_id == "":
            return
        if selected_id == "<NEW ID>":
            self.id_input.setEditText("")
            self.id_input.setToolTip("Please enter a new ID here.")
            self.d_input.clear()
        else:
            self.id_input.setToolTip("")
            data = data_manager.get_data(selected_id)
            if data:
                geometry = data.get("geometry", "")
                d = data.get("d", "")
                self.geometry_input.setCurrentText(geometry)
                self.d_input.setText(str(d))
                self.update_d_visibility()
        self.check_inputs()

    def on_text_edited(self, text):
        """
        When the user edits the ID field, if the text is "<NEW ID>",
        show a tooltip indicating that the user should clear it.
        """
        if text == "<NEW ID>":
            self.id_input.setToolTip("Please clear '<NEW ID>' to enter a new ID.")
        else:
            self.id_input.setToolTip("")

    def update_d_visibility(self):
        """
        Updates the label for the 'd' input based on the selected geometry.
        """
        geometry = self.geometry_input.currentText()
        if geometry == "Spheric-like body":
            self.d_label.setText("Enter the radius (d) of the sphere:")
        elif geometry == "Tabular-like body":
            self.d_label.setText("Enter half the width (d) of the heated area (-d < x < d):")
        elif geometry == "Plug-like body":
            self.d_label.setText("Enter the radius (d) of the cylindrical plug:")
        else:
            self.d_label.setText("Enter the characteristic dimension (d):")
        self.d_label.setVisible(True)
        self.d_input.setVisible(True)
        self.check_inputs()

    def check_inputs(self):
        """
        Validates that the ID field is not empty or equal to "<NEW ID>" 
        and that 'd' is a valid number greater than zero.
        Enables the OK button if valid.
        """
        id_text = self.id_input.currentText().strip()
        d_text = self.d_input.text().strip()

        is_id_valid = (id_text != "" and id_text != "<NEW ID>")
        is_d_valid = self.is_valid_number(d_text) and float(d_text) > 0

        self.ok_button.setEnabled(is_id_valid and is_d_valid)

    def is_valid_number(self, text):
        """
        Returns True if the given text can be converted to a float.
        """
        try:
            float(text)
            return True
        except ValueError:
            return False

    def get_geometry_and_d(self):
        """
        Returns the selected geometry, the 'd' value, and the ID.
        If the ID is "<NEW ID>" or empty, prompts the user for a new ID.
        If the new ID already exists, warns the user and returns (None, None, None).
        """
        geometry = self.geometry_input.currentText()
        d = float(self.d_input.text()) if self.d_input.text() else None
        selected_id = self.id_input.currentText().strip()

        if selected_id == "" or selected_id == "<NEW ID>":
            new_id, ok = QInputDialog.getText(self, "Enter New ID", "Enter a unique ID:")
            if not ok or not new_id.strip():
                QMessageBox.warning(self, "Invalid ID", "ID cannot be empty.")
                return None, None, None
            if data_manager.id_exists(new_id):
                QMessageBox.warning(self, "ID Exists", "This ID already exists. Please choose another.")
                return None, None, None
            return geometry, d, new_id.strip()
        else:
            return geometry, d, selected_id


class ParameterInputDialog(QDialog):
    def __init__(self, geometry):
        super().__init__()
        self.setWindowTitle("Enter Parameters")
        self.setGeometry(100, 100, 400, 500)
        layout = QFormLayout()
        self.geometry = geometry

        self.T0_input = QLineEdit()
        self.K1_input = QLineEdit()
        self.k_input = QLineEdit()
        self.K_input = QLineEdit()
        self.k1_input = QLineEdit()
        self.g_input = QLineEdit()
        self.l_input = QLineEdit()
        self.time_input = QLineEdit()
        # Default value for times
        self.time_input.setText("1;10;100;1000;10000;100000;1000000;5000000;10000000")

        self.inputs = [
            self.T0_input,
            self.K1_input,
            self.k_input,
            self.K_input,
            self.k1_input,
            self.g_input,
            self.l_input,
            self.time_input
        ]

        layout.addRow("Initial Temperature of Magma (T0):", self.T0_input)
        layout.addRow("Thermal Conductivity of Solidified Magma (K1):", self.K1_input)
        layout.addRow("Diffusivity of Country Rock (k):", self.k_input)
        layout.addRow("Thermal Conductivity of Country Rock (K):", self.K_input)
        layout.addRow("Diffusivity of Solidified Magma (k1):", self.k1_input)
        layout.addRow("Thermal Gradient (g):", self.g_input)
        layout.addRow("Depth (l):", self.l_input)
        layout.addRow("Times (semicolon separated):", self.time_input)

        # Plot configuration section
        self.auto_plot_checkbox = QCheckBox("Auto-plot configuration")
        # Carrega os defaults de plot do DataManager.
        plot_defaults = data_manager.get_plot_defaults()
        auto_plot_default = plot_defaults.get("auto_plot", True)
        self.auto_plot_checkbox.setChecked(auto_plot_default)
        self.auto_plot_checkbox.toggled.connect(self.toggle_plot_config_fields)
        layout.addRow(self.auto_plot_checkbox)

        # Create custom plot configuration fields with descriptive labels.
        self.x_custom_label = QLabel("Distance to mid-intrusion (plot half-range):")
        self.x_custom_input = QLineEdit()
        self.x_custom_input.setPlaceholderText("Enter distance for plot x-axis")
        layout.addRow(self.x_custom_label, self.x_custom_input)

        self.Tmin_label = QLabel("Minimum temperature (plot y-axis):")
        self.Tmin_input = QLineEdit()
        self.Tmin_input.setPlaceholderText("Enter minimum temperature for plot")
        layout.addRow(self.Tmin_label, self.Tmin_input)

        self.Tmax_label = QLabel("Maximum temperature (plot y-axis):")
        self.Tmax_input = QLineEdit()
        self.Tmax_input.setPlaceholderText("Enter maximum temperature for plot")
        layout.addRow(self.Tmax_label, self.Tmax_input)

        # Se o default auto_plot for True, os campos customizados são ocultos.
        if auto_plot_default:
            self.x_custom_label.hide()
            self.x_custom_input.hide()
            self.Tmin_label.hide()
            self.Tmin_input.hide()
            self.Tmax_label.hide()
            self.Tmax_input.hide()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        # Connect signals for validation.
        for input_field in self.inputs:
            input_field.textChanged.connect(self.check_inputs)
        self.x_custom_input.textChanged.connect(self.check_inputs)
        self.Tmin_input.textChanged.connect(self.check_inputs)
        self.Tmax_input.textChanged.connect(self.check_inputs)

    def toggle_plot_config_fields(self, checked):
        """
        Shows or hides the custom plot configuration fields based on the checkbox state.
        """
        if checked:  # Auto-plot enabled: hide custom fields.
            self.x_custom_label.hide()
            self.x_custom_input.hide()
            self.Tmin_label.hide()
            self.Tmin_input.hide()
            self.Tmax_label.hide()
            self.Tmax_input.hide()
        else:  # Auto-plot disabled: show custom fields.
            self.x_custom_label.show()
            self.x_custom_input.show()
            self.Tmin_label.show()
            self.Tmin_input.show()
            self.Tmax_label.show()
            self.Tmax_input.show()
        try:
            data_manager.set_plot_defaults({
                "auto_plot": self.auto_plot_checkbox.isChecked(),
                "x_custom": float(self.x_custom_input.text()) if self.x_custom_input.text() else None,
                "Tmin": float(self.Tmin_input.text()) if self.Tmin_input.text() else None,
                "Tmax": float(self.Tmax_input.text()) if self.Tmax_input.text() else None
            })
        except ValueError:
            pass

        self.check_inputs()

    def set_parameters(self, parameters):
        """Fills the fields with stored parameters and loads plot defaults from DataManager."""
        self.T0_input.setText(str(parameters.get("T0", "")))
        self.K1_input.setText(str(parameters.get("K1", "")))
        self.k_input.setText(str(parameters.get("k", "")))
        self.K_input.setText(str(parameters.get("K", "")))
        self.k1_input.setText(str(parameters.get("k1", "")))
        self.g_input.setText(str(parameters.get("g", "")))
        self.l_input.setText(str(parameters.get("l", "")))
        self.time_input.setText(";".join(map(str, parameters.get("time", []))))
        
        # Load plot defaults from DataManager (ignoring any plot-related keys in 'parameters')
        plot_defaults = data_manager.get_plot_defaults()
        print("DEBUG: Loaded plot_defaults from DataManager:", plot_defaults)  # Debug print
        auto_plot_default = plot_defaults.get("auto_plot", True)
        self.auto_plot_checkbox.setChecked(auto_plot_default)
        if not auto_plot_default:
            # Se os defaults estiverem definidos, preenche os campos customizados.
            x_custom = plot_defaults.get("x_custom", "")
            Tmin = plot_defaults.get("Tmin", "")
            Tmax = plot_defaults.get("Tmax", "")
            print("DEBUG: Setting custom plot fields: x_custom =", x_custom, "Tmin =", Tmin, "Tmax =", Tmax)  # Debug
            self.x_custom_input.setText(str(x_custom) if x_custom is not None else "")
            self.Tmin_input.setText(str(Tmin) if Tmin is not None else "")
            self.Tmax_input.setText(str(Tmax) if Tmax is not None else "")
        else:
            # Se auto-plot estiver ativado, limpa os campos customizados.
            self.x_custom_input.setText("")
            self.Tmin_input.setText("")
            self.Tmax_input.setText("")
        self.toggle_plot_config_fields(self.auto_plot_checkbox.isChecked())

    def check_inputs(self):
        """
        Validates that all visible fields are filled and contain valid numbers.
        """
        all_filled = all(input_field.text().strip() for input_field in self.inputs if input_field.isVisible())
        all_valid = all(self.is_valid_number(input_field.text()) for input_field in self.inputs[:-1] if input_field.isVisible())

        time_text = self.time_input.text()
        time_values = [t.strip() for t in time_text.split(';') if t.strip()]
        try:
            all_times_valid = all(float(t) != 0 for t in time_values)
        except ValueError:
            all_times_valid = False

        if not self.auto_plot_checkbox.isChecked():
            extra_filled = (self.x_custom_input.text().strip() != "" and 
                            self.Tmin_input.text().strip() != "" and 
                            self.Tmax_input.text().strip() != "")
            extra_valid = (self.is_valid_number(self.x_custom_input.text()) and
                           self.is_valid_number(self.Tmin_input.text()) and
                           self.is_valid_number(self.Tmax_input.text()))
        else:
            extra_filled = True
            extra_valid = True

        self.ok_button.setEnabled(all_filled and all_valid and all_times_valid and extra_filled and extra_valid)

    def is_valid_number(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def get_parameters(self):
        """Returns the parameters entered by the user."""
        times = [float(t.strip()) for t in self.time_input.text().split(';') if t.strip()]
        parameters = {
            "geometry": self.geometry,
            "T0": float(self.T0_input.text()),
            "K1": float(self.K1_input.text()),
            "k": float(self.k_input.text()),
            "K": float(self.K_input.text()),
            "k1": float(self.k1_input.text()),
            "g": float(self.g_input.text()),
            "l": float(self.l_input.text()),
            "time": times,
        }
        parameters["auto_plot"] = self.auto_plot_checkbox.isChecked()
        if not parameters["auto_plot"]:
            parameters["x_custom"] = float(self.x_custom_input.text())
            parameters["Tmin"] = float(self.Tmin_input.text())
            parameters["Tmax"] = float(self.Tmax_input.text())
        return parameters
