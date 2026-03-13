import sqlite3
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

db_path = os.path.join('data', 'data/spotify_database.db')
connection = sqlite3.connect(db_path)

df_albums = pd.read_sql_query("SELECT * FROM albums_data", connection)
df_albums.replace('', np.nan, inplace=True)
df_albums = df_albums.dropna(subset=['track_id'])
df_albums = df_albums.dropna(subset=['album_id'])
df_albums = df_albums.dropna(subset=['artist_id'])
df_albums = df_albums.dropna(subset=['artist_0'])
df_albums = df_albums[df_albums['duration_sec'] > 0]
df_albums = df_albums[df_albums['duration_ms'] > 0]
df_albums.dropna(axis=1, how='all', inplace=True)

df_tracks = pd.read_sql_query("SELECT * FROM tracks_data", connection)
df_tracks.replace('', np.nan, inplace=True)
df_tracks = df_tracks.dropna(subset=['id'])

df_features = pd.read_sql_query("SELECT * FROM features_data", connection)
df_features.replace('', np.nan, inplace=True)
df_features = df_features.dropna(subset=['id'])
df_features = df_features[df_features['duration_ms'] > 0]

df_artists = pd.read_sql_query("SELECT * FROM artist_data", connection)
df_artists.replace('', np.nan, inplace=True)
df_artists = df_artists.dropna(subset=['id'])
df_artists = df_artists.dropna(subset=['name'])
df_artists = df_artists.dropna(subset=['genre_0'])
df_artists.dropna(axis=1, how='all', inplace=True)

query = """
SELECT 
    a.track_id,
    a.release_date,
    f.danceability,
    f.energy,
    f.valence,
    f.loudness,
    f.tempo
FROM albums_data a
JOIN features_data f
ON a.track_id = f.id
WHERE a.release_date IS NOT NULL
"""

df_time = pd.read_sql_query(query, connection)
df_time['release_date'] = pd.to_datetime(df_time['release_date'], errors='coerce')
df_time = df_time.dropna(subset=['release_date'])
df_time['year'] = df_time['release_date'].dt.year
features = ['danceability', 'energy', 'valence', 'loudness', 'tempo']
yearly_trend = df_time.groupby('year')[features].mean()

for feature in features:
    plt.figure()
    plt.plot(yearly_trend.index, yearly_trend[feature])
    plt.xlabel("Year")
    plt.ylabel(feature)
    plt.title(f"{feature} over time")
    plt.show()

def album_feature_summary(album_name, connection):

    query = """
    SELECT 
        a.album_name,
        f.danceability,
        f.energy,
        f.valence,
        f.loudness,
        f.tempo,
        f.speechiness,
        f.acousticness
    FROM albums_data a
    JOIN features_data f
    ON a.track_id = f.id
    WHERE LOWER(a.album_name) = LOWER(?)
    """

    df_album = pd.read_sql_query(query, connection, params=(album_name,))

    print("Rows returned:", len(df_album))

    if df_album.empty:
        print("Album not found.")
        return None

    summary = df_album.drop(columns=['album_name']).mean()

    print("\nAlbum Feature Summary:")
    print(summary)

    return summary

album_feature_summary("Pure Mccartney (Deluxe Edition)", connection)

connection.close()