import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib
from datetime import datetime
from pvlib import location
import streamlit as st
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Solar Irradiance Dashboard", page_icon="🌞", layout="wide")

# Sidebar filters
st.sidebar.header("Filter Options")
selected_month = st.sidebar.selectbox("Select Month", options=list(range(1, 13)), format_func=lambda x: datetime(1900, x, 1).strftime('%B'))
display_diurnal = st.sidebar.checkbox("Show Diurnal Plot", value=True)
display_monthly = st.sidebar.checkbox("Show Monthly Plot", value=True)
display_poa = st.sidebar.checkbox("Show POA Plot", value=True)

tilt = st.sidebar.slider("Tilt Angle (Degrees)", 0, 90, 30)
azimuth = st.sidebar.slider("Azimuth (Degrees)", 0, 360, 180)

# Header
st.title("Solar Irradiance Dashboard - Dublin, Ireland (2023)")
st.markdown("""
Analyze global horizontal irradiance (GHI), plane of array (POA) irradiance, and variability index from a solar dataset.
""")

# Load data
file_path = "Timeseries_53.120_-9.669_SA3_37deg_5deg_2023_2023.csv"
df = pd.read_csv(file_path)
df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
df.set_index('datetime', inplace=True)
df['month'] = df.index.month
df['day'] = df.index.day

# Download option
st.sidebar.download_button("Download Filtered CSV", df.to_csv().encode(), file_name="filtered_irradiance_data.csv", mime="text/csv")

# Month filter
df_filtered = df[df['month'] == selected_month]

st.subheader("Data Preview")
st.dataframe(df_filtered.head(10), use_container_width=True)

# Diurnal plot
if display_diurnal:
    st.subheader(f"Average Daily GHI - {datetime(1900, selected_month, 1).strftime('%B')}")
    daily_avg = df_filtered.groupby('day')['G(i)'].mean()
    fig1, ax1 = plt.subplots()
    daily_avg.plot(marker='o', color='dodgerblue', lw=2, ax=ax1)
    ax1.set_title("Daily GHI")
    ax1.set_xlabel("Day")
    ax1.set_ylabel("GHI (W/m²)")
    ax1.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig1)

# Monthly GHI
if display_monthly:
    st.subheader("Monthly Average GHI")
    monthly_avg = df.groupby('month')['G(i)'].mean()
    fig2, ax2 = plt.subplots()
    monthly_avg.plot(marker='o', color='darkorange', lw=2, ax=ax2)
    ax2.set_title("Monthly GHI")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("GHI (W/m²)")
    ax2.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig2)

# POA Global
if display_poa:
    st.subheader("POA Global Irradiance")
    timezone = 'Europe/Dublin'
    latitude = 53.350
    longitude = -6.260
    df.index = df.index.tz_localize('UTC').tz_convert(timezone)
    site = location.Location(latitude, longitude, tz=timezone)
    solar_position = site.get_solarposition(df.index)

    dni_dhi = pvlib.irradiance.erbs(df['G(i)'], solar_position['zenith'], df.index)
    df['DNI'] = dni_dhi['dni']
    df['DHI'] = dni_dhi['dhi']

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
    fig3, ax3 = plt.subplots()
    monthly_poa_avg.plot(ax=ax3, title='Monthly Average POA Global Irradiance', color='forestgreen', lw=2)
    ax3.set_xlabel('Month')
    ax3.set_ylabel('POA (W/m²)')
    ax3.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig3)

# Clear-sky vs Actual Plot
st.subheader("Clear-sky vs Measured GHI Comparison")
clearsky = site.get_clearsky(df.index)
df['GHI_clear'] = clearsky['ghi']
comparison_df = df[['G(i)', 'GHI_clear']].resample('D').mean()
fig_comp = px.line(comparison_df, labels={'value': 'Irradiance (W/m²)', 'datetime': 'Date'}, title='Daily Average GHI: Measured vs Clear-sky')
st.plotly_chart(fig_comp, use_container_width=True)

# Variability Index
st.subheader("Variability Index (VI)")
ghi_measured = df['G(i)'].resample('15min').mean()
ghi_clear = df['GHI_clear'].resample('15min').mean()

std_measured = ghi_measured.std()
std_clear = ghi_clear.std()
VI = std_measured / std_clear

st.metric("Variability Index (VI)", f"{VI:.4f}")

# Hide footer
st.markdown("""
    <style>
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

