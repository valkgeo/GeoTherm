import os
import time
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

import win32com.client  # For COM automation if needed (not used in PDF saving)
from PyQt5.QtCore import pyqtSignal, Qt, QBuffer, QIODevice
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QGridLayout, QMessageBox, QInputDialog
)

class ClickableLabel(QLabel):
    """
    QLabel subclass that emits a signal when clicked.
    """
    clicked = pyqtSignal(int)

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)

def figure_to_pixmap(fig, width=200, height=200):
    """
    Converts a matplotlib figure to a QPixmap thumbnail.

    Parameters:
        fig (matplotlib.figure.Figure): The figure to convert.
        width (int): The desired thumbnail width.
        height (int): The desired thumbnail height.

    Returns:
        QPixmap: The resulting thumbnail pixmap.
    """
    # Ensure the figure has square proportions
    fig.set_size_inches(2, 2)
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    canvas = FigureCanvas(fig)
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    canvas.print_png(buffer)
    data = buffer.data()
    pixmap = QPixmap()
    pixmap.loadFromData(data, "PNG")
    pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    buffer.close()
    return pixmap

class Visualization(QDialog):
    next_input_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Model Results")
        self.setGeometry(100, 100, 800, 600)
        # Initialize user ID, geometry type, and results.
        self.id = ""
        self.geom_type = ""
        self.results = None

        # List to store plots (up to 9).
        self.stored_plots = []
        self.grid_rows = 3  # Default rows for grid preview
        self.grid_cols = 3  # Default columns for grid preview

        # Main layout with buttons and preview grid.
        layout = QVBoxLayout()
        self.info_label = QLabel(
            "Options: Show Plot, Save Plot as PDF, Store Plot, Clear Grid, Save Grid as PDF."
        )
        layout.addWidget(self.info_label)

        # Preview grid layout for thumbnails.
        self.preview_layout = QGridLayout()
        layout.addLayout(self.preview_layout)

        # Control buttons.
        self.show_button = QPushButton("Show Plot")
        self.show_button.clicked.connect(self.plot_results)
        layout.addWidget(self.show_button)

        self.store_button = QPushButton("Store Plot")
        self.store_button.clicked.connect(self.store_plot)
        layout.addWidget(self.store_button)

        self.clear_grid_button = QPushButton("Clear Grid")
        self.clear_grid_button.clicked.connect(self.clear_grid)
        layout.addWidget(self.clear_grid_button)

        self.save_grid_button = QPushButton("Save Grid as PDF")
        self.save_grid_button.clicked.connect(self.save_grid_as_pdf)
        layout.addWidget(self.save_grid_button)

        self.next_input_button = QPushButton("Next Input")
        self.next_input_button.clicked.connect(self.next_input)
        self.next_input_button.setVisible(False)
        layout.addWidget(self.next_input_button)

        self.setLayout(layout)
        self.update_preview()
        self.update_store_button_text()

    def set_data(self, results, geom_type):
        """
        Sets the model results and the geometry type.

        Parameters:
            results (dict): Dictionary containing the model results.
                For 1D data: {time: (x, T)}
                For 2D data: {time: (X, Y, T)}
            geom_type (str): The type of geometry chosen (e.g., "Spheric-like body", "Tabular-like body", "Plug-like body").
        """
        self.results = results
        self.geom_type = geom_type

    def set_id(self, id_):
        """
        Sets the user-provided ID.

        Parameters:
            id_ (str): The identifier entered by the user.
        """
        self.id = id_

    def plot_results(self):
        """
        Displays the thermal model results using matplotlib.
        
        If each result tuple has 2 elements, a 1D line plot is produced.
        If it has 3 elements (X, Y, T), a contour plot is produced for each time.
        """
        if self.results is None:
            return

        sample = next(iter(self.results.values()))
        # Check if results are 1D (tuple with 2 elements) or 2D (tuple with 3 elements)
        if len(sample) == 2:
            # 1D case
            fig, ax = plt.subplots()
            for t, (x, T) in self.results.items():
                ax.plot(x, T, label=f"Time = {t} years")
            ax.set_xlabel("Distance from center (m)")
            ax.set_ylabel("Temperature (°C)")
            ax.set_title(f"Thermal modeling for {self.id} {self.geom_type}")
            ax.legend()
            plt.tight_layout()
            plt.show(block=False)
        elif len(sample) == 3:
            # 2D case: create subplots for each time
            num_plots = len(self.results)
            cols = int(np.ceil(np.sqrt(num_plots)))
            rows = int(np.ceil(num_plots / cols))
            fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3))
            axes = np.array(axes).flatten()
            for i, (t, (X, Y, T)) in enumerate(self.results.items()):
                ax = axes[i]
                cp = ax.contourf(X, Y, T, levels=20, cmap="viridis")
                fig.colorbar(cp, ax=ax)
                ax.set_title(f"Time = {t} years")
                ax.set_xlabel("x (m)")
                ax.set_ylabel("y (m)")
            # Turn off extra subplots if necessary
            for j in range(i+1, len(axes)):
                axes[j].axis('off')
            fig.suptitle(f"Thermal modeling for {self.id} {self.geom_type}", fontsize=16)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.show(block=False)
        else:
            print("Unexpected result format.")

    def save_plot_as_pdf(self):
        """
        Saves the current plot to a PDF file.

        A file dialog opens so that the user can choose where to save the PDF.
        """
        if self.results is None:
            print("No results to save.")
            return

        initial_directory = os.getcwd()
        pdf_filename, _ = QFileDialog.getSaveFileName(
            self, "Save Plot as PDF", initial_directory, "PDF Files (*.pdf)"
        )
        if not pdf_filename:
            print("Save cancelled by user.")
            return
        if not pdf_filename.lower().endswith(".pdf"):
            pdf_filename += ".pdf"
        pdf_filename = os.path.abspath(pdf_filename)

        fig, ax = plt.subplots()
        sample = next(iter(self.results.values()))
        if len(sample) == 2:
            for t, (x, T) in self.results.items():
                ax.plot(x, T, label=f"Time = {t} years")
            ax.set_xlabel("Distance from center (m)")
            ax.set_ylabel("Temperature (°C)")
            ax.set_title(f"Thermal modeling for {self.id} {self.geom_type}")
            ax.legend()
        else:
            ax.text(0.5, 0.5, "2D plot - use Save Grid as PDF", ha="center", va="center")
        plt.tight_layout()
        fig.savefig(pdf_filename, format="pdf")
        plt.close(fig)
        print(f"Plot saved as {pdf_filename}.")

    def create_placeholder(self):
        """
        Creates a placeholder figure to indicate an empty slot.

        Returns:
            matplotlib.figure.Figure: A placeholder figure.
        """
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.text(0.5, 0.5, "Placeholder", fontsize=12, ha="center", va="center", color="gray")
        ax.axis("off")
        return fig

    def is_placeholder(self, fig):
        """
        Checks if the given figure is a placeholder by looking for the text "Placeholder".

        Parameters:
            fig (matplotlib.figure.Figure): The figure to check.

        Returns:
            bool: True if the figure is a placeholder, otherwise False.
        """
        try:
            texts = [txt.get_text() for txt in fig.axes[0].texts]
            return "Placeholder" in texts
        except Exception:
            return False

    def manage_placeholder(self):
        """
        Automatically manages the placeholder:
         - If there is exactly one real plot stored, ensure that a placeholder is appended.
         - Otherwise, remove any placeholder.
        """
        real_plots = [fig for fig in self.stored_plots if not self.is_placeholder(fig)]
        if len(real_plots) == 1:
            if not any(self.is_placeholder(fig) for fig in self.stored_plots):
                placeholder_fig = self.create_placeholder()
                self.stored_plots = real_plots + [placeholder_fig]
            else:
                self.stored_plots = real_plots + [fig for fig in self.stored_plots if self.is_placeholder(fig)]
        else:
            self.stored_plots = real_plots

    def store_plot(self):
        """
        Stores the current plot in the internal list (up to max slots).
        Automatically manages the placeholder so that it is only present when exactly one real plot is stored.
        Updates the store button text and preview grid.
        """
        if self.results is None:
            QMessageBox.warning(self, "No Results", "No results to store.")
            return

        max_slots = self.grid_rows * self.grid_cols
        self.stored_plots = [fig for fig in self.stored_plots if not self.is_placeholder(fig)]
        if len(self.stored_plots) >= max_slots:
            QMessageBox.warning(self, "Limit Reached", f"Maximum number of plots ({max_slots}) reached.")
            return

        fig, ax = plt.subplots(figsize=(4, 4))
        sample = next(iter(self.results.values()))
        if len(sample) == 2:
            for t, (x, T) in self.results.items():
                ax.plot(x, T, label=f"Time = {t} years")
            ax.set_xlabel("Distance from center (m)")
            ax.set_ylabel("Temperature (°C)")
            ax.set_title(f"{self.id}")
            ax.legend()
        else:
            ax.text(0.5, 0.5, "2D Plot", fontsize=12, ha="center", va="center")
            ax.axis("off")
        plt.tight_layout()

        self.stored_plots.append(fig)
        self.manage_placeholder()
        self.update_store_button_text()
        self.update_preview()
        print(f"Plot stored. Total stored plots: {len(self.stored_plots)}")

    def update_store_button_text(self):
        """
        Updates the text of the store button to indicate the number of used slots.
        """
        real_count = len([fig for fig in self.stored_plots if not self.is_placeholder(fig)])
        max_slots = self.grid_rows * self.grid_cols
        self.store_button.setText(f"Store Plot - {real_count}/{max_slots} slots used")
        if real_count >= 1:
            self.next_input_button.setVisible(True)
        else:
            self.next_input_button.setVisible(False)
            
    def next_input(self):
        """
        Called when the 'Next Input' button is clicked.
        Emits a signal to indicate that main inputs should be cleared, then closes this window.
        """
        self.next_input_signal.emit()
        self.close()

    def update_preview(self):
        """
        Updates the preview grid layout with thumbnails of the stored plots.
        """
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for index, fig in enumerate(self.stored_plots):
            pixmap = figure_to_pixmap(fig)
            label = ClickableLabel(index)
            label.setPixmap(pixmap)
            label.setScaledContents(True)
            label.clicked.connect(self.on_preview_click)
            self.preview_layout.addWidget(label, index // self.grid_cols, index % self.grid_cols)

    def on_preview_click(self, index):
        """
        Called when a thumbnail is clicked in the preview grid.
        Prompts the user to view or delete the stored plot.
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Slot Options")
        msg_box.setText(f"Do you want to view or delete the plot in slot {index + 1}?")
        msg_box.setStandardButtons(QMessageBox.Cancel)
        view_button = msg_box.addButton("View", QMessageBox.ActionRole)
        delete_button = msg_box.addButton("Delete", QMessageBox.ActionRole)
        msg_box.exec_()

        if msg_box.clickedButton() == view_button:
            fig = self.stored_plots[index]
            new_fig, new_ax = plt.subplots()
            for line in fig.axes[0].get_lines():
                new_ax.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
            new_ax.set_xlabel(fig.axes[0].get_xlabel())
            new_ax.set_ylabel(fig.axes[0].get_ylabel())
            new_ax.set_title(fig.axes[0].get_title())
            new_ax.legend()
            plt.tight_layout()
            plt.show(block=False)
        elif msg_box.clickedButton() == delete_button:
            del self.stored_plots[index]
            self.update_store_button_text()
            QMessageBox.information(self, "Plot Deleted", f"Plot in slot {index + 1} has been deleted.")
            self.update_preview()

    def clear_grid(self):
        """
        Clears all stored plots from the grid.
        """
        self.stored_plots = []
        self.update_store_button_text()
        self.update_preview()
        print("Stored plots cleared.")

    def save_grid_as_pdf(self):
        """
        Saves all stored plots in a grid layout as a single PDF file.
        """
        if not self.stored_plots:
            QMessageBox.warning(self, "No Plots", "No plots to save.")
            return

        pdf_filename, _ = QFileDialog.getSaveFileName(
            self, "Save Grid as PDF", os.getcwd(), "PDF Files (*.pdf)"
        )
        if not pdf_filename:
            return
        if not pdf_filename.lower().endswith(".pdf"):
            pdf_filename += ".pdf"
        pdf_filename = os.path.abspath(pdf_filename)

        real_count = len([fig for fig in self.stored_plots if not self.is_placeholder(fig)])
        if real_count <= 4:
            rows, cols = 2, 2
        elif real_count <= 9:
            rows, cols = 3, 3
        else:
            rows, cols = 4, 4

        fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3))
        axes = axes.flatten()

        for i in range(rows * cols):
            ax = axes[i]
            ax.clear()
            if i < len(self.stored_plots):
                for line in self.stored_plots[i].axes[0].get_lines():
                    ax.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
                ax.set_title(self.stored_plots[i].axes[0].get_title())
                ax.legend()
            else:
                ax.axis('off')

        fig.suptitle(f"Thermal Model Results Grid", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig(pdf_filename, format="pdf")
        plt.close(fig)
        QMessageBox.information(self, "Success", f"Grid saved as {pdf_filename}.")
        self.clear_grid()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Visualization()

    # Example data for testing.
    # Uncomment one of the following examples:
    # For 1D results:
    # sample_results = {
    #     1: ([0, 10, 20, 30], [100, 90, 80, 70]),
    #     2: ([0, 10, 20, 30], [95, 85, 75, 65])
    # }
    # For 2D results (e.g., pipe-like):
    # import numpy as np
    # x = np.linspace(-30, 30, 100)
    # y = np.linspace(-30, 30, 100)
    # X, Y = np.meshgrid(x, y)
    # T = 100 * np.exp(-((X/20)**2 + (Y/30)**2))
    # sample_results = {1: (X, Y, T)}
    
    # Usando o exemplo 1D:
    sample_results = {
        1: ([0, 10, 20, 30], [100, 90, 80, 70]),
        2: ([0, 10, 20, 30], [95, 85, 75, 65])
    }
    window.set_data(sample_results, "Tabular-like body")
    window.set_id("1")

    window.show()
    sys.exit(app.exec_())
