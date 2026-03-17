import sqlite3
import pandas as pd
import numpy as np
import os

def create_cleaned_database(source_db, target_db):
    
    if not os.path.exists(source_db):
        print(f" Error: {source_db} not found!")
        return

    conn = sqlite3.connect(source_db)
    
    # clean artists
    print("🧹 Cleaning Artist Data...")
    df_artists = pd.read_sql_query("SELECT * FROM artist_data", conn)
    df_artists.replace('', np.nan, inplace=True)
    
    # Drop rows missing essential info
    df_artists = df_artists.dropna(subset=['id', 'name'])
    df_artists = df_artists[df_artists['name'].str.lower() != 'various artists']
    # Standardize names for deduplication
    df_artists['name_clean'] = df_artists['name'].str.lower().str.strip()
    
    # Sort so that the most popular version of a duplicate artist is kept
    df_artists = df_artists.sort_values(by=['name_clean', 'artist_popularity'], ascending=[True, False])
    
    # Create the master cleaned artist list
    df_artists_cleaned = df_artists.drop_duplicates(subset=['name_clean'], keep='first').copy()
    
    # Create a mapping to ensure all track data points to the Master Artist ID
    name_to_master_id = dict(zip(df_artists_cleaned['name_clean'], df_artists_cleaned['id']))
    mapping_dict = dict(zip(df_artists['id'], df_artists['name_clean'].map(name_to_master_id)))

    # clean albums
    df_albums = pd.read_sql_query("SELECT * FROM albums_data", conn)
    df_albums.replace('', np.nan, inplace=True)
    
    # Fix Artist IDs using our mapping
    df_albums['artist_id'] = df_albums['artist_id'].map(mapping_dict)
    
    # We drop duplicates based on the song name and the artist.
    df_albums = df_albums.drop_duplicates(subset=['track_name', 'artist_id'], keep='first')
    
    # Remove rows with missing IDs or zero duration
    df_albums = df_albums.dropna(subset=['track_id', 'artist_id'])
    if 'duration_sec' in df_albums.columns:
        df_albums = df_albums[df_albums['duration_sec'] > 0]

    # clean tracks and features
    df_tracks = pd.read_sql_query("SELECT * FROM tracks_data", conn)
    df_features = pd.read_sql_query("SELECT * FROM features_data", conn)

    # Standardize empty strings
    for df in [df_tracks, df_features]:
        df.replace('', np.nan, inplace=True)
        df.dropna(subset=['id'], inplace=True)

    valid_track_ids = df_albums['track_id'].unique()
    df_tracks = df_tracks[df_tracks['id'].isin(valid_track_ids)]
    df_features = df_features[df_features['id'].isin(valid_track_ids)]

    conn.close()

    
    # Remove old file if exists to start fresh
    if os.path.exists(target_db):
        os.remove(target_db)
        
    clean_conn = sqlite3.connect(target_db)
    
    df_artists_cleaned.to_sql('artist_data', clean_conn, if_exists='replace', index=False)
    df_albums.to_sql('albums_data', clean_conn, if_exists='replace', index=False)
    df_tracks.to_sql('tracks_data', clean_conn, if_exists='replace', index=False)
    df_features.to_sql('features_data', clean_conn, if_exists='replace', index=False)
    
    clean_conn.close()


if __name__ == "__main__":
    create_cleaned_database('data/spotify_database.db', 'data/spotify_cleaned.db')