import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
from styling import apply_design, editorial_header, theme_plotly


st.set_page_config(layout="wide", page_title="Audio Feature Analysis")
apply_design()

BRAND_COLORS = {"bg": "#83AD6C", "primary": "#753696", "text": "#220C10"}


@st.cache_data
def load_features_data():
    conn = sqlite3.connect('data/spotify_cleaned.db')
    query = """
    SELECT 
        ar.name as artist_name,
        ar.genre_0,
        al.track_name, 
        al.release_date,
        t.track_popularity,
        f.danceability, f.energy, f.acousticness, f.valence, 
        f.speechiness, f.loudness, f.tempo, f.instrumentalness, f.liveness
    FROM features_data f
    JOIN tracks_data t ON f.id = t.id
    JOIN albums_data al ON f.id = al.track_id
    JOIN artist_data ar ON al.artist_id = ar.id
    """
    df = pd.read_sql(query, conn)
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['year'] = df['release_date'].dt.year
    conn.close()
    return df


df_raw = load_features_data()

st.sidebar.title("Filter the Context")
unique_genres = sorted([g for g in df_raw['genre_0'].unique() if g and g != 'null'])
genre_options = ["All Genres"] + unique_genres
selected_genre = st.sidebar.selectbox("Filter by Genre", genre_options)

features_list = ['danceability', 'energy', 'acousticness', 'valence', 'speechiness', 'tempo', 'instrumentalness',
                 'liveness']
selected_feature = st.sidebar.selectbox("Select Audio Feature", features_list)


if selected_genre == "All Genres":
    df = df_raw
else:
    df = df_raw[df_raw['genre_0'] == selected_genre]


editorial_header("Feature Engineering Analysis", f"{selected_feature.capitalize()} Overview")

if not df.empty:
    genre_display = "Global" if selected_genre == "All Genres" else selected_genre
    st.write(f"Showing analysis for: **{genre_display}** ({len(df)} tracks analyzed)")

    avg_score = df[selected_feature].mean()
    highest_row = df.loc[df[selected_feature].idxmax()]
    lowest_row = df.loc[df[selected_feature].idxmin()]

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Avg {selected_feature.capitalize()}", f"{avg_score:.3f}")
    col2.metric("Highest Artist", highest_row['artist_name'], help=f"Track: {highest_row['track_name']}")
    col3.metric("Lowest Artist", lowest_row['artist_name'], help=f"Track: {lowest_row['track_name']}")
    st.divider()


    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.subheader(f"Top 5 Artists: {selected_feature.capitalize()}")
        top_artists = (
            df.groupby('artist_name')[selected_feature]
            .mean()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
        top_artists.columns = ['Artist', f'Avg {selected_feature.capitalize()}']
        st.table(top_artists.reset_index(drop=True))

    with col_right:
        st.subheader(f"Top 10 Genres Comparison")
        top_10_names = df_raw['genre_0'].value_counts().head(10).index
        genre_comp = (
            df_raw[df_raw['genre_0'].isin(top_10_names)]
            .groupby('genre_0')[selected_feature]
            .mean()
            .sort_values(ascending=True)
            .reset_index()
        )

        fig_genre = px.bar(
            genre_comp, x=selected_feature, y='genre_0',
            orientation='h',
            color_discrete_sequence=[BRAND_COLORS['primary']]
        )

        fig_genre.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=BRAND_COLORS['text']),
            xaxis_title=f"Mean {selected_feature.capitalize()}",
            yaxis_title=None,
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(theme_plotly(fig_genre), use_container_width=True)

    st.divider()

    st.subheader(f"Correlation: {selected_feature.capitalize()} vs Others")
    corr_matrix = df[features_list].corr()
    feature_corr = corr_matrix[[selected_feature]].sort_values(by=selected_feature, ascending=False)


    fig_heat, ax = plt.subplots(figsize=(10, 2))
    sns.heatmap(
        feature_corr.T, annot=True,
        cmap=sns.diverging_palette(280, 120, as_cmap=True),  # Purple to Green
        cbar=False, ax=ax, linewidths=1.5
    )


    fig_heat.patch.set_facecolor(BRAND_COLORS['bg'])
    ax.set_facecolor(BRAND_COLORS['bg'])
    st.pyplot(fig_heat)

    st.divider()


    st.subheader(f"{selected_feature.capitalize()} Trends Over Time")
    evolution = df.groupby('year')[selected_feature].mean().reset_index()

    fig_line = px.line(
        evolution, x='year', y=selected_feature,
        markers=True
    )

    fig_line.update_traces(
        line_color=BRAND_COLORS['primary'],
        line_width=3,
        marker=dict(size=8, color=BRAND_COLORS['text'])
    )

    fig_line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=BRAND_COLORS['text']),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    st.plotly_chart(theme_plotly(fig_line), use_container_width=True)

else:
    st.error(f"No data available for the genre: {selected_genre}")
