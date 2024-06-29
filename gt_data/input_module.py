from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox
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

        self.d_label = QLabel("Half Diameter of Sphere (d):")
        self.d_label.setVisible(False)  # Inicialmente oculto

        self.d_input = QLineEdit()
        self.d_input.setVisible(False)  # Inicialmente oculto
        self.d_input.textChanged.connect(self.check_inputs)  # Conectar para validar o input
        self.id_input.textChanged.connect(self.check_inputs)

        self.layout.addRow("Enter ID:", self.id_input)
        self.layout.addRow("Select the geometry:", self.geometry_input)
        self.layout.addRow(self.d_label, self.d_input)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)  # Inicialmente desabilitado
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

    def update_d_visibility(self):
        geometry = self.geometry_input.currentText()
        if geometry == "Spheric-like body":
            self.d_label.setVisible(True)
            self.d_input.setVisible(True)
            self.check_inputs()  # Verifica o input ao exibir o campo
        else:
            self.d_label.setVisible(False)
            self.d_input.setVisible(False)
            self.check_inputs()

    def check_inputs(self):
        id_text = self.id_input.text().strip()
        if self.geometry_input.currentText() == "Spheric-like body":
            d_text = self.d_input.text().strip()
            if self.is_valid_number(d_text) and float(d_text) > 0 and id_text:
                self.ok_button.setEnabled(True)
            else:
                self.ok_button.setEnabled(False)
        else:
            self.ok_button.setEnabled(bool(id_text))

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

        # Conectar sinais de mudança de texto
        for input_field in self.inputs:
            input_field.textChanged.connect(self.check_inputs)

    def check_inputs(self):
        all_filled = all(input_field.text().strip() for input_field in self.inputs if input_field.isVisible())
        all_valid = all(self.is_valid_number(input_field.text()) for input_field in self.inputs[:-1] if input_field.isVisible())  # Exceto time_input
        all_valid &= all(float(t.strip()) != 0 for t in self.time_input.text().split(';') if t.strip())  # Verifica se todos os tempos são diferentes de zero
        self.ok_button.setEnabled(all_filled and all_valid)

    def is_valid_number(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def get_parameters(self):
        times = [float(t.strip()) for t in self.time_input.text().split(';')]
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