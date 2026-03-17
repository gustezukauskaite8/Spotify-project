import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

##########################################################################################################################
# Album of choice, features of it, consistent features such as danceability, loudness, energy, tempo
# AI usage: fixing the database path, query, and feature analysis plot

db_path = os.path.join('data', 'data/spotify_database.db')
connection = sqlite3.connect(db_path)

query_features = """
SELECT t.track_name, f.danceability, f.loudness, f.energy, f.tempo, 
    f.speechiness, f.acousticness, f.instrumentalness, f.liveness, f.valence
FROM  albums_data t
JOIN features_data f ON t.track_id = f.id
WHERE t.album_name = 'Beauty Behind The Madness'
GROUP BY t.track_name
"""
cursor = connection.cursor()
cursor.execute(query_features)
rows = cursor.fetchall()
df_BBTM = pd.DataFrame(rows, columns = [x[0] for x in cursor.description])

statistics_songs = df_BBTM.describe()
print('The statistics of the album "Beauty Behind The Madness" by The Weeknd:')
print(statistics_songs)


# Feature analysis plot
df_map = df_BBTM.set_index('track_name')
df_scaled = (df_map - df_map.min()) / (df_map.max() - df_map.min())

df_scaled_T = df_scaled.T
annot_T = df_map.values.T

plt.figure(figsize=(20, 8))
sns.heatmap(df_scaled_T, annot=annot_T, fmt=".2f", cmap="BuPu", linewidths=.5)
plt.xticks(rotation=45, ha='right')

plt.title('Song Feature Analysis: Beauty Behind The Madness (Swapped Axes)', fontsize=16)
plt.xlabel('Song Title')
plt.ylabel('Audio Features')
plt.tight_layout()
plt.show()


# Correlations
corr_matrix = df_BBTM.drop(columns=['track_name']).corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='BuPu', fmt=".2f", linewidths=0.5)
plt.title('Correlation Heatmap of Audio Features: Beauty Behind The Madness', fontsize=16)
plt.tight_layout()
plt.show()


##########################################################################################################################
# Top 10% tracks (+ their artist) that perform best on ENERGY, TEMPO 
# Which artists appear most? Which artists stand out in this feature?
# AI usage: fixing query, syntax mistakes

# Analysis of feature ENERGY 
query_energy = """
SELECT t.artist_0, t.track_name, f.energy
FROM  albums_data t
JOIN features_data f ON t.track_id = f.id
ORDER BY f.energy DESC
LIMIT (SELECT COUNT(*) FROM features_data) / 10
"""
cursor.execute(query_energy)
rows = cursor.fetchall()
df_energy = pd.DataFrame(rows, columns = [x[0] for x in cursor.description])

count_artist_songs_in_10_percent_energy = df_energy['artist_0'].value_counts()
top_10_artists_in_energy = count_artist_songs_in_10_percent_energy.head(10)
print("\nTop 10 artists in Energy:\n", top_10_artists_in_energy)

plt.figure(figsize = (10, 6))
plt.barh(top_10_artists_in_energy.index, top_10_artists_in_energy.values, color = 'purple', alpha = 0.8)

plt.title('Top 10 Artists in Energy', fontsize = 14)
plt.xlabel('Number of Tracks')
plt.ylabel('Artist Name')

plt.gca().invert_yaxis()
plt.grid(axis = 'x', linestyle = '--', alpha = 0.6)

plt.tight_layout()
plt.show()

standout_energy_name = top_10_artists_in_energy.index[0]
standout_energy_count = top_10_artists_in_energy.iloc[0]
print(f"\nThe standout artist for Energy is {standout_energy_name} with {standout_energy_count} tracks.")


# Analysis of feature TEMPO
query_tempo = """
SELECT t.artist_0, t.track_name, f.tempo
FROM  albums_data t
JOIN features_data f ON t.track_id = f.id
ORDER BY f.tempo DESC
LIMIT (SELECT COUNT(*) FROM features_data) / 10
"""
cursor.execute(query_tempo)
rows = cursor.fetchall()
df_tempo = pd.DataFrame(rows, columns = [x[0] for x in cursor.description])

count_artist_songs_in_10_percent_tempo = df_tempo['artist_0'].value_counts()
top_10_artists_in_tempo = count_artist_songs_in_10_percent_tempo.head(10)
print("\nTop 10 artists in Tempo:\n", top_10_artists_in_tempo)

plt.figure(figsize = (10, 6))
plt.barh(top_10_artists_in_tempo.index, top_10_artists_in_tempo.values, color = 'purple', alpha = 0.8)

plt.title('Top 10 Artists in Tempo', fontsize = 14)
plt.xlabel('Number of Tracks')
plt.ylabel('Artist Name')

plt.gca().invert_yaxis()
plt.grid(axis = 'x', linestyle = '--', alpha = 0.6)

plt.tight_layout()
plt.show()

standout_tempo_name = top_10_artists_in_tempo.index[0]
standout_tempo_count = top_10_artists_in_tempo.iloc[0]
print(f"The standout artist for Tempo is {standout_tempo_name} with {standout_tempo_count} tracks.")


# Checking if artists appear in both of these lists 
both = set(top_10_artists_in_energy.index) & set(top_10_artists_in_tempo.index)
print(f"\nArtists standing out in BOTH categories: {both}")

##########################################################################################################################
# Analysis of popularity regarding the collaborations
# AI usage: fixing query, syntax mistakes

query_collabs = """
SELECT 
    album_popularity,
    CASE 
        WHEN artist_1 IS NOT NULL AND artist_1 != '' THEN 'Collaboration' 
        ELSE 'Solo' 
    END AS track_type
FROM albums_data
"""
cursor.execute(query_collabs)
rows = cursor.fetchall()
df_counts = pd.DataFrame(rows, columns=['album_popularity','track_type'])


# Count of Solo VS Collaborations
type_counts = df_counts['track_type'].value_counts()

print("\nNumber of Collaborations VS Solo tracks:")
print(type_counts)

plt.figure(figsize = (8, 6))
type_counts.plot(kind = 'bar', color = ['purple', 'skyblue'], alpha = 0.8)

plt.title('Solo Tracks vs. Collaborations', fontsize = 14)
plt.xlabel('Track Type')
plt.ylabel('Number of Tracks')
plt.xticks(rotation = 0)
plt.grid(axis = 'y', linestyle = '--', alpha = 0.6)

plt.tight_layout()
plt.show()


# Popularity analysis
popularity_analysis = df_counts.groupby('track_type')['album_popularity'].mean()

print("\nComaprison of popularity of track types")
print(popularity_analysis)

plt.figure(figsize=(8, 6))
popularity_analysis.plot(kind = 'bar', color = ['purple','skyblue'], alpha = 0.8)

plt.title('Album popularity: Solo VS Collaborations', fontsize = 14)
plt.xlabel('Track Type')
plt.ylabel('Average Album Popularity')
plt.xticks(rotation = 0)
plt.grid(axis = 'y', linestyle = '--', alpha = 0.6)

plt.tight_layout()
plt.show()

