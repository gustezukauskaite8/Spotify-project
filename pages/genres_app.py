
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
from itertools import combinations
import plotly.express as px
import numpy as np
from styling import apply_design, editorial_header, theme_plotly

# 1. Page Config & Theme
st.set_page_config(page_title="Spotify 2023 Analysis", layout="wide")
apply_design()

# Define Brand Colors to match your Eras Dashboard
BRAND_COLORS = {"bg": "#83AD6C", "primary": "#753696", "text": "#220C10"}

@st.cache_data
def load_dashboard_data():
    conn = sqlite3.connect('data/spotify_database.db')

    n_artists = pd.read_sql("SELECT COUNT(DISTINCT id) FROM artist_data", conn).iloc[0, 0]
    n_songs = pd.read_sql("SELECT COUNT(DISTINCT track_id) FROM albums_data", conn).iloc[0, 0]

    genre_query = """
        SELECT name, artist_popularity, genre_0, genre_1, genre_2, 
        genre_3, genre_4, genre_5, genre_6 
        FROM artist_data
    """
    top_pop = pd.read_sql(genre_query, conn)

    query = """
        SELECT r.genre_0 as genre, 
               r.name as artist_name,
               a.track_name, 
               t.track_popularity
        FROM artist_data r
        JOIN albums_data a ON r.id = a.artist_id
        JOIN tracks_data t ON a.track_id = t.id
        WHERE r.genre_0 IS NOT NULL AND r.genre_0 != ''
    """
    df_genre = pd.read_sql_query(query, conn)

    features_query = """
        SELECT 
            r.genre_0 AS genre,
            AVG(f.danceability) AS danceability,
            AVG(f.energy) AS energy,
            AVG(f.key) AS key,
            AVG(f.loudness) AS loudness,
            AVG(f.mode) AS mode,
            AVG(f.speechiness) AS speechiness,
            AVG(f.acousticness) AS acousticness,
            AVG(f.instrumentalness) AS instrumentalness,
            AVG(f.liveness) AS liveness,
            AVG(f.valence) AS valence,
            AVG(f.tempo) AS tempo
        FROM artist_data r
        JOIN albums_data a ON r.id = a.artist_id
        JOIN features_data f ON a.track_id = f.id
        WHERE r.genre_0 IS NOT NULL AND r.genre_0 != ''
        GROUP BY r.genre_0
    """
    df_features = pd.read_sql_query(features_query, conn)

    timeline_query = """
        SELECT
            r.genre_0 AS genre,
            a.release_date
        FROM artist_data r
        JOIN albums_data a ON r.id = a.artist_id
        WHERE r.genre_0 IS NOT NULL AND r.genre_0 != ''
    """
    df_timeline = pd.read_sql_query(timeline_query, conn)

    conn.close()
    return n_artists, n_songs, top_pop, df_genre, df_features, df_timeline

n_artists, n_songs, top_pop, df_genre, df_features, df_timeline = load_dashboard_data()

st.sidebar.header("Filter the Context")
if not df_genre.empty:
    available_genres = sorted(df_genre['genre'].unique())
    selected_genre = st.sidebar.selectbox("Choose a Genre", available_genres)
else:
    st.error("No data loaded. Check database connection.")
    st.stop()

editorial_header("Data Engineering Analysis", "Spotify Genres Dashboard")
st.markdown(f"### Current View: {selected_genre}")
st.divider()

genre_data = df_genre[df_genre['genre'] == selected_genre]
genre_artists = genre_data['artist_name'].nunique()
genre_songs = genre_data.shape[0]
genre_avg = genre_data['track_popularity'].mean()

col1, col2, col3 = st.columns(3)
col1.metric(f"Artists in {selected_genre}", f"{genre_artists:,}")
col2.metric(f"Songs in {selected_genre}", f"{genre_songs:,}")
col3.metric(f"{selected_genre} Avg Pop.", f"{genre_avg:.1f}")

# --- Rankings Tables ---
st.subheader(f"Rankings in: {selected_genre}")
col_left, col_right = st.columns(2)

with col_left:
    st.write("**Top 5 Songs**")
    top_5_songs = genre_data.nlargest(5, 'track_popularity')[['track_name', 'track_popularity']].reset_index(drop=True)
    if not top_5_songs.empty:
        top_5_songs.index += 1
        st.table(top_5_songs)

with col_right:
    st.write("**Top 5 Artists**")
    top_5_artists = genre_data.groupby('artist_name')['track_popularity'].max().reset_index()
    top_5_artists = top_5_artists.nlargest(5, 'track_popularity').reset_index(drop=True)
    if not top_5_artists.empty:
        top_5_artists.index += 1
        st.table(top_5_artists)

# --- Genre Combinations ---
st.divider()
st.subheader(f"Most frequent combinations with: {selected_genre}")

def top_genre_combinations(top_pop, selected_genre):
    genre_cols = [col for col in top_pop.columns if col.startswith('genre_')]
    is_in_genre = (top_pop[genre_cols] == selected_genre).any(axis=1)
    df_filtered = top_pop[is_in_genre]

    df_row_of_genres = df_filtered.melt(id_vars=['name'], value_vars=genre_cols, value_name='genres')
    df_row_of_genres = df_row_of_genres.dropna(subset=['genres'])
    df_row_of_genres = df_row_of_genres[df_row_of_genres['genres'] != ""]

    artist_groups = df_row_of_genres.groupby('name')
    all_pair_dfs = []

    for name, group in artist_groups:
        unique_genres = sorted(group['genres'].unique())
        if len(unique_genres) >= 2:
            genre_pairs = list(combinations(unique_genres, 2))
            relevant_pairs = [p for p in genre_pairs if selected_genre in p]
            if relevant_pairs:
                all_pair_dfs.append(pd.DataFrame(relevant_pairs, columns=['Genre1', 'Genre2']))

    if all_pair_dfs:
        pairs_df = pd.concat(all_pair_dfs, ignore_index=True)
        top_combos = pairs_df.value_counts().head(10).reset_index()
        top_combos.columns = ['Genre A', 'Genre B', 'Artist Count']
        top_combos['Combination'] = top_combos['Genre A'] + " & " + top_combos['Genre B']
        return top_combos[['Combination', 'Artist Count']]
    return pd.DataFrame()

combo_data = top_genre_combinations(top_pop, selected_genre)

if not combo_data.empty:
    fig_combo = px.bar(combo_data, x='Combination', y='Artist Count', color_discrete_sequence=[BRAND_COLORS['primary']])
    fig_combo.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(theme_plotly(fig_combo), use_container_width=True)
    st.table(combo_data)
else:
    st.info(f"No common genre combinations found for {selected_genre}.")

# --- Popularity Distribution ---
st.divider()
st.subheader(f"Popularity Analysis for: {selected_genre}")

genre_cols = [col for col in top_pop.columns if col.startswith('genre_')]
top_pop['is_target_genre'] = (top_pop[genre_cols] == selected_genre).any(axis=1).astype(int)
correlation_genre_popularity = top_pop['is_target_genre'].corr(top_pop['artist_popularity'])

col_text, col_visual = st.columns([1, 2])

with col_text:
    st.write(f"**Correlation Coefficient**")
    st.code(f"{correlation_genre_popularity:.4f}")
    if correlation_genre_popularity > 0.1:
        st.success(f"Artists show a positive popularity correlation.")
    elif correlation_genre_popularity < -0.1:
        st.warning(f"Artists show a negative popularity correlation.")
    else:
        st.info(f"Genre has no significant impact on popularity.")

with col_visual:
    top_pop['Category'] = top_pop['is_target_genre'].map({1: f'{selected_genre}', 0: 'Other Genres'})
    fig_box = px.box(top_pop, x="Category", y="artist_popularity", color="Category",
        color_discrete_map={f'{selected_genre}': BRAND_COLORS['primary'], 'Other Genres': '#777777'}
    )
    fig_box.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=BRAND_COLORS['text']))
    st.plotly_chart(theme_plotly(fig_box), use_container_width=True)

# --- Radar Chart ---
st.divider()
st.subheader(f"Audio Fingerprint: {selected_genre}")

genre_stats = df_features[df_features['genre'] == selected_genre].iloc[0]
categories = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']
values = [genre_stats[cat] for cat in categories]

fig_radar = px.line_polar(r=values, theta=categories, line_close=True, range_r=[0, 1], color_discrete_sequence=[BRAND_COLORS['primary']])
fig_radar.update_traces(fill='toself')
fig_radar.update_layout(
    margin=dict(l=50, r=50, t=50, b=50),
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color=BRAND_COLORS['text'])
)
st.plotly_chart(theme_plotly(fig_radar), use_container_width=True)

# --- Timeline ---
st.divider()
st.subheader(f"Release Timeline: {selected_genre}")

df_timeline['release_year'] = pd.to_datetime(df_timeline['release_date'], errors='coerce').dt.year
df_timeline = df_timeline.dropna(subset=['release_year'])
genre_timeline = df_timeline[df_timeline['genre'] == selected_genre]
yearly_counts = genre_timeline.groupby('release_year').size().reset_index(name='Count')

if not yearly_counts.empty:
    peak_row = yearly_counts.loc[yearly_counts['Count'].idxmax()]
    st.markdown(f"**{int(peak_row['release_year'])}** was the peak year with **{int(peak_row['Count'])}** releases.")

    fig_timeline = px.bar(yearly_counts, x='release_year', y='Count', color_discrete_sequence=[BRAND_COLORS['primary']])
    fig_timeline.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=BRAND_COLORS['text'])
    )
    fig_timeline.update_xaxes(type='linear', tickformat="d")
    st.plotly_chart(theme_plotly(fig_timeline), use_container_width=True)
else:
    st.info("No timeline data available.")
