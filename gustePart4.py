import sqlite3
import pandas as pd 
import os 
import numpy as np

db_path = os.path.join('data', 'spotify_database.db')
connection = sqlite3.connect(db_path)

# 1. Clean Albums Data
df_albums = pd.read_sql_query("SELECT * FROM albums_data", connection)

df_albums.replace('', np.nan, inplace=True)                     # replaces '' with NULL because dropna() cannnot catch ''

df_albums = df_albums.dropna(subset=['track_id'])               # checks IDs, main artists
df_albums = df_albums.dropna(subset=['album_id'])
df_albums = df_albums.dropna(subset=['artist_id'])
df_albums = df_albums.dropna(subset=['artist_0'])

df_albums = df_albums[df_albums['duration_sec'] > 0]            # checks for negative durations
df_albums = df_albums[df_albums['duration_ms'] > 0] 

df_albums.dropna(axis=1, how='all', inplace=True)               # drops columns with all NULLs


# 2. Clean Tracks Data
df_tracks = pd.read_sql_query("SELECT * FROM tracks_data", connection)

df_tracks.replace('', np.nan, inplace=True)                     # replaces '' with NULL

df_tracks = df_tracks.dropna(subset=['id'])                     # checks IDs


# 3. Clean Features Data
df_features = pd.read_sql_query("SELECT * FROM features_data", connection)

df_features.replace('', np.nan, inplace=True)                   # replaces '' with NULL

df_features = df_features.dropna(subset=['id'])                 # checks IDs

df_features = df_features[df_features['duration_ms'] > 0]       # checks for negative durations


# 4. Clean Artist Data 
df_artists = pd.read_sql_query("SELECT * FROM artist_data", connection)

df_artists.replace('', np.nan, inplace=True)                    # replaces '' with NULL

df_artists = df_artists.dropna(subset=['id'])                   # checks for IDs, names, first genres
df_artists = df_artists.dropna(subset=['name'])
df_artists = df_artists.dropna(subset=['genre_0'])

df_artists.dropna(axis=1, how='all', inplace=True)               # drops columns with all NULLs



