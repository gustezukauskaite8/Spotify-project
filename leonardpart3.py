import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


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