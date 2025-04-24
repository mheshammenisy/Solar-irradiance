import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib
from datetime import datetime
from pvlib import location, irradiance, solarposition
from tabulate import tabulate
import streamlit as st

# Set Streamlit page config for better layout
st.set_page_config(page_title="Solar Irradiance Analysis", page_icon="🌞", layout="wide")

# Add a header for the dashboard
st.title("Solar Irradiance Analysis Dashboard in store location in Dublin Ireland 2023 statistics")
st.markdown("""
    This dashboard presents solar irradiance data, including GHI, POA, and the variability index, 
    visualized over daily and monthly intervals for the given location. 
    Data is sourced from the timeseries CSV file.
""")

# Directly load the CSV from the specified path
file_path = "Timeseries_53.120_-9.669_SA3_37deg_5deg_2023_2023.csv"
df = pd.read_csv(file_path)

# Convert 'time' column to datetime and extract year, month, day, and time
df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['day'] = df['datetime'].dt.day
df['timehours'] = df['datetime'].dt.strftime('%H:%M')
df.set_index('datetime', inplace=True)

# Display data preview
st.subheader("Modified Data Preview")
st.dataframe(df.head(10))

# --- Plot Diurnal Variation ---
st.subheader("Average Diurnal GHI per Day")
diurnal_avg_daily = df.groupby('day')['G(i)'].mean()

fig, ax = plt.subplots(figsize=(10, 5))
diurnal_avg_daily.plot(kind='line', marker='o', ax=ax, color='dodgerblue', lw=2)
ax.set_title('Average Diurnal GHI per Day', fontsize=16)
ax.set_xlabel('Day', fontsize=12)
ax.set_ylabel('GHI (W/m²)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7)

# Display the plot on Streamlit with custom color and styling
st.pyplot(fig)

# --- Plot Monthly Average ---
st.subheader("Average Diurnal GHI per Month")
diurnal_avg_month = df.groupby('month')['G(i)'].mean()

fig, ax = plt.subplots(figsize=(10, 5))
diurnal_avg_month.plot(kind='line', marker='o', ax=ax, color='darkorange', lw=2)
ax.set_title('Average Diurnal GHI per Month', fontsize=16)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('GHI (W/m²)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7)

# Display the plot on Streamlit
st.pyplot(fig)

# --- POA Global Irradiance ---
timezone = 'Europe/Dublin'
latitude = 53.350
longitude = -6.260

df.index = df.index.tz_localize('UTC')
df.index = df.index.tz_convert(timezone)

site = location.Location(latitude, longitude, tz=timezone)
solar_position = site.get_solarposition(df.index)
dni_dhi = pvlib.irradiance.erbs(df['G(i)'], solar_position['zenith'], df.index)

df['DNI'] = dni_dhi['dni']
df['DHI'] = dni_dhi['dhi']

tilt = 30
azimuth = 180

poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azimuth,
    dni=df['DNI'],
    ghi=df['G(i)'],
    dhi=df['DHI'],
    solar_zenith=solar_position['zenith'],
    solar_azimuth=solar_position['azimuth']
)

df['POA_Global'] = poa['poa_global']
monthly_poa_avg = df['POA_Global'].resample('M').mean()

fig, ax = plt.subplots(figsize=(12, 5))
monthly_poa_avg.plot(ax=ax, title='Monthly Average POA Global Irradiance', color='forestgreen', lw=2)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Average Irradiance (W/m²)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7)

st.pyplot(fig)

# --- Variability Index Calculation ---
st.subheader("Variability Index (VI) Calculation")
clearsky = site.get_clearsky(df.index)
df['GHI_clear'] = clearsky['ghi']

ghi_measured = df['G(i)'].resample('15min').mean()
ghi_clear = df['GHI_clear'].resample('15min').mean()

std_measured = ghi_measured.std()
std_clear = ghi_clear.std()

VI = std_measured / std_clear
st.write(f"**Variability Index (VI):** {VI:.4f}", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
    <style>
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
