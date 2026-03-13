import sqlite3
import pandas as pd
import numpy as np
import os

def create_cleaned_database(source_db, target_db):
    print("🚀 Starting data cleaning process...")
    source_db = 'spotify_database.db'
    conn = sqlite3.connect(source_db)
    
    # 1. CLEAN ARTISTS
    df_artists = pd.read_sql_query("SELECT * FROM artist_data", conn)
    df_artists.replace('', np.nan, inplace=True)
    df_artists = df_artists.dropna(subset=['id', 'name', 'genre_0'])
    
    # Standardize names for deduplication
    df_artists['name_clean'] = df_artists['name'].str.lower().str.strip()
    df_artists = df_artists.sort_values(by=['name_clean', 'artist_popularity', 'followers'], 
                                        ascending=[True, False, False])
    
    # Create the master cleaned artist list
    df_artists_cleaned = df_artists.drop_duplicates(subset=['name_clean'], keep='first').copy()
    
    # Create the mapping dictionary for ID consistency
    name_to_master_id = dict(zip(df_artists_cleaned['name_clean'], df_artists_cleaned['id']))
    mapping_dict = dict(zip(df_artists['id'], df_artists['name_clean'].map(name_to_master_id)))

    # 2. CLEAN ALBUMS 
    df_albums = pd.read_sql_query("SELECT * FROM albums_data", conn)
    df_albums.replace('', np.nan, inplace=True)
    df_albums['artist_id'] = df_albums['artist_id'].map(mapping_dict)
    df_albums = df_albums.dropna(subset=['track_id', 'album_id', 'artist_id'])
    df_albums = df_albums[(df_albums['duration_sec'] > 0) & (df_albums['duration_ms'] > 0)]

    # 3. CLEAN TRACKS & FEATURES
    df_tracks = pd.read_sql_query("SELECT * FROM tracks_data", conn)
    df_features = pd.read_sql_query("SELECT * FROM features_data", conn)
    
    for df in [df_tracks, df_features]:
        df.replace('', np.nan, inplace=True)
        df.dropna(subset=['id'], inplace=True)
        
    # Add engineered features here so app.py doesn't have to calculate them
    df_features['log_followers'] = np.log1p(df_features['duration_ms']) # Example: replace with actual logic
    
    conn.close()

    # --- SAVE TO NEW DATABASE ---
    print(f"💾 Saving cleaned data to {target_db}...")
    clean_conn = sqlite3.connect(target_db)
    
    df_artists_cleaned.to_sql('artist_data', clean_conn, if_exists='replace', index=False)
    df_albums.to_sql('albums_data', clean_conn, if_exists='replace', index=False)
    df_tracks.to_sql('tracks_data', clean_conn, if_exists='replace', index=False)
    df_features.to_sql('features_data', clean_conn, if_exists='replace', index=False)
    
    clean_conn.close()
    print("✅ Done! Your dashboard can now use the cleaned database.")

if __name__ == "__main__":
    create_cleaned_database('data/spotify_database.db', 'data/spotify_clean.db')
    