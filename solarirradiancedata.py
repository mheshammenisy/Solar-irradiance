"""
app.py  —  Solar Irradiance Portfolio Dashboard
Run with:  streamlit run app.py
"""

from pathlib import Path

import streamlit as st
import pandas as pd
import pvlib
from pvlib.location import Location

from solar_dashboard import (
    load_data,
    add_solar_components,
    variability_index,
    plot_diurnals,
)

# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------
CSV_PATH = Path("data/Timeseries_53.120_-9.669_SA3_37deg_5deg_2023_2023.csv")
LATITUDE, LONGITUDE = 53.350, -6.260
TIMEZONE = "Europe/Dublin"

st.set_page_config(
    page_title="Solar Irradiance Dashboard",
    page_icon="☀️",
    layout="wide",
)

# ------------------------------------------------------------------------------
# THEME (same dark‑glass look)
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {background: radial-gradient(ellipse at top, #16222A 0%, #1C1C1C 60%);
            color:#F3F4F6;font-family:'Inter',sans-serif;}
    .metric-container{backdrop-filter:blur(16px) saturate(120%);
        background-color:rgba(255,255,255,0.08);padding:1rem 1.25rem;
        border-radius:1rem;border:1px solid rgba(255,255,255,0.15);text-align:center;}
    .metric-container>label{color:#FDE047;font-weight:600;font-size:0.9rem}
    .metric-container>div{font-size:1.6rem;font-weight:700;margin-top:0.25rem}
    footer{visibility:hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# HERO
# ------------------------------------------------------------------------------
st.title("☀️ Solar Irradiance Analysis")
st.caption("Professional dashboard — bundled data, ready for GitHub Pages / Streamlit Cloud")

# ------------------------------------------------------------------------------
# LOAD DATA (no upload widget)
# ------------------------------------------------------------------------------
if not CSV_PATH.exists():
    st.error(f"CSV file not found at `{CSV_PATH}` – please commit it to the repo.")
    st.stop()

df = load_data(CSV_PATH)
df = add_solar_components(df)

# ------------------------------------------------------------------------------
# SIDEBAR – interactive panel orientation
# ------------------------------------------------------------------------------
st.sidebar.header("Panel Orientation")
tilt = st.sidebar.slider("Tilt (°)", 0, 90, 30)
azim = st.sidebar.slider("Azimuth (°)", 0, 360, 180)

# recompute POA for new tilt/azimuth
site = Location(LATITUDE, LONGITUDE, tz=TIMEZONE)
solpos = site.get_solarposition(df.index)
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azim,
    dni=df["DNI"],
    ghi=df["GHI"],
    dhi=df["DHI"],
    solar_zenith=solpos["zenith"],
    solar_azimuth=solpos["azimuth"],
)
df["POA_Global"] = poa["poa_global"]

# ------------------------------------------------------------------------------
# KPI cards
# ------------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f'<div class="metric-container"><label>Variability Index (15 min)</label>'
        f'<div>{variability_index(df):.2f}</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="metric-container"><label>Mean POA (W/m²)</label>'
        f'<div>{df["POA_Global"].mean():.0f}</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="metric-container"><label>Max GHI (W/m²)</label>'
        f'<div>{df["GHI"].max():.0f}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("### ")

# ------------------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------------------
tab_chart, tab_data, tab_dl = st.tabs(["📈 Charts", "📊 Data", "📂 Download"])

with tab_chart:
    st.info("Close pop‑ups to return here.")
    plot_diurnals(df)

with tab_data:
    st.dataframe(df.head(500), height=450)

with tab_dl:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download enriched CSV",
        csv,
        file_name="solar_enriched.csv",
        mime="text/csv",
    )
