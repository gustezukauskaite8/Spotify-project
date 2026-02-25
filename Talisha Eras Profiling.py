
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Connect and Join Data
connection = sqlite3.connect('spotify_database.db')
query = """
SELECT a.release_date, f.danceability, f.energy, f.acousticness, f.valence, f.speechiness
FROM albums_data a
JOIN features_data f ON a.track_id = f.id
WHERE a.release_date IS NOT NULL
"""
df = pd.read_sql_query(query, connection)
connection.close()

df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df = df.dropna(subset=['release_date'])
df['era'] = (df['release_date'].dt.year // 10 * 10).astype(int).astype(str) + 's'
era_profile = df.groupby('era')[['danceability', 'energy', 'acousticness', 'valence', 'speechiness']].mean().sort_index()
print(df['era'].head)
plt.figure(figsize=(10, 8))
sns.heatmap(era_profile, annot=True, cmap='YlOrRd', fmt=".3f")
plt.title(' Feature Heatmap by Era')
plt.tight_layout()
plt.show()