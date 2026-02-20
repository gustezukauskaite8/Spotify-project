import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#Importing Database
#AI Usage: Figuring out how to format the query and create an adjusted data frame
database = 'spotify_database.db'
connection = sqlite3.connect(database)
query = """
SELECT a.track_name, f.danceability, f.loudness
FROM albums_data a
JOIN features_data f ON a.track_id = f.id
WHERE a.album_name = 'Nirvana' AND a.artist_0 = 'Nirvana'
ORDER BY a.track_number
"""
df_nirvana = pd.read_sql_query(query, connection)

#Danceability and loudness consistency
stats = df_nirvana[['danceability', 'loudness']].describe()
cv_dance = stats.loc['std', 'danceability'] / stats.loc['mean', 'danceability']
cv_loudness = stats.loc['std', 'loudness'] / stats.loc['mean', 'loudness']

#PLot and Stats Danceablity and loudness
df_nirvana.plot(x='track_name', y='danceability', kind='bar', legend=False)
plt.title('Danceability')
plt.ylabel('Score (0-1)')
plt.show()

df_nirvana.plot(x='track_name', y='loudness', kind='bar', color='orange', legend=False)
plt.title('Loudness')
plt.ylabel('Decibels (dB)')
plt.show()

print(f"Dancebility and loudness statistics")
print(stats)
print(f"Danceability Coefficient of Variation: {cv_dance:.3f}")
print(f"Loudness Coefficient of Variation: {cv_loudness:.3f}")

#Artist vs album popularity
query_album = """
SELECT DISTINCT album_id, album_popularity, artist_popularity
FROM albums_data a
JOIN artist_data r ON a.artist_id = r.id
"""
df_popularity = pd.read_sql_query(query_album, connection)


#Plot: Popularity album vs artist
df_popularity.plot(kind='scatter', x='artist_popularity', y='album_popularity', alpha=0.5)
plt.title(f'Album vs Artist Popularity')
plt.xlabel('Artist Popularity')
plt.ylabel('Album Popularity')
plt.show()
correlation_artist_album = df_popularity['artist_popularity'].corr(df_popularity['album_popularity'])
print(f"Correlation: album vs artist popularity: {correlation_artist_album:.3f}")

connection.close()