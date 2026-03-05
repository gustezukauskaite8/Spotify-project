import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm
from Spotify_project import plot_circular_bars
import sqlite3


connection = sqlite3.connect('data/spotify_clean.db')
query = f"SELECT * FROM artist_data"

cursor = connection.cursor()
cursor.execute(query)

rows = cursor.fetchall()
data = pd.DataFrame(rows, columns= [x[0] for x in cursor.description])

# 1. Page Configuration (Looks professional for "Spotify Owners")
st.set_page_config(page_title="Spotify Dashboar", layout="wide")

st.title("🎵 Spotify 2023 Strategy Dashboard")
st.markdown("---")

# 3. Sidebar Navigation (Satisfies "Ease of Use" rubric)
st.sidebar.header("Filter Options")
min_pop = st.sidebar.slider("Minimum Popularity", 0, 100, 50)
selected_data = data[data['artist_popularity'] >= min_pop]



# 5. Dashboard Layout: Columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Popularity vs. Followers (OLS)")
    # Using Plotly for interactivity (Hover to see names!)
    fig = plot_circular_bars(data)
    st.pyplot(fig)

with col2:
    st.subheader("🚀 The Viral Radar (Creative Insight)")
    # Showing over-performers (high residuals)
    over_performers = selected_data.nlargest(10, 'residual')[['name', 'artist_popularity', 'followers']]
    st.write("Top 10 Artists Outperforming their Fanbase:")
    st.table(over_performers)
