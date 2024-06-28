# GeoTherm

GeoTherm is a Python-based software designed for modeling the thermal effects of magmatic intrusions. This tool allows geoscientists to analyze the cooling of magmatic bodies and their thermal impacts on surrounding rock environments.

## Features

- Analytical solutions for heat conduction equations in infinite media.
- Applicable to simple geometric shapes such as planes, cylinders, and spheres.
- Considers temperature-dependent petrophysical properties (density, thermal conductivity and thermal diffusivity).
- Detailed thermal analysis of magmatic cooling and its impacts on adjacent rocks.

## Installation

To install GeoTherm, clone the repository and install the required dependencies:

```bash
git clone https://github.com/valkgeo/GeoTherm.git
cd GeoTherm
pip install -r requirements.txt
```

## Usage

To use GeoTherm, follow the instructions below:

1. Run the main script with the necessary parameters:
    ```bash
    python main.py
    ```
2. Use the graphical user interface (GUI) to perform the following actions:
 - Enter Input Data: Click on the "Enter Input Data" button to input the necessary data for thermal modeling.
 - Run Thermal Model: Once the input data is provided, click on the "Run Thermal Model" button to perform the thermal modeling.
 - Visualize Results: After running the model, click on the "Visualize Results" button to view the results of the thermal modeling.
   
## Case Studies

### Case Study 1: Planar Plutonic Intrusion

- Initial conditions: Amphibolitic conditions at 4 kbar.
- Observed the temperature decrease over time and its effects on the immediate rock environment.

### Case Study 2: Spherical Sub-volcanic Intrusion

- Initial conditions: Subvolcanic environment at 0.5 kbar.
- Studied the cooling dynamics and thermal gradients at the contact between the intrusion and surrounding rocks.

## Validation

The results were compared with Al-Hornblende thermobarometry data and petrographic analyses of metamorphic textures, showing thermodynamic conditions similar to those predicted by GeoTherm.

## Compatibility

GeoTherm has been successfully tested on Apple and Windows platforms. The software package includes source files, executables, and comprehensive documentation available in the online repository.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or further information, please contact [Samir do Nascimento Valcácio] at [samir.valcacio@ufrr.br].
