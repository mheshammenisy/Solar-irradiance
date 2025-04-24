# Solar Irradiance Dashboard

This project provides an interactive dashboard to visualize solar irradiance data. The dashboard is built using Streamlit and showcases solar irradiance data for specific geographical locations.

## Features

- **Time Series Data**: Displays daily and monthly averages of POA (Plane of Array) global irradiance.
- **GHI (Global Horizontal Irradiance)**: Visualizes GHI values, with averages calculated for each day and month.
- **Solar Panel Simulation**: Simulates solar irradiance on a panel with specific tilt and azimuth angles.
- **Variability Index**: Calculates and displays the variability index for GHI data.

## Live Dashboard

You can explore the solar irradiance data on the live Streamlit app here:

[**Solar Irradiance Dashboard**](https://solar-irradiance-f9dzbuxqkzzk3mjsi525df.streamlit.app/)

## Requirements

- Python 3.x
- pandas
- numpy
- matplotlib
- pvlib
- streamlit
- tabulate

## Installation

1. Clone the repository or download the project files.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
