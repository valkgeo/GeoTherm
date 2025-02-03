# gt_data/data_manager.py

class DataManager:
    def __init__(self):
        self.data_store = {}  # Dictionary to store all parameters keyed by ID

    def add_or_update_data(self, id_, parameters):
        """
        Adds or updates the data for a specific ID.
        
        Parameters:
            id_ (str): Unique identifier for the model.
            parameters (dict): Dictionary containing all input parameters.
        """
        self.data_store[id_] = parameters

    def get_data(self, id_):
        """
        Retrieves the stored parameters for a specific ID.
        """
        return self.data_store.get(id_, None)

    def get_ids(self):
        """
        Returns a list of all stored IDs.
        """
        return list(self.data_store.keys())

    def id_exists(self, id_):
        """
        Checks if an ID already exists.
        """
        return id_ in self.data_store

# Create a global instance for use in other modules.
data_manager = DataManager()
