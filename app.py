import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm
from Spotify_project import *
import sqlite3


connection = sqlite3.connect('data/spotify_clean.db')
query = f"SELECT * FROM artist_data"
home_page = st.Page("dashboard_home.py", title="Main overview", default=True)
artist_page = st.Page("pages/artists_app.py", title="Artists")
features_page = st.Page("pages/features_app.py", title="Features")
genres_page = st.Page("pages/genres_app.py", title="Genres")
#ai_analyst = st.Page("pages/ai_analyst.py", title="Ask the AI analyst")
#eras_page = st.Page("pages/eras_app.py", title="Eras")

pg = st.navigation([home_page, artist_page, features_page,genres_page ])

st.set_page_config(page_title="Spotify 2023 Global Overview", layout="wide")
pg.run()
