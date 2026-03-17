import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


db_path = os.path.join('data', 'spotify_database.db')
connection = sqlite3.connect(db_path)

##########################################################################################################################
# Leonard

# 1. Setup Connection

def album_feature_summary(album_name):
    with sqlite3.connect(db_path) as connection:
        query = """
        SELECT 
            f.danceability, f.energy, f.valence, 
            f.speechiness, f.acousticness
        FROM albums_data a
        JOIN features_data f ON a.track_id = f.id
        WHERE LOWER(a.album_name) = LOWER(?)
        """
        df_album = pd.read_sql_query(query, connection, params=(album_name,))

    if df_album.empty:
        return None
    
    return df_album.mean()

st.subheader("Album Search")
album_name = st.text_input("Enter Album Name")

if album_name:
    summary = album_feature_summary(album_name)
    
    if summary is not None:
        st.write(f"### Summary for: {album_name}")
        st.table(summary)
    else:
        st.warning(f"Could not find an album named '{album_name}'.")




##########################################################################################################################
# Guste
# Album of choice, features of it, consistent features such as danceability, loudness, energy, tempo
# AI usage: fixing the database path, query, and feature analysis plot

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
# Mia
mia_album = "Oops!... I Did It Again"

# AI usage for query structure ( Talisha's code)
query = """
SELECT a.track_name, a.track_number, f.energy, f.valence, f.tempo
FROM albums_data a
JOIN features_data f ON a.track_id = f.id
WHERE a.album_name LIKE ? AND a.total_tracks >= 12
ORDER BY a.track_number
"""

df_britney = pd.read_sql_query(query, connection, params=[f"%{mia_album}%"])
connection.close()

df_britney = df_britney.drop_duplicates(subset=['track_name'], keep='first')

stats = df_britney[['energy', 'valence', 'tempo']].describe()

cv_energy = stats.loc['std', 'energy'] / stats.loc['mean', 'energy']
cv_valence = stats.loc['std', 'valence'] / stats.loc['mean', 'valence']
correlation_valence_energy = df_britney['valence'].corr(df_britney['energy'])


# Energy Plot
df_britney.plot(x='track_name', y='energy', kind='bar', color='pink', legend=False)
plt.title(f'Energy Levels: {mia_album}')
plt.ylabel('Score (0-1)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Valence Plot 
df_britney.plot(x='track_name', y='valence', kind='bar', color='purple', legend=False)
plt.title(f'Valence (Positivity): {mia_album}')
plt.ylabel('Score (0-1)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Scatter plot to visualize the correlation
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_britney, x='valence', y='energy', hue='track_name', s=100)

plt.title(f'Valence vs. Energy Correlation: {mia_album}')
plt.xlabel('Valence (Positivity)')
plt.ylabel('Energy')
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

# Create a scatter plot with a "quadrant" feel
plt.figure(figsize=(10, 7))
sns.scatterplot(data=df_britney, x='valence', y='energy', hue='track_name', s=150)

# Add lines for the "average" to show the four quadrants
plt.axhline(df_britney['energy'].mean(), color='red', linestyle='--', alpha=0.5)
plt.axvline(df_britney['valence'].mean(), color='red', linestyle='--', alpha=0.5)

plt.title('Emotional Quadrants: Valence vs. Energy')
plt.xlabel('Valence (Sad <---> Happy)')
plt.ylabel('Energy (Calm <---> Intense)')

# Label the quadrants
plt.text(0.3, 0.9, "Angry/Tense", fontsize=10, color='gray')
plt.text(0.8, 0.9, "Excited/Happy", fontsize=10, color='gray')
plt.text(0.3, 0.3, "Sad/Depressing", fontsize=10, color='gray')
plt.text(0.8, 0.3, "Relaxed/Chill", fontsize=10, color='gray')
plt.legend(title='Tracks', 
           bbox_to_anchor=(1, 1), 
           loc='upper left', 
           fontsize='small', 
           title_fontsize='medium',
           frameon=True, 
           shadow=True)

plt.show()

# 6. Printing Stats
print(f"--- {mia_album} Statistics ---")
print(stats)
print(f"\nEnergy Coefficient of Variation: {cv_energy:.3f}")
print(f"Valence Coefficient of Variation: {cv_valence:.3f}")
print(f"Correlation between Valence and Energy: {correlation_valence_energy:.3f}")




##########################################################################################################################
# Talisha
#Importing Database
#AI Usage: Figuring out how to format the query and create an adjusted data frame

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




##########################################################################################################################
# Leonard
def connect_db(db_path='data/spotify_database.db'):
    return sqlite3.connect(db_path)


def get_album_features(conn, album_name):
    query = """
    SELECT 
        a.track_id, a.track_name, a.album_name, a.artist_0 AS artist,
        f.danceability, f.loudness, f.energy, f.tempo, f.valence
    FROM albums_data a
    JOIN features_data f ON a.track_id = f.id
    WHERE a.album_name = ?
    ORDER BY a.track_number;
    """
    return pd.read_sql_query(query, conn, params=(album_name,))


def plot_album_features(album_df, features=None):
    if album_df.empty:
        print("No data found for this album.")
        return

    if features is None:
        features = ['danceability', 'loudness', 'energy', 'tempo']

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    for i, feature in enumerate(features):
        axes[i].bar(range(len(album_df)), album_df[feature], color='tab:blue')
        axes[i].set_title(f"Track {feature.capitalize()}")
        axes[i].set_xlabel('Track Number')
        axes[i].set_ylabel('Value')

    plt.tight_layout()
    plt.show()


def top_percent_tracks(conn, feature, percentile=0.9):
    query = f"""
    SELECT 
        a.track_id,
        a.track_name,
        a.album_name,
        a.artist_0 AS artist,
        f.{feature}
    FROM albums_data a
    JOIN features_data f ON a.track_id = f.id;
    """
    df = pd.read_sql_query(query, conn)
    threshold = df[feature].quantile(percentile)
    top_df = df[df[feature] >= threshold].copy()
    top_df = top_df.sort_values(by=feature, ascending=False)
    return top_df

def get_album_artist_popularity(conn):
    query = """
    SELECT a.album_name, a.album_popularity, ar.name AS artist, ar.artist_popularity
    FROM albums_data a
    JOIN artist_data ar ON a.artist_id = ar.id;
    """
    return pd.read_sql_query(query, conn)


def plot_artist_album_popularity(df):
    if df.empty: return
    plt.figure(figsize=(8, 6))
    plt.scatter(df['artist_popularity'], df['album_popularity'], alpha=0.4, color='tab:blue')
    plt.xlabel('Artist Popularity')
    plt.ylabel('Album Popularity')
    plt.title('Relationship: Artist vs. Album Popularity')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

    corr = df['artist_popularity'].corr(df['album_popularity'])
    print(f"Correlation coefficient: {corr:.2f}")


def get_tracks_popularity(conn):
    query = "SELECT explicit, track_popularity FROM tracks_data;"
    return pd.read_sql_query(query, conn)


def plot_explicit_popularity(tracks_df):
    if tracks_df.empty: return
    avg_pop = tracks_df.groupby('explicit')['track_popularity'].mean()
    print("\nAverage popularity (0=Clean, 1=Explicit):")
    print(avg_pop)

    tracks_df.boxplot(column='track_popularity', by='explicit', figsize=(6, 5))
    plt.title("Popularity: Explicit vs Non-Explicit")
    plt.suptitle('')
    plt.ylabel('Popularity Score')
    plt.show()

try:
    conn = connect_db()

    album_name = 'Pure Mccartney (Deluxe Edition)'
    album_df = get_album_features(conn, album_name)
    print(f"--- Analysis for: {album_name} ---")
    print(album_df.head())
    plot_album_features(album_df)

    feature = 'speechiness'
    top_tracks = top_percent_tracks(conn, feature, 0.9)
    print(f"\n--- Top 10% tracks by {feature} ---")
    print(top_tracks[['track_name', 'artist', feature]])
    print(f"\n--- Top artists for {feature} ---")
    print(top_tracks['artist'].value_counts().head(10))

    pop_df = get_album_artist_popularity(conn)
    plot_artist_album_popularity(pop_df)

    tracks_df = get_tracks_popularity(conn)
    plot_explicit_popularity(tracks_df)

finally:
    conn.close()