import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm
from Spotify_project import plot_circular_bars, scatterplot_popularity
import sqlite3

st.set_page_config(layout="wide")

@st.cache_data
def load_combined_data(eras):
    all_data = []
        
    conn = sqlite3.connect('data/spotify_cleaned.db')
    era_map = {"1980s": (1980, 1989), "1990s": (1990, 1999), "2000s": (2000, 2009), "2010s": (2010, 2019), "2020s": (2020, 2029)}
    
    for era in eras:
        start, end = era_map[era]
        query = f"""
        SELECT f.*, a.album_name, a.release_date, a.track_name, r.name as artist_name, r.genre_0 as genre, r.artist_popularity
        FROM features_data f
        JOIN albums_data a ON f.id = a.track_id
        JOIN artist_data r ON a.artist_id = r.id
        WHERE CAST(SUBSTR(a.release_date, 1, 4) AS INTEGER) BETWEEN {start} AND {end}
        """
        temp_df = pd.read_sql_query(query, conn)
        temp_df = temp_df.loc[:, ~temp_df.columns.duplicated()].copy()
        temp_df['era_label'] = era 
        all_data.append(temp_df)
    conn.close()
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()



# 3. Page Header

st.title(" Spotify 2023 Eras overview dashboard")


eras = st.multiselect("Select decades:", ['1980s', '1990s', '2000s', '2010s', '2020s'])
st.write("You selected", len(eras), "decades")


if eras:
    final_df = load_combined_data(eras)


# 5. Dashboard Layout: Columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Artists based on popularity")
    fig = plot_circular_bars(final_df)
    st.pyplot(fig)

with col2:
    st.subheader("Top 10 Artists based on followers")
    scatterplot_popularity(final_df)