import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
import os

db_path = os.path.join('data', 'spotify_database.db')
connection = sqlite3.connect(db_path)

##########################################################################################################################
# Talisha

def top10_genre(genre,df):
    filtered_artist = []
    for index, row in df.iterrows():
        for i in range(0, 6):
            column_name = f'genre_{i}'
            if column_name in row and row[column_name] == genre:
                filtered_artist.append(row)

    filtered_df = pd.DataFrame(filtered_artist)[['name', 'artist_popularity']]
    top10_genre = filtered_df.nlargest(10, 'artist_popularity')

    return top10_genre


def genre_count(df):
    all_counts = []
    for index, row in df.iterrows():
        current_artist_count = 0
        for i in range(0, 7):
            column_name = f'genre_{i}'
            if column_name in row and pd.notna(row[column_name]) and str(row[column_name]).strip() != "":
                current_artist_count += 1
        all_counts.append(current_artist_count)
    df['genre_count'] = all_counts
    return df

#Cleaning the automatic header
def plot_genre_boxplot(df):
    plt.figure(figsize=(10, 6))
    df.boxplot(column='artist_popularity', by='genre_count', grid=False)

    plt.title("Popularity Distribution by Number of Genres")
    plt.suptitle("")
    plt.xlabel("Number of Genres Associated with Artist")
    plt.ylabel("Popularity Score")
    plt.show()




##########################################################################################################################
# Talisha

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




##########################################################################################################################
# Guste
# Genres that appear together most frequently 
# AI usage: fixing application of groupby for combinations of genres, fixing the figure

genre_query = """
    SELECT name, artist_popularity, genre_0, genre_1, genre_2, 
        genre_3, genre_4, genre_5, genre_6 
    FROM artist_data
"""
top_pop = pd.read_sql(genre_query, connection)

def top_genre_combinations(df, selected_genre):
    genre_cols = [col for col in df.columns if col.startswith('genre_')]

    is_in_genre = (df[genre_cols] == selected_genre).any(axis = 1)
    df_filtered = df[is_in_genre]

    df_row_of_genres = df_filtered.melt(id_vars = ['name'], value_vars = genre_cols, value_name = 'genres')
    df_row_of_genres = df_row_of_genres.dropna(subset = ['genres'])
    df_row_of_genres = df_row_of_genres[df_row_of_genres['genres'] != ""]

    artist_groups = df_row_of_genres.groupby('name')
    all_pair_dfs = []

    for name, group in artist_groups:
        unique_genres = sorted(group['genres'].unique())
        if len(unique_genres) >= 2:
            genre_pairs = list(combinations(unique_genres, 2))
            pair_df = pd.DataFrame(genre_pairs, columns = ['Genre1', 'Genre2'])
            all_pair_dfs.append(pair_df)

    if all_pair_dfs:
        pairs_df = pd.concat(all_pair_dfs, ignore_index=True)
        top_combos = pairs_df.value_counts().head(10).reset_index()
        top_combos.columns = ['Genre A', 'Genre B', 'Artist Count']
        
        top_combos['Combination'] = top_combos['Genre A'] + " & " + top_combos['Genre B']
        return top_combos[['Combination', 'Artist Count']]
    
    return pd.DataFrame()

top_combinations = top_genre_combinations(top_pop, "Pop")
print("Most frequent combinations of genres")
print(top_combinations)

plt.figure(figsize=(10, 6))
top_combinations.plot(
    kind='barh', 
    x='Combination',      
    y='Artist Count',     
    color='purple',
    legend=False        
)
plt.title('Most frequent combinations of genres')
plt.xlabel('Number of artists')
plt.ylabel('Genre pairs')
plt.gca().invert_yaxis() 
plt.tight_layout()        
plt.show()

connection.close()