import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


##########################################################################################################################
# Talisha

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

#2.Create Heatmap eras and features
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

#3.Create Average Graph features
features_to_plot = ['energy', 'danceability', 'acousticness', 'valence']

# Used AI to figure out how to connect to previous dataframe
plot_data = era_profile.reset_index()


for feature in features_to_plot:
    plt.figure(figsize=(10, 6))

    plt.bar(plot_data['era'], plot_data[feature], color='purple', alpha=0.8)

    plt.title(f'Average {feature.capitalize()} across Eras', fontsize=14)
    plt.xlabel('Eras', fontsize=12)
    plt.ylabel(f'Mean {feature.capitalize()}', fontsize=12)
    plt.grid(axis='y', alpha=0.6)


    plt.show()

