import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm
from Spotify_project import plot_circular_bars
import sqlite3
import time


connection = sqlite3.connect('data/spotify_cleaned.db')
query = f"SELECT * FROM artist_data"

cursor = connection.cursor()
cursor.execute(query)

rows = cursor.fetchall()
data = pd.DataFrame(rows, columns= [x[0] for x in cursor.description])

X = np.log1p(data["followers"])
Y = data["artist_popularity"]

X = sm.add_constant(X)

model = sm.OLS(Y, X).fit()

data["residual"] = model.resid

st.set_page_config(page_title="Spotify Dashboard", layout="wide")

st.title("🎵 Spotify 2023 Strategy Dashboard")
st.markdown("---")


# 3. Sidebar Navigation (Satisfies "Ease of Use" rubric)
st.sidebar.header("Filter Options")

st.sidebar.page_link("app.py", label="Home", icon="🏠")

st.sidebar.page_link("pages/features_app.py", label="Page 2", icon="2️⃣", disabled=True)
st.sidebar.page_link("http://www.google.com", label="Google", icon="🌎")

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

st.markdown("---")
st.header("🔎 Artist Explorer")

# -------------------------------------------------------
# USER INPUT
# -------------------------------------------------------

artist_input = st.text_input("Enter Artist Name")

if artist_input:

    artist_row = data[data["name"].str.lower() == artist_input.lower()]

    if artist_row.empty:
        st.warning("Artist not found in database.")
    else:

        artist = artist_row.iloc[0]

        # -------------------------------------------------------
        # BASIC ARTIST INFO
        # -------------------------------------------------------

        st.subheader(f"Artist Overview: {artist['name']}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Popularity", artist["artist_popularity"])

        with col2:
            st.metric("Followers", f"{artist['followers']:,}")

        with col3:
            genre_list = [
                artist[f"genre_{i}"] for i in range(7)
                if f"genre_{i}" in artist and pd.notna(artist[f"genre_{i}"])
            ]
            st.metric("Number of Genres", len(genre_list))

        st.write("Genres:", ", ".join(genre_list))

        data["popularity_rank"] = data["artist_popularity"].rank(ascending=False)
        rank_all = data.loc[data["name"] == artist["name"], "popularity_rank"].values[0]
        st.markdown(f"<span style='color:#220C10'>Popularity Rank Among All Artists: <b>#{int(rank_all)}</b></span>",
                    unsafe_allow_html=True)

        st.subheader("Popularity Rank per Genre")
        genre_cols = [f"genre_{i}" for i in range(7)]
        genres = [artist[c] for c in genre_cols if c in artist and pd.notna(artist[c])]
        for g in genres:
            df = data[data[genre_cols].isin([g]).any(axis=1)].copy()
            df["genre_rank"] = df["artist_popularity"].rank(ascending=False)
            r = df.loc[df["name"] == artist["name"], "genre_rank"].values[0]
            st.markdown(f"<span style='color:#220C10'>Popularity Rank within <b>{g}</b>: <b>#{int(r)}</b></span>",
                        unsafe_allow_html=True)

        conn = sqlite3.connect('data/spotify_cleaned.db')
        albums = pd.read_sql("SELECT * FROM albums_data", conn)
        features = pd.read_sql("SELECT * FROM features_data", conn)
        tracks = pd.read_sql("SELECT * FROM tracks_data", conn)
        conn.close()

        artist_cols = [f"artist_{i}" for i in range(12)]
        mask = albums[artist_cols].eq(artist["name"]).any(axis=1)
        artist_tracks = albums[mask].merge(tracks, left_on="track_id", right_on="id", how="left")

        top = artist_tracks.sort_values("track_popularity", ascending=False).head(5)[
            ["track_name", "album_name", "album_popularity"]
        ].rename(columns={
            "track_name": "Track Name",
            "album_name": "Album Name",
            "album_popularity": "Album Popularity"
        })
        st.dataframe(top.style.set_table_styles(
            [{"selector": "th", "props": [("background-color", "#83AD6C"), ("color", "#220C10")]}]))

        st.subheader("Album Release Timeline")
        al = albums[mask].copy()
        al["year"] = pd.to_datetime(al["release_date"], errors="coerce").dt.year
        start_year = al["year"].min()
        tl = al.groupby("year")["album_name"].nunique().reset_index(name="albums")
        tl = pd.DataFrame({"year": range(int(start_year), 2024)}).merge(tl, on="year", how="left").fillna(0)
        tl["albums_cumulative"] = tl["albums"].cumsum()

        fig = px.line(tl, x="year", y="albums_cumulative", markers=True)
        fig.update_traces(line=dict(color="#753696"))
        fig.update_layout(plot_bgcolor="#83AD6C", paper_bgcolor="#83AD6C", font=dict(color="#220C10"))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Audio Feature Comparison")
        af = artist_tracks.merge(features, left_on="track_id", right_on="id", how="left")
        cols = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "valence", "tempo"]
        x_feat = st.selectbox("Select X-axis feature", cols, index=0)
        y_feat = st.selectbox("Select Y-axis feature", cols, index=1)

        fig = px.scatter(features, x=x_feat, y=y_feat, opacity=0.2, title=f"{x_feat} vs {y_feat}")
        fig.update_traces(marker=dict(color="#753696", size=2))
        fig.add_scatter(x=af[x_feat], y=af[y_feat], mode="markers",
                        marker=dict(color="#E2B4BD", size=12, line=dict(color="#220C10", width=2)),
                        name=artist["name"], showlegend=True)
        fig.update_layout(plot_bgcolor="#83AD6C", paper_bgcolor="#83AD6C", font=dict(color="#220C10"))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Compare With Another Artist")
        other_name = st.selectbox("Select artist to compare", data["name"].sort_values())
        if other_name:
            other = data[data["name"] == other_name].iloc[0]
            fmt = lambda x: f"{int(x):,}"
            genres_str = lambda a: ", ".join([str(a[f"genre_{i}"]) for i in range(7) if pd.notna(a[f"genre_{i}"])])
            comp = pd.DataFrame({
                artist["name"]: [artist["artist_popularity"], fmt(artist["followers"]), genres_str(artist)],
                other["name"]: [other["artist_popularity"], fmt(other["followers"]), genres_str(other)]
            }, index=["Popularity", "Followers", "Genres"])


            def hi(row):
                if row.name == "Genres":
                    return ["color:#220C10"] * len(row)
                numeric_row = pd.to_numeric([str(v).replace(",", "") for v in row], errors="coerce")
                m = numeric_row.max()
                return ["background-color: #E2B4BD; color:#220C10" if numeric_row[i] == m else "color:#220C10" for i in
                        range(len(row))]


            st.dataframe(comp.style.apply(hi, axis=1))