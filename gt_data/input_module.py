from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt

class GeometrySelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Geometry and Parameters")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QFormLayout()

        self.id_input = QLineEdit()

        self.geometry_input = QComboBox()
        self.geometry_input.addItems(["Tabular-like body", "Spheric-like body", "Plug-like body"])
        self.geometry_input.currentIndexChanged.connect(self.update_d_visibility)

        # Initially define ok_button as None so that check_inputs() can check its existence
        self.ok_button = None

        # Create label and input for "d" without setting texto ainda
        self.d_label = QLabel()
        self.d_input = QLineEdit()
        self.d_input.textChanged.connect(self.check_inputs)
        self.id_input.textChanged.connect(self.check_inputs)

        # Add rows to the layout
        self.layout.addRow("Enter ID:", self.id_input)
        self.layout.addRow("Select the geometry:", self.geometry_input)
        self.layout.addRow(self.d_label, self.d_input)

        # Now define ok_button and add it to the layout
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)  # Initially disabled
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

        # Call update_d_visibility AFTER all widgets are created
        self.update_d_visibility()

    def update_d_visibility(self):
        """
        Update the label text for the 'd' input field according to the selected geometry.
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
        
        # Ensure that the label and input are visible
        self.d_label.setVisible(True)
        self.d_input.setVisible(True)
        self.check_inputs()

    def check_inputs(self):
        """
        Validate that the ID field is non-empty and that 'd' is a valid number greater than zero.
        Enables the OK button if valid.
        """
        id_text = self.id_input.text().strip()
        d_text = self.d_input.text().strip()
        if id_text and self.is_valid_number(d_text) and float(d_text) > 0:
            if self.ok_button is not None:
                self.ok_button.setEnabled(True)
        else:
            if self.ok_button is not None:
                self.ok_button.setEnabled(False)

    def is_valid_number(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def get_geometry_and_d(self):
        geometry = self.geometry_input.currentText()
        d = float(self.d_input.text()) if self.d_input.text() else None
        return geometry, d, self.id_input.text().strip()

class ParameterInputDialog(QDialog):
    def __init__(self, geometry):
        super().__init__()
        self.setWindowTitle("Enter Parameters")
        self.setGeometry(100, 100, 400, 400)

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

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        # Connect textChanged signals for validation
        for input_field in self.inputs:
            input_field.textChanged.connect(self.check_inputs)

    def check_inputs(self):
        """
        Validates that all visible fields are filled and contain valid numbers,
        and that each time value (separated by semicolons) is non-zero.
        """
        all_filled = all(input_field.text().strip() for input_field in self.inputs if input_field.isVisible())
        all_valid = all(self.is_valid_number(input_field.text()) for input_field in self.inputs[:-1] if input_field.isVisible())
        time_text = self.time_input.text()
        time_values = [t.strip() for t in time_text.split(';') if t.strip()]
        try:
            all_times_valid = all(float(t) != 0 for t in time_values)
        except ValueError:
            all_times_valid = False

        self.ok_button.setEnabled(all_filled and all_valid and all_times_valid)

    def is_valid_number(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def get_parameters(self):
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
            "time": times
        }
        return parameters
