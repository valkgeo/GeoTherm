from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Visualization(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Visualization")
        self.setGeometry(100, 100, 600, 400)
        
        self.data = None
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)
        
        self.ax = self.canvas.figure.add_subplot(111)
        
        self.setLayout(layout)
    
    def set_data(self, data):
        self.data = data
        self.update_plot()
    
    def update_plot(self):
        if self.data:
            x, T = self.data
            self.ax.clear()
            self.ax.plot(x, T, marker='o')
            self.ax.set_xlabel('Position (m)')
            self.ax.set_ylabel('Temperature (C)')
            self.ax.set_title('Temperature Distribution')
            self.canvas.draw()
