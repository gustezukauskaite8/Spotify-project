import streamlit as st


home_page = st.Page("dashboard_home.py", title="Main overview", default=True)
artist_page = st.Page("pages/artists_app.py", title="Artists")
features_page = st.Page("pages/features_app.py", title="Features")
genres_page = st.Page("pages/genres_app.py", title="Genres")

pg = st.navigation([home_page, artist_page, features_page,genres_page ])

st.set_page_config(page_title="Spotify Dashboard", layout="wide")

pg.run()