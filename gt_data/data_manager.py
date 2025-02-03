# gt_data/data_manager.py

class DataManager:
    def __init__(self):
        self.data_store = {}  # Dicionário para armazenar os dados

    def add_or_update_data(self, id_, geometry, d, parameters):
        """
        Adds or updates the data for a specific ID.
        
        Parameters:
            id_ (str): The unique identifier for the input.
            geometry (str): The selected geometry.
            d (float): The value of 'd' (e.g., radius or half-width).
            parameters (dict): A dictionary containing all the parameters (T0, K1, k, K, k1, g, l, time, etc.).
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

# Cria uma instância global para ser usada em outros módulos.
data_manager = DataManager()
