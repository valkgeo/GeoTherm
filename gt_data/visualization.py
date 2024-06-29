import matplotlib.pyplot as plt

class Visualization:
    def __init__(self):
        self.data = None

    def set_data(self, data):
        self.data = data

    def show(self):
        if self.data:
            for t, (x, T) in self.data.items():
                plt.plot(x, T, label=f'Time = {t} years')

            plt.xlabel('Distance from center (m)')
            plt.ylabel('Temperature (°C)')
            plt.legend()
            plt.title('Thermal Modeling for Spheric-like body')
            plt.show()
        else:
            print("No data to visualize")
