import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


db_path = os.path.join('data', 'data/spotify_database.db')
connection = sqlite3.connect(db_path)

##########################################################################################################################
# Guste 
# Top 10% tracks (+ their artist) that perform best on ENERGY, TEMPO 
# Which artists appear most? Which artists stand out in this feature?
# AI usage: fixing query, syntax mistakes

cursor = connection.cursor()

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
# Mia 

query = """
SELECT t.track_popularity, a.release_date, f.valence, f.energy
FROM tracks_data t
JOIN features_data f ON t.id = f.id
JOIN albums_data a ON t.id = a.track_id
WHERE a.release_date IS NOT NULL
"""

df =pd.read_sql_query(query, connection)
connection.close()


df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df = df.dropna(subset=['release_date', 'valence', 'energy'])

df['era'] = (df['release_date'].dt.year // 10 * 10).astype(int).astype(str) + 's'

df = df[df['release_date'].dt.year >= 1970]



conditions = [
    (df['valence'] < 0.5) & (df['energy'] >= 0.5), # Tense (Low Happiness, High Intensity)
    (df['valence'] >= 0.5) & (df['energy'] >= 0.5), # Happy (High Happiness, High Intensity)
    (df['valence'] < 0.5) & (df['energy'] < 0.5),  # Sad (Low Happiness, Low Intensity)
    (df['valence'] >= 0.5) & (df['energy'] < 0.5)  # Chill (High Happiness, Low Intensity)
]

labels = ['Tense', 'Happy', 'Sad', 'Chill']


df['quadrant'] = np.select(conditions, labels, default='Unknown')

#Mood and popularity table
era_mood_profile = df.pivot_table(
    index='era', 
    columns='quadrant', 
    values='track_popularity', 
    aggfunc='mean'
).sort_index()

#Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(era_mood_profile, annot=True, cmap='YlOrRd', fmt=".1f")

plt.title('Average Popularity of Music Moods by Era')
plt.ylabel('Decade (Era)')
plt.xlabel('Emotional Quadrant (Mood)')
plt.tight_layout()
plt.show()




##########################################################################################################################
# Talisha
#AI Usage: Figuring out how to format the query and create an adjusted data frame

query_danceability = """
SELECT 
    f.danceability, 
    t.track_popularity, 
    a.artist_0 AS artist_name
FROM features_data f
JOIN tracks_data t ON f.id = t.id
JOIN albums_data a ON f.id = a.track_id
"""

#Setting up Danceability Data
df_danceability = pd.read_sql_query(query_danceability, connection)
top_10_percent_count = int(len(df_danceability) * 0.10)
top10_percent = df_danceability.nlargest(top_10_percent_count, 'danceability')
artist_names = top10_percent['artist_name'].value_counts()

#Plot: Average Popluarity per Danceability bin
df_danceability['dance_bin'] = pd.cut(df_danceability['danceability'], bins=15)
bin_analysis = df_danceability.groupby('dance_bin')['track_popularity'].mean()
bin_analysis.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Average Popularity by Danceability Level')
plt.xlabel('Danceability Range (0 to 1)')
plt.ylabel('Average Popularity Score')
plt.show()
correlation = top10_percent['danceability'].corr(df_danceability['track_popularity'])

#Printing statistics
print(f"Correlation coefficient danceability and popularity: {correlation:.3f}")
print("Artists appearing most in the top 10% of danceability:")
print(artist_names.head(10))

#Standout artists
#AI usage: figuring out how to gather standout artists with the mean
artist_means = df_danceability.groupby('artist_name')['danceability'].agg(['mean', 'count'])
standout_specialists = artist_means[artist_means['count'] > 5].sort_values(by='mean', ascending=False)

print("Artists with the highest AVERAGE danceability:")
print(standout_specialists.head(10))


connection.close()