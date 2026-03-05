import pandas as pd 
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

mia_album = "Oops!... I Did It Again"
database = 'data/spotify_database.db'
connection = sqlite3.connect(database)

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



