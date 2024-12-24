import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import numpy as np
from grid_painter import PaintGridDialog


def run_numerical_modelling():
    app = QApplication(sys.argv)
    numerical_dialog = NumericalModelingDialog()
    numerical_dialog.exec()
    sys.exit(app.exec_())


class NumericalModelingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Numerical Modeling Configuration")
        self.setGeometry(100, 100, 600, 400)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        grid_x_label = QLabel("Enter number of grid points in X:")
        layout.addWidget(grid_x_label)

        self.grid_x_input = QLineEdit(self)
        self.grid_x_input.setPlaceholderText("e.g., 50")
        layout.addWidget(self.grid_x_input)

        grid_y_label = QLabel("Enter number of grid points in Y:")
        layout.addWidget(grid_y_label)

        self.grid_y_input = QLineEdit(self)
        self.grid_y_input.setPlaceholderText("e.g., 50")
        layout.addWidget(self.grid_y_input)

        configure_button = QPushButton("Configure Grid")
        configure_button.clicked.connect(self.configure_grid)
        layout.addWidget(configure_button)

    def configure_grid(self):
        try:
            nx = int(self.grid_x_input.text())
            ny = int(self.grid_y_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Grid dimensions must be integers.")
            return

        if nx > 500 or ny > 500:
            QMessageBox.warning(self, "Large Grid", "The grid is very large and may affect performance.")

        # Create and open the grid painting dialog
        default_grid = np.zeros((nx, ny))
        paint_dialog = PaintGridDialog(default_grid, nx, ny)
        if paint_dialog.exec():
            magmatic_area = paint_dialog.get_magmatic_area()
            QMessageBox.information(self, "Grid Configured", "Magmatic body configured successfully.")
            print("Magmatic Area:\n", magmatic_area)
