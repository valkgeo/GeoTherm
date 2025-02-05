# gt_data/data_manager.py

class DataManager:
    def __init__(self):
        """
        Initializes the DataManager with an empty data store and default plot configuration.
        """
        self.data_store = {}  # Dictionary to store all model data.
        # Store plot defaults in a separate attribute.
        self.plot_defaults = {
            "auto_plot": True,  # By default, auto-plot is enabled.
            "x_custom": None,   # No default custom x-range.
            "Tmin": None,       # No default Tmin.
            "Tmax": None        # No default Tmax.
        }

    def add_or_update_data(self, id_, geometry, d, parameters):
        """
        Adds or updates the data for a specific ID.
        """
        self.data_store[id_] = {
            "geometry": geometry,
            "d": d,
            "parameters": parameters
        }

    def get_data(self, id_):
        """Retrieves the stored data for a specific ID."""
        return self.data_store.get(id_, None)

    def get_ids(self):
        """Returns a list of all stored IDs."""
        return list(self.data_store.keys())

    def id_exists(self, id_):
        """Checks if an ID already exists."""
        return id_ in self.data_store

    def set_plot_defaults(self, defaults):
        """
        Sets the default plot configuration.
        
        Parameters:
            defaults (dict): A dictionary containing the default plot configuration.
                             Expected keys: "auto_plot" (bool), "x_custom", "Tmin", "Tmax".
        """
        self.plot_defaults = defaults

    def get_plot_defaults(self):
        """
        Retrieves the default plot configuration.
        
        Returns:
            dict: The default plot configuration.
        """
        return self.plot_defaults

# Global instance:
data_manager = DataManager()
