import sqlite3
import pandas as pd

#AI: Filtering only artist with existing artist data entry
database = 'spotify_database.db'
connection = sqlite3.connect(database)
query_breakout = """
SELECT 
    a.track_name, 
    a.album_popularity, 
    r.artist_popularity
FROM albums_data a
INNER JOIN artist_data r ON a.artist_id = r.id
WHERE r.artist_popularity > 0
"""


df_breakout = pd.read_sql_query(query_breakout, connection)
df_breakout['pop_gap'] = df_breakout['album_popularity'] - df_breakout['artist_popularity']


top_breakouts = df_breakout.nlargest(20, ['pop_gap'])

print(top_breakouts[['track_name', 'artist_popularity', 'album_popularity', 'pop_gap']])
print("Average popularity gap:")
print(df_breakout['pop_gap'].mean())