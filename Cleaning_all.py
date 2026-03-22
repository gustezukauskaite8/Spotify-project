import sqlite3
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations


##########################################################################################################################
# Mia
def create_cleaned_database(source_db, target_db):
    conn = sqlite3.connect(source_db)
    
    # clean artists
    df_artists = pd.read_sql_query("SELECT * FROM artist_data", conn)
    df_artists.replace('', np.nan, inplace=True)
    df_artists = df_artists.dropna(subset=['id', 'name', 'genre_0'])
    
    # Standardize names for deduplication
    df_artists['name_clean'] = df_artists['name'].str.lower().str.strip()
    df_artists = df_artists.sort_values(by=['name_clean', 'artist_popularity', 'followers'], 
                                        ascending=[True, False, False])
    
    # Create the cleaned artist list
    df_artists_cleaned = df_artists.drop_duplicates(subset=['name_clean'], keep='first').copy()
    
    # Create the mapping dictionary for ID consistency
    name_to_master_id = dict(zip(df_artists_cleaned['name_clean'], df_artists_cleaned['id']))
    mapping_dict = dict(zip(df_artists['id'], df_artists['name_clean'].map(name_to_master_id)))

    # Albums cleaning
    df_albums = pd.read_sql_query("SELECT * FROM albums_data", conn)
    df_albums.replace('', np.nan, inplace=True)
    df_albums['artist_id'] = df_albums['artist_id'].map(mapping_dict)
    df_albums = df_albums.dropna(subset=['track_id', 'album_id', 'artist_id'])
    df_albums = df_albums[(df_albums['duration_sec'] > 0) & (df_albums['duration_ms'] > 0)]

    # Tracks adn features 
    df_tracks = pd.read_sql_query("SELECT * FROM tracks_data", conn)
    df_features = pd.read_sql_query("SELECT * FROM features_data", conn)
    
    for df in [df_tracks, df_features]:
        df.replace('', np.nan, inplace=True)
        df.dropna(subset=['id'], inplace=True)
        
    # Add engineered features here so app.py doesn't have to calculate them
    df_features['log_followers'] = np.log1p(df_features['duration_ms']) # Example: replace with actual logic
    
    conn.close()

    # New database
    clean_conn = sqlite3.connect(target_db)
    
    df_artists_cleaned.to_sql('artists', clean_conn, if_exists='replace', index=False)
    df_albums.to_sql('albums', clean_conn, if_exists='replace', index=False)
    df_tracks.to_sql('tracks', clean_conn, if_exists='replace', index=False)
    df_features.to_sql('features', clean_conn, if_exists='replace', index=False)
    
    clean_conn.close()

if __name__ == "__main__":
    create_cleaned_database('data/spotify_database.db', 'data/spotify_clean.db')




##########################################################################################################################
# Mia
database = 'data/spotify_database.db'
connection = sqlite3.connect(database)

df_artists = pd.read_sql_query("SELECT * FROM artist_data", connection)
df_artists.replace('', np.nan, inplace=True)
df_artists = df_artists.dropna(subset=['id', 'name', 'genre_0'])
df_artists.dropna(axis=1, how='all', inplace=True)

# Normalize data (remove extra spaces and make names lowercase)  
# Help from AI
df_artists['name_clean'] = df_artists['name'].str.lower().str.strip()

# sort based on popularity
df_artists = df_artists.sort_values(by=['name_clean', 'artist_popularity', 'followers'], 
                                    ascending=[True, False, False])

# keep most popular one
df_artists_cleaned = df_artists.drop_duplicates(subset=['name_clean'], keep='first')

# ID map
# Help from AI: to ensure the ids are not pointing to the ones we deleted

id_mapping = pd.merge(
    df_artists[['id', 'name_clean']], 
    df_artists_cleaned[['id', 'name_clean']], 
    on='name_clean', 
    suffixes=('_old', '_master')
)
mapping_dict = dict(zip(id_mapping['id_old'], id_mapping['id_master']))

# replace any deleted artist IDs in albums with the correct id

df_albums = pd.read_sql_query("SELECT * FROM albums_data", connection)
df_albums['artist_id'] = df_albums['artist_id'].map(mapping_dict)

df_artists_cleaned = df_artists_cleaned.drop(columns=['name_clean'])




##########################################################################################################################
# Guste
# Removing invalid records 

db_path = os.path.join('data', 'spotify_database.db')
connection = sqlite3.connect(db_path)

# 1. Clean Albums Data
df_albums = pd.read_sql_query("SELECT * FROM albums_data", connection)

df_albums.replace('', np.nan, inplace = True)                     # replaces '' with NULL because dropna() cannnot catch ''

df_albums = df_albums.dropna(subset = ['track_id'])               # checks IDs, main artists
df_albums = df_albums.dropna(subset = ['album_id'])
df_albums = df_albums.dropna(subset = ['artist_id'])
df_albums = df_albums.dropna(subset = ['artist_0'])

df_albums = df_albums[df_albums['duration_sec'] > 0]            # checks for negative durations
df_albums = df_albums[df_albums['duration_ms'] > 0] 

df_albums.dropna(axis = 1, how = 'all', inplace = True)               # drops columns with all NULLs


# 2. Clean Tracks Data
df_tracks = pd.read_sql_query("SELECT * FROM tracks_data", connection)

df_tracks.replace('', np.nan, inplace = True)                     # replaces '' with NULL

df_tracks = df_tracks.dropna(subset = ['id'])                     # checks IDs


# 3. Clean Features Data
df_features = pd.read_sql_query("SELECT * FROM features_data", connection)

df_features.replace('', np.nan, inplace = True)                   # replaces '' with NULL

df_features = df_features.dropna(subset = ['id'])                 # checks IDs

df_features = df_features[df_features['duration_ms'] > 0]       # checks for negative durations


# 4. Clean Artist Data 
df_artists = pd.read_sql_query("SELECT * FROM artist_data", connection)

df_artists.replace('', np.nan, inplace = True)                    # replaces '' with NULL

df_artists = df_artists.dropna(subset = ['id'])                   # checks for IDs, names, first genres
df_artists = df_artists.dropna(subset = ['name'])
df_artists = df_artists.dropna(subset = ['genre_0'])

df_artists.dropna(axis = 1, how = 'all', inplace = True)               # drops columns with all NULLs




##########################################################################################################################
# Leonard
db_path = os.path.join('data', 'spotify_database.db')
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

connection.close()
