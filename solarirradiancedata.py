# Required Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib
from datetime import datetime
from pvlib import location, irradiance, solarposition
from tabulate import tabulate
import streamlit as st


# Directly load the CSV from the specified path
file_path = "C:/Users/mhesh/Documents/Aces3b/Timeseries_53.120_-9.669_SA3_37deg_5deg_2023_2023.csv"

# Read the CSV into a DataFrame
df = pd.read_csv(file_path)

# Display the first few rows in a table format
st.write("Data Preview:")
st.write(tabulate(df.head(10), headers='keys', tablefmt='psql'))

# Convert 'time' column to datetime and extract year, month, day, and time
df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['day'] = df['datetime'].dt.day
df['timehours'] = df['datetime'].dt.strftime('%H:%M')
df.set_index('datetime', inplace=True)

# Display data again after modifications
st.write("Modified Data Preview:")
st.write(tabulate(df.head(10), headers='keys', tablefmt='psql'))

# Calculate the daily average GHI (Global Horizontal Irradiance)
diurnal_avg_daily = df.groupby('day')['G(i)'].mean()

# Plot the diurnal variation
st.write("Average Diurnal GHI per Day")
fig, ax = plt.subplots(figsize=(10, 5))
diurnal_avg_daily.plot(kind='line', marker='o', ax=ax)
ax.set_title('Average Diurnal GHI per Day')
ax.set_xlabel('Day')
ax.set_ylabel('GHI (W/m²)')
ax.grid(True)

# Display the plot on Streamlit
st.pyplot(fig)


# Calculate the monthly average GHI (Global Horizontal Irradiance)
diurnal_avg_month = df.groupby('month')['G(i)'].mean()

# Plot the monthly diurnal variation
st.write("Average Diurnal GHI per Month")
fig, ax = plt.subplots(figsize=(10, 5))
diurnal_avg_month.plot(kind='line', marker='o', ax=ax)
ax.set_title('Average Diurnal GHI per Month')
ax.set_xlabel('Month')
ax.set_ylabel('GHI (W/m²)')
ax.grid(True)

# Display the plot on Streamlit
st.pyplot(fig)

# Localize the time index to your time zone
timezone = 'Europe/Dublin'

# Replace with your actual latitude and longitude
latitude = 53.350
longitude = -6.260

# Assuming df is already loaded, localize timestamps to UTC and convert to local timezone
df.index = pd.to_datetime(df.index)
df.index = df.index.tz_localize('UTC')
df.index = df.index.tz_convert(timezone)

# Create a Location object for the site
site = Location(latitude, longitude, tz=timezone)

# Calculate solar position for each timestamp
solar_position = site.get_solarposition(df.index)

# Use the Erbs model to estimate DNI and DHI
dni_dhi = pvlib.irradiance.erbs(df['G(i)'], solar_position['zenith'], df.index)

# Add DNI and DHI to the DataFrame
df['DNI'] = dni_dhi['dni']
df['DHI'] = dni_dhi['dhi']

# Define the tilt and azimuth of the solar panel
tilt = 30
azimuth = 180

# Calculate POA irradiance
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

# Resample to monthly average POA
monthly_poa_avg = df['POA_Global'].resample('M').mean()

# Plot the Monthly Average POA Global Irradiance
st.write("Monthly Average POA Global Irradiance")
fig, ax = plt.subplots(figsize=(12, 5))
monthly_poa_avg.plot(kind='line', marker='o', ax=ax)
ax.set_title('Monthly Average POA Global Irradiance')
ax.set_xlabel('Month')
ax.set_ylabel('Average Irradiance (W/m²)')
ax.grid(True)

# Display the plot in Streamlit
st.pyplot(fig)


# Assuming df is already loaded with the correct datetime index
# Localize the time index to your time zone
timezone = 'Europe/Dublin'

# Replace with your actual latitude and longitude
latitude = 53.350
longitude = -6.260

# Localize naive timestamps to UTC (assuming input is in UTC)
df.index = pd.to_datetime(df.index)  # Ensure datetime index is parsed correctly
df.index = df.index.tz_convert('UTC')
# Convert to local timezone
df.index = df.index.tz_convert(timezone)

# Create a Location object for the site
site = Location(latitude, longitude, tz=timezone)

# Calculate solar position for each timestamp
solar_position = site.get_solarposition(df.index)

# Use the Erbs model to estimate DNI and DHI
dni_dhi = pvlib.irradiance.erbs(df['G(i)'], solar_position['zenith'], df.index)

# Add DNI and DHI to the DataFrame
df['DNI'] = dni_dhi['dni']
df['DHI'] = dni_dhi['dhi']

# Define the tilt and azimuth of the solar panel
tilt = 30
azimuth = 180

# Calculate POA irradiance
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

# === ✅ NEW PART: Plot Daily Average POA Global Irradiance ===
# Resample to daily average POA
daily_poa_avg = df['POA_Global'].resample('D').mean()

# Plot the Daily Average POA Global Irradiance
st.write("Daily Average POA Global Irradiance")
fig, ax = plt.subplots(figsize=(12, 5))
daily_poa_avg.plot(kind='line', marker='o', ax=ax)
ax.set_title('Daily Average POA Global Irradiance')
ax.set_xlabel('Date')
ax.set_ylabel('Average Irradiance (W/m²)')
ax.grid(True)

# Display the plot in Streamlit
st.pyplot(fig)

# Assuming df is already loaded with the correct datetime index
# Set location for Dublin
latitude = 53.35
longitude = -6.26
timezone = 'Europe/Dublin'
site = Location(latitude=latitude, longitude=longitude, tz=timezone)

# Generate clear-sky GHI using the Ineichen model
clearsky = site.get_clearsky(df.index)
df['GHI_clear'] = clearsky['ghi']

# Resample GHI data to 15-minute intervals (adjust as needed for your dataset)
ghi_measured = df['G(i)'].resample('15min').mean()
ghi_clear = df['GHI_clear'].resample('15min').mean()

# Calculate standard deviation over the resampled period
std_measured = ghi_measured.std()
std_clear = ghi_clear.std()

# Compute the Variability Index (VI)
VI = std_measured / std_clear

# Display the Variability Index (VI) in Streamlit
st.write(f"**Variability Index (VI):** {VI:.4f}")

# Optionally, plot the measured GHI and clearsky GHI to visualize the variability
st.write("**Measured GHI vs Clear Sky GHI**")
fig, ax = plt.subplots(figsize=(12, 5))
ghi_measured.plot(kind='line', label='Measured GHI', ax=ax)
ghi_clear.plot(kind='line', label='Clear Sky GHI', ax=ax)
ax.set_title('Measured GHI vs Clear Sky GHI')
ax.set_xlabel('Date')
ax.set_ylabel('GHI (W/m²)')
ax.legend()
ax.grid(True)

# Display the plot in Streamlit
st.pyplot(fig)




# Assuming your DataFrame is already loaded and contains the necessary columns

# Calculate the differences (ramp rates) between consecutive GHI values (in G(i) column)
df['Ramp_Rate'] = df['G(i)'].diff().abs()  # Absolute difference between consecutive GHI values

# Group by year, month, and day to calculate DARR for each day
darr_daily = df.groupby(['year', 'month', 'day'])['Ramp_Rate'].mean()

# Convert the Series to DataFrame for better compatibility with tabulate
darr_daily_df = darr_daily.reset_index()

# Display the DARR table in a PostgreSQL-style format within Streamlit
st.write("**Daily Average Ramp Rate (DARR)**")
st.table(darr_daily_df)



# Assuming your DataFrame is already loaded and contains the necessary columns

# Calculate the differences (ramp rates) between consecutive GHI values (in G(i) column)
df['Ramp_Rate'] = df['G(i)'].diff().abs()  # Absolute difference between consecutive GHI values

# Group by year, month, and day to calculate DARR for each day
darr_daily = df.groupby(['year', 'month', 'day'])['Ramp_Rate'].mean()

# Convert the Series to DataFrame for better compatibility with tabulate
darr_daily_df = darr_daily.reset_index()

# Display the DARR table in a PostgreSQL-style format within Streamlit
st.write("**Daily Average Ramp Rate (DARR)**")
st.table(darr_daily_df)

# Optionally, print the table in PostgreSQL-style format in the Streamlit log
st.write("PostgreSQL-style table format:")
st.text(tabulate(darr_daily_df, headers='keys', tablefmt='psql', showindex=False))



