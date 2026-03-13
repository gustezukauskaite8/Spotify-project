import streamlit as st
from Spotify_project import *

st.set_page_config(page_title="Spotify 2023 Global Overview", layout="wide")
#AI Usage: figure out hpw to make the different querys for each necessary df
@st.cache_data
def load_dashboard_data():
    conn = sqlite3.connect('spotify_clean.db')


    n_artists = pd.read_sql("SELECT COUNT(DISTINCT id) FROM artist_data", conn).iloc[0, 0]
    n_songs = pd.read_sql("SELECT COUNT(DISTINCT track_id) FROM albums_data", conn).iloc[0, 0]


    top_pop_df = pd.read_sql("SELECT name, artist_popularity, followers FROM artist_data", conn)


    genre_query = """
    SELECT genre_0 as genre, AVG(artist_popularity) as avg_popularity
    FROM artist_data
    WHERE genre_0 IS NOT NULL AND genre_0 != ''
    GROUP BY genre_0
    ORDER BY avg_popularity DESC
    LIMIT 5
    """
    top_5_genres = pd.read_sql(genre_query, conn)


    features_query = """
    SELECT 
        AVG(danceability) as Danceability, 
        AVG(energy) as Energy, 
        AVG(acousticness) as Acousticness, 
        AVG(valence) as Valence, 
        AVG(speechiness) as Speechiness,
        AVG(instrumentalness) as Instrumentalness
    FROM features_data
    """
    avg_features = pd.read_sql(features_query, conn).T.reset_index()
    avg_features.columns = ['Feature', 'Average Global Score']


    global_avg_pop = pd.read_sql("SELECT AVG(track_popularity) FROM tracks_data", conn).iloc[0, 0]

    conn.close()
    return n_artists, n_songs, top_pop_df, top_5_genres, avg_features, global_avg_pop


n_artists, n_songs, top_pop_df, top_5_genres, avg_features, global_avg_pop = load_dashboard_data()


st.title("🎵 Spotify 2023 Analysis Overview")
st.markdown("---")


col1, col2, col3 = st.columns(3)
col1.metric("Unique Artists", f"{n_artists:,}")
col2.metric("Total Songs", f"{n_songs:,}")
col3.metric("Global Avg Track Pop.", f"{global_avg_pop:.1f}")

st.divider()

col_mid_left, col_mid_right = st.columns(2)

with col_mid_left:
    st.subheader("Top 5 Genres (By Avg Artist Popularity)")
    top_5_genres.index += 1
    st.table(top_5_genres)

with col_mid_right:
    st.subheader("Global Audio Feature Profiles")
    st.table(avg_features.style.format({"Average Global Score": "{:.3f}"}))

st.divider()


st.subheader("Artist Performance Rankings")
col_left, col_right = st.columns(2)

with col_left:
    st.write("**Top 10 by Popularity**")
    fig_pop = top10_popularity_chart(top_pop_df)
    st.pyplot(fig_pop)

with col_right:
    st.write("**Top 10 by Followers**")
    fig_foll = top10_follower_chart(top_pop_df)
    st.pyplot(fig_foll)