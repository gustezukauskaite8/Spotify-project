import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

connection = sqlite3.connect('data/spotify_database.db')
query_genre = """
SELECT 
    r.genre_0 as genre, 
    r.artist_popularity,
    f.danceability, f.energy, f.acousticness, f.valence, f.speechiness
FROM artist_data r
JOIN albums_data a ON r.id = a.artist_id
JOIN features_data f ON a.track_id = f.id
WHERE r.genre_0 IS NOT NULL AND r.genre_0 != ''
"""
df_genre = pd.read_sql_query(query_genre, connection)
connection.close()

# HEATMAP 1: MOST COMMON GENRES
top_10_common = df_genre['genre'].value_counts().head(10).index
profile_common = df_genre[df_genre['genre'].isin(top_10_common)].groupby('genre').mean()

plt.figure(figsize=(10, 6))
sns.heatmap(profile_common.drop(columns=['artist_popularity']), annot=True, cmap='YlOrRd', fmt=".2f")
plt.title('Feature Profile: 10 Most Common Genres')
plt.show()

# HEATMAP 2: MOST POPULAR GENRES
# AI USAGE: figuring out how to group the genres
top_10_popular = df_genre.groupby('genre')['artist_popularity'].mean().nlargest(10).index
profile_popular = df_genre[df_genre['genre'].isin(top_10_popular)].groupby('genre').mean()

plt.figure(figsize=(10, 6))
sns.heatmap(profile_popular.drop(columns=['artist_popularity']), annot=True, cmap='YlOrRd', fmt=".2f")
plt.title('Feature Profile: 10 Most Popular Genres')
plt.show()