from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
import matplotlib.pyplot as plt

class Visualization(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Model Results")
        self.setGeometry(100, 100, 800, 600)
        # Initialize the user ID and geometry type attributes.
        self.id = ""
        self.geom_type = ""
        self.results = None

    def set_data(self, results, geom_type):
        """
        Sets the model results and the geometry type.
        
        Parameters:
            results (dict): Dictionary containing the model results 
                            (e.g., {time: (x, T)}).
            geom_type (str): The type of geometry chosen (e.g., 
                             "Spheric-like body", "Tabular-like body", "Plug-like body").
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

    def show(self):
        """
        Overrides the default show method. Plots the results before displaying the dialog.
        """
        self.plot_results()

    def plot_results(self):
        """
        Plots the thermal model results using matplotlib.
        
        The plot title is formatted as:
            "Thermal modeling for {geom_type} {id} body"
            
        It iterates over the result dictionary and plots each time series.
        """
        if self.results is not None:
            plt.figure()
            # Loop over each time and corresponding (x, T) data pair.
            for time, (x, T) in self.results.items():
                plt.plot(x, T, label=f"Time = {time} years")
            plt.xlabel("Distance from center (m)")
            plt.ylabel("Temperature (°C)")
            # Set the plot title using the geometry type and user-provided ID.
            plt.title(f"Thermal modeling for {self.id}  {self.geom_type}")
            plt.legend()
            plt.show()
