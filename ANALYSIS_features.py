import sqlite3
import pandas as pd 
import os 
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns

db_path = os.path.join('data', 'spotify_database.db')
connection = sqlite3.connect(db_path)

##########################################################################################################################
# Guste
# Scoring of tracks according to their features
# AI usage: correcting the implementation of pd.cut

df_albums = pd.read_sql_query("SELECT * FROM albums_data", connection)
df_features = pd.read_sql_query("SELECT * FROM features_data", connection)
df_artists = pd.read_sql_query("SELECT * FROM artist_data", connection)


labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

df_features['dance_level'] = pd.cut(df_features['danceability'], bins = 5, labels = labels)

df_merged_step1 = pd.merge(df_features[['id', 'dance_level']], df_albums[['track_id', 'artist_id']], left_on = 'id', right_on = 'track_id')
df_final_binning = pd.merge(df_merged_step1, df_artists[['id', 'genre_0']], left_on = 'artist_id', right_on = 'id')

# Very High danceability
very_high_dance_genres = df_final_binning[df_final_binning['dance_level'] == 'Very High']
top_genres_high = very_high_dance_genres['genre_0'].value_counts().head(5)

# Very Low danceability
very_low_dance_genres = df_final_binning[df_final_binning['dance_level'] == 'Very Low']
top_genres_low = very_low_dance_genres['genre_0'].value_counts().head(5)

print("\nTop genres for Very High danceability:")
print(top_genres_high)

print("\nTop Genres for Very Low danceability:")
print(top_genres_low)

plt.figure(figsize=(8, 5))
sns.countplot(x='dance_level', data=df_features, palette='BuPu',hue='dance_level', 
    legend=False, order=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
plt.title('Distribution of tracks by Danceability Level')
plt.show()




##########################################################################################################################
# Leonard
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

connection.close()