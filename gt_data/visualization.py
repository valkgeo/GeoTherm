from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
import matplotlib.pyplot as plt

class Visualization(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Model Results")
        self.setGeometry(100, 100, 800, 600)
        self.id = ""

    def set_data(self, results):
        self.results = results

    def set_id(self, id_):
        self.id = id_

    def show(self):
        self.plot_results()

    def plot_results(self):
        if hasattr(self, 'results') and self.results is not None:
            plt.figure()
            for time, (x, T) in self.results.items():
                plt.plot(x, T, label=f"Time = {time} years")
            plt.xlabel("Distance from center (m)")
            plt.ylabel("Temperature (°C)")
            plt.title(f"Thermal Modeling for Spheric-like {self.id} body")
            plt.legend()
            plt.show()
