import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from Spotify_project import *
st.set_page_config(page_title="Spotify 2023 Analysis", layout="wide")


@st.cache_data
def load_dashboard_data():
    conn = sqlite3.connect('spotify_database.db')

    n_artists = pd.read_sql("SELECT COUNT(DISTINCT id) FROM artist_data", conn).iloc[0, 0]
    n_songs = pd.read_sql("SELECT COUNT(DISTINCT track_id) FROM albums_data", conn).iloc[0, 0]


    top_pop = pd.read_sql("SELECT name, artist_popularity, followers FROM artist_data",conn)
    query = """
            SELECT r.genre_0 as genre, \
                   a.track_name, \
                   t.track_popularity
            FROM artist_data r
                     JOIN albums_data a ON r.id = a.artist_id
                     JOIN tracks_data t ON a.track_id = t.id
            WHERE r.genre_0 IS NOT NULL \
              AND r.genre_0 != '' \
            """
    df_genre = pd.read_sql_query(query, conn)

    conn.close()
    return n_artists, n_songs, top_pop, df_genre


n_artists, n_songs, top_pop, df_genre = load_dashboard_data()


st.sidebar.header("Navigation & Filters")
available_genres = sorted(df_genre['genre'].unique())
selected_genre = st.sidebar.selectbox("Choose a Genre", available_genres)

st.title("🎵 Spotify 2023 Analysis Dashboard")
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Unique Artists", f"{n_artists:,}")
col2.metric("Total Songs", f"{n_songs:,}")
col3.metric("Selected Genre Avg Pop.",
            f"{df_genre[df_genre['genre'] == selected_genre]['track_popularity'].mean():.1f}")

st.divider()


st.subheader(f"Top 5 Songs in: {selected_genre}")
top_5 = df_genre[df_genre['genre'] == selected_genre].nlargest(5, 'track_popularity')[
    ['track_name', 'track_popularity']].reset_index(drop=True)
if not top_5.empty:
    top_5.index += 1
    st.table(top_5)

st.divider()
st.subheader("Artist Rankings (Top 10)")
col_left, col_right = st.columns(2)

with col_left:
    st.write("**By Popularity**")
    fig_pop = top10_popularity_chart(top_pop)
    st.pyplot(fig_pop)

with col_right:
    st.write("**By Followers**")
    fig_foll = top10_follower_chart(top_pop)
    st.pyplot(fig_foll)