import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#AI Usage: Figuring out how to format the query and create an adjusted data frame
database = 'spotify_database.db'
connection = sqlite3.connect(database)

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