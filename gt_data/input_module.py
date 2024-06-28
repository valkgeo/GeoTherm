from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QComboBox

class InputModule(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Input Data")
        self.setGeometry(100, 100, 400, 300)
        
        self.data = {}
        self.initUI()
    
    def initUI(self):
        layout = QFormLayout()
        
        self.geometry_input = QComboBox(self)
        self.geometry_input.addItems(["Tabular-like body", "Plug-like body", "Spheric-like body"])
        self.k_input = QLineEdit(self)
        self.L_input = QLineEdit(self)
        self.A_input = QLineEdit(self)
        self.T0_input = QLineEdit(self)
        self.T1_input = QLineEdit(self)
        
        layout.addRow("Geometry", self.geometry_input)
        layout.addRow("Thermal Conductivity (k)", self.k_input)
        layout.addRow("Length (L)", self.L_input)
        layout.addRow("Area (A)", self.A_input)
        layout.addRow("Temperature at left end (T0)", self.T0_input)
        layout.addRow("Temperature at right end (T1)", self.T1_input)
        
        submit_button = QPushButton("Submit", self)
        submit_button.clicked.connect(self.submit_data)
        layout.addWidget(submit_button)
        
        self.setLayout(layout)
    
    def submit_data(self):
        self.data['geometry'] = self.geometry_input.currentText()
        self.data['k'] = float(self.k_input.text())
        self.data['L'] = float(self.L_input.text())
        self.data['A'] = float(self.A_input.text())
        self.data['T0'] = float(self.T0_input.text())
        self.data['T1'] = float(self.T1_input.text())
        self.accept()
    
    def get_data(self):
        return self.data
