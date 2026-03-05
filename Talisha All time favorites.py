import sqlite3
import pandas as pd

database = 'spotify_database.db'
connection = sqlite3.connect(database)

query_timeless = """
SELECT 
    a.track_name, 
    r.name AS artist_name,
    a.album_popularity,
    r.artist_popularity, 
    a.release_date
FROM albums_data a
JOIN artist_data r ON a.artist_id = r.id
"""

df_timeless = pd.read_sql_query(query_timeless, connection)
df_timeless['release_date'] = pd.to_datetime(df_timeless['release_date'], errors='coerce')
df = df_timeless.dropna(subset=['release_date'])
df_filtered = df.loc[(df['release_date'] <= '1990-01-01')]
df_alltimers = df_filtered.nlargest(20, 'album_popularity')
print(df_alltimers[['track_name', 'artist_name', 'album_popularity']])

connection.close()