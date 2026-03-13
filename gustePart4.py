import sqlite3
import pandas as pd 
import os 
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns

db_path = os.path.join('data', 'data/spotify_database.db')
connection = sqlite3.connect(db_path)

##########################################################################################################################
# Removing invalid records 

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
# Genres that appear together most frequently - already using clean data 
# AI usage: fixing application of groupby for combinations of genres, fixing the figure

genre_cols = [col for col in df_artists.columns if col.startswith('genre_')]

df_row_of_genres = df_artists.melt(id_vars = ['id'], value_vars = genre_cols, value_name = 'genres')
df_row_of_genres = df_row_of_genres.dropna(subset=['genres'])

artist_groups = df_row_of_genres.groupby('id')

all_pair_dfs = []

for artist_id, group in artist_groups:
    
    unique_genres = sorted(group['genres'].unique())
    genre_pairs = list(combinations(unique_genres, 2))
 
    pair_df = pd.DataFrame(genre_pairs, columns=['Genre1', 'Genre2'])
    all_pair_dfs.append(pair_df)

pairs_df = pd.concat(all_pair_dfs, ignore_index=True)
top_genre_combinations = pairs_df.value_counts().head(10)

print("Most frequent combinations of genres")
print(top_genre_combinations)

plt.figure(figsize=(10, 6))
top_genre_combinations.plot(kind='barh', color='purple')
plt.title('Most frequent combinations of genres')
plt.xlabel('Number of artists')
plt.ylabel('Genre pairs')
plt.gca().invert_yaxis() # Highest at the top
plt.show()

##########################################################################################################################
# Scoring of tracks according to their features - already using clean data
# AI usage: correcting the implementation of pd.cut

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





