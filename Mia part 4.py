# Aggregate popularity and streams by month and visualize the results for songs with the most total streams.
# Check the artists data for duplicates. This includes resolving issues ambiguous artist names that appear with multiple artist id ’s and considering capitalization issues

import pandas as pd 
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

database = 'data/spotify_database.db'
connection = sqlite3.connect(database)

df_artists = pd.read_sql_query("SELECT * FROM artist_data", connection)
df_artists.replace('', np.nan, inplace=True)
df_artists = df_artists.dropna(subset=['id', 'name', 'genre_0'])
df_artists.dropna(axis=1, how='all', inplace=True)

# Normalize data (remove extra spaces and make names lowercase)  
# Help from AI
df_artists['name_clean'] = df_artists['name'].str.lower().str.strip()

# sort based on popularity
df_artists = df_artists.sort_values(by=['name_clean', 'artist_popularity', 'followers'], 
                                    ascending=[True, False, False])

# keep most popular one
df_artists_cleaned = df_artists.drop_duplicates(subset=['name_clean'], keep='first')

# ID map
# Help from AI: to ensure the ids are not pointing to the ones we deleted

id_mapping = pd.merge(
    df_artists[['id', 'name_clean']], 
    df_artists_cleaned[['id', 'name_clean']], 
    on='name_clean', 
    suffixes=('_old', '_master')
)
mapping_dict = dict(zip(id_mapping['id_old'], id_mapping['id_master']))

# replace any deleted artist IDs in albums with the correct id

df_albums = pd.read_sql_query("SELECT * FROM albums_data", connection)
df_albums['artist_id'] = df_albums['artist_id'].map(mapping_dict)

df_artists_cleaned = df_artists_cleaned.drop(columns=['name_clean'])

#Monthly aggregation based on popularity instead of streams

df_tracks = pd.read_sql_query("SELECT id, track_popularity FROM tracks_data", connection)
df_dates = pd.read_sql_query("SELECT track_id, track_name, release_date FROM albums_data", connection)

# Help from AI to merge the dataframes
df_monthly = pd.merge(df_tracks, df_dates, left_on='id', right_on='track_id')

# 4. Clean the dates
df_monthly['release_date'] = pd.to_datetime(df_monthly['release_date'], errors='coerce')
df_monthly = df_monthly.dropna(subset=['release_date'])

# filter for months
df_monthly['year_month'] = df_monthly['release_date'].dt.to_period('M')

monthly_summary = df_monthly.groupby('year_month').agg({
    'track_popularity': ['mean', 'count']
})
monthly_summary.columns = ['avg_popularity', 'song_count']
monthly_summary = monthly_summary.reset_index()


# Plot avg popularity per release month
df_monthly['month_name'] = df_monthly['release_date'].dt.month_name()

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

#
seasonal_pop = df_monthly.groupby('month_name')['track_popularity'].mean().reindex(month_order)


plt.figure(figsize=(12, 6))
seasonal_pop.plot(kind='bar', color='coral', edgecolor='black')

plt.title('Seasonality: Average Song Popularity by Month of the Year')
plt.ylabel('Average Popularity Score')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

connection.close()