import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Spotify 2023 Analysis", layout="wide")

@st.cache_data
def get_artist_list():
    conn = sqlite3.connect('data/spotify_database.db')
    artists = pd.read_sql("SELECT DISTINCT name FROM artist_data ORDER BY name", conn)
    conn.close()
    return artists['name'].tolist()

@st.cache_data
def get_selected_artist_data(artist_name):
    conn = sqlite3.connect('data/spotify_database.db')
    query = """
        SELECT 
            b.track_name, b.release_date, b.album_name,
            a.name, a.genre_0, a.genre_1, a.genre_2, 
            t.track_popularity,
            f.danceability, f.energy, f.acousticness, f.valence, f.speechiness, f.loudness, f.tempo, f.key, f.instrumentalness, f.liveness
        FROM artist_data a
        JOIN albums_data b ON a.id = b.artist_id
        JOIN tracks_data t ON b.track_id = t.id
        JOIN features_data f ON b.track_id = f.id
        WHERE a.name = ?
    """
    df = pd.read_sql_query(query, conn, params=(artist_name,))
    conn.close()
    return df

artist_list = get_artist_list()
selected_artist = st.sidebar.selectbox("Select an Artist", artist_list)
df_artist = get_selected_artist_data(selected_artist)

st.title("Spotify 2023 Analysis Dashboard")
st.markdown(f"### Artist Profile: {selected_artist}")
st.divider()

#Top 5 songs 
st.subheader(f"Top 5 songs of {selected_artist}")
top_5 = df_artist.nlargest(5, 'track_popularity')[['track_name', 'track_popularity']]
st.table(top_5)
st.divider()

#Artist genres
st.subheader(f"Genres of {selected_artist}")
st.write("**Genres**")
data_genres = df_artist[['genre_0', 'genre_1', 'genre_2']].iloc[0].dropna().unique()
genres = [g for g in data_genres if str(g).strip() != ""]
if len(genres) > 0:
    st.write(", ".join(genres))
else:
    st.info("No genre data available for this artist.")
st.divider()

#Artist features
st.subheader(f"Features of {selected_artist}") 
st.write("**Features**")
radar_categories = ['danceability', 'energy', 'acousticness', 'valence','speechiness', 'instrumentalness', 'liveness']
artist_stats = df_artist[radar_categories].mean()
values = [artist_stats[cat] for cat in radar_categories]

fig_radar = px.line_polar(
    r=values,
    theta=radar_categories,
    line_close=True,
    range_r=[0, 1],
    color_discrete_sequence=['#1DB954'] 
)

fig_radar.update_traces(fill='toself')
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=10))),
    showlegend=False,
    margin=dict(l=40, r=40, t=20, b=20)
)

st.plotly_chart(fig_radar, use_container_width=True)
st.divider()

#Timeline of album releases
st.subheader("Timeline of album releases")

df_artist['year'] = pd.to_datetime(df_artist['release_date'], errors='coerce').dt.year
timeline_data = df_artist.groupby(['year', 'album_name']).size().reset_index(name='track_count')

if not timeline_data.empty:
    fig_time = px.scatter(
        timeline_data, 
        x='year', 
        y='album_name', 
        size_max=15, 
        title=f"Career Discography: {selected_artist}",
        color_discrete_sequence=['#1DB954'],
        labels={'year': 'Year', 'album_name': 'Album Name'}
    )

    fig_time.update_xaxes(type='linear', tickformat="d")
    fig_time.update_layout(
        yaxis={'categoryorder':'total ascending'},
        showlegend=False
    )
    
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("No timeline data available for this artist.")