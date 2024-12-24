import numpy as np
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PaintGridDialog(QDialog):
    """Dialog to allow the user to paint the magmatic area on the grid."""
    def __init__(self, grid, nx, ny):
        super().__init__()
        self.setWindowTitle("Paint Magmatic Body")
        self.setGeometry(200, 200, 800, 800)
        self.grid = grid
        self.nx = nx
        self.ny = ny
        self.magmatic_area = np.zeros((nx, ny), dtype=int)  # Default: No magmatic body

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        info_label = QLabel("Click on the grid to paint the magmatic body. Use the clear button to reset.")
        layout.addWidget(info_label)

        # Create matplotlib figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Buttons for clearing and completing painting
        button_layout = QVBoxLayout()
        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_paint)
        button_layout.addWidget(clear_button)

        done_button = QPushButton("Done", self)
        done_button.clicked.connect(self.accept)
        button_layout.addWidget(done_button)

        layout.addLayout(button_layout)

        # Draw the initial grid
        self.plot_grid()

        # Connect mouse click events to the canvas
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def plot_grid(self):
        """Draw the grid and painted cells."""
        ax = self.figure.add_subplot(111)
        ax.clear()

        # Draw grid lines
        ax.set_xticks(np.arange(0, self.nx, max(1, self.nx // 10)))
        ax.set_yticks(np.arange(0, self.ny, max(1, self.ny // 10)))
        ax.tick_params(labelsize=8)

        ax.set_xticks(np.arange(-0.5, self.nx, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.ny, 1), minor=True)
        ax.grid(which="minor", color="gray", linestyle="-", linewidth=0.5)

        # Highlight painted cells
        ax.imshow(self.magmatic_area, cmap="Reds", origin="upper", extent=(-0.5, self.nx - 0.5, -0.5, self.ny - 0.5))

        # Set limits and aspect ratio
        ax.set_xlim(-0.5, self.nx - 0.5)
        ax.set_ylim(-0.5, self.ny - 0.5)
        ax.set_aspect("equal")
        ax.set_xlabel("Grid X")
        ax.set_ylabel("Grid Y")

        self.canvas.draw()

    def on_click(self, event):
        """Handle mouse clicks on the grid."""
        if event.inaxes is not None:
            self.toggle_cell(event)

    def on_drag(self, event):
        """Handle mouse drag events to paint multiple cells."""
        if event.inaxes is not None and event.button == 1:  # Left button drag
            self.toggle_cell(event)

    def toggle_cell(self, event):
        """Toggle the state of a cell on the grid."""
        ix, iy = int(np.floor(event.xdata + 0.5)), int(np.floor(event.ydata + 0.5))
        if 0 <= ix < self.nx and 0 <= iy < self.ny:
            self.magmatic_area[iy, ix] = 1
            self.plot_grid()

    def clear_paint(self):
        """Clear all painted cells."""
        self.magmatic_area.fill(0)
        self.plot_grid()

    def get_magmatic_area(self):
        """Return the painted magmatic area."""
        return self.magmatic_area
