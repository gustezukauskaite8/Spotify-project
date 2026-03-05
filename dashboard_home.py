import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm
from Spotify_project import plot_circular_bars, scatterplot_popularity
import sqlite3

# 1. Data Connection
# We use st.cache_resource so it doesn't reconnect every time you switch pages
@st.cache_resource
def get_connection():
    return sqlite3.connect('data/spotify_cleaned.db', check_same_thread=False)

connection = get_connection()
query = "SELECT * FROM artist_data"

# 2. Data Loading
@st.cache_data
def load_data():
    return pd.read_sql(query, connection)

data = load_data()

# 3. Page Header
st.title(" Spotify 2023 Data Engineering Dashboard")
st.markdown("---")

# 5. Dashboard Layout: Columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Artists based on popularity")
    # Using your custom plot function
    fig = plot_circular_bars(data)
    st.pyplot(fig)

with col2:
    st.subheader("Top 10 Artists based on followers")
    # Showing over-performers (high residuals)
    scatterplot_popularity(data)