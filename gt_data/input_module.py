from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt

class GeometrySelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Geometry")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()
        self.geometry_input = QComboBox()
        self.geometry_input.addItems(["Tabular-like body", "Spheric-like body", "Plug-like body"])

        layout.addWidget(QLabel("Select the geometry:"))
        layout.addWidget(self.geometry_input)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_geometry(self):
        return self.geometry_input.currentText()

class ParameterInputDialog(QDialog):
    def __init__(self, geometry):
        super().__init__()
        self.setWindowTitle("Enter Parameters")
        self.setGeometry(100, 100, 400, 300)

        layout = QFormLayout()
        self.geometry = geometry

        self.T0_input = QLineEdit()
        self.K1_input = QLineEdit()
        self.k_input = QLineEdit()
        self.K_input = QLineEdit()
        self.k1_input = QLineEdit()
        self.g_input = QLineEdit()
        self.l_input = QLineEdit()

        self.inputs = [
            self.T0_input,
            self.K1_input,
            self.k_input,
            self.K_input,
            self.k1_input,
            self.g_input,
            self.l_input
        ]

        layout.addRow("Initial Temperature of Magma (T0):", self.T0_input)
        layout.addRow("Thermal Conductivity of Solidified Magma (K1):", self.K1_input)
        layout.addRow("Diffusivity of Country Rock (k):", self.k_input)
        layout.addRow("Thermal Conductivity of Country Rock (K):", self.K_input)
        layout.addRow("Diffusivity of Solidified Magma (k1):", self.k1_input)
        layout.addRow("Thermal Gradient (g):", self.g_input)
        layout.addRow("Depth (l):", self.l_input)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        # Conectar sinais de mudança de texto
        for input_field in self.inputs:
            input_field.textChanged.connect(self.check_inputs)

    def check_inputs(self):
        all_filled = all(input_field.text().strip() and input_field.text().strip().replace('.', '', 1).isdigit() for input_field in self.inputs)
        self.ok_button.setEnabled(all_filled)

    def get_parameters(self):
        return {
            "geometry": self.geometry,
            "T0": float(self.T0_input.text()),
            "K1": float(self.K1_input.text()),
            "k": float(self.k_input.text()),
            "K": float(self.K_input.text()),
            "k1": float(self.k1_input.text()),
            "g": float(self.g_input.text()),
            "l": float(self.l_input.text())
        }
