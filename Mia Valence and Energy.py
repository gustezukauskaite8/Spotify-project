import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


connection = sqlite3.connect('data/spotify_database.db')

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