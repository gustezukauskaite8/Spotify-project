import streamlit as st
import sqlite3

home_page = st.Page("dashboard_home.py", title="Main overview", default=True)
artist_page = st.Page("pages/artists_app.py", title="Artists")
features_page = st.Page("pages/features_app.py", title="Features")
genres_page = st.Page("pages/genres_app.py", title="Genres")
eras_page = st.Page("pages/eras_app.py", title="Eras")
ai_analyst = st.Page("pages/ai_analyst.py", title="Ask the AI analyst")


pg = st.navigation([home_page, artist_page, features_page,genres_page, eras_page, ai_analyst ])

st.set_page_config(page_title="Spotify 2023 Global Overview", layout="wide")
pg.run()
