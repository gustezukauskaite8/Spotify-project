import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statsmodels.api as sm
from styling import apply_design, theme_plotly

apply_design()

db_path = os.path.join('data', 'spotify_cleaned.db')
connection = sqlite3.connect(db_path)

##########################################################################################################################
# Guste 

query = f"SELECT * FROM artist_data"

cursor = connection.cursor()
cursor.execute(query)

rows = cursor.fetchall()
data = pd.DataFrame(rows, columns= [x[0] for x in cursor.description])

def unique_arists(df):
    result = df['artist_name'].nunique()
    return print(result)

def top10_followers(df):
    large10_followers = df.nlargest(10, "followers")
    return large10_followers[['artist_name', 'followers']]


def top10_popularity_chart(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    top10 = df.nlargest(10, "artist_popularity")
    ax.barh(top10['name'], top10['artist_popularity'], color='#753696')
    ax.set_title("Top 10 Artists by Popularity")
    ax.invert_yaxis()
    return fig

def top10_follower_chart(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    top10 = df.nlargest(10, "followers")
    ax.barh(top10['name'], top10['followers'], color= '#83AD6C')
    ax.set_title("Top 10 Artists by Followers")
    ax.invert_yaxis()
    return fig




##########################################################################################################################
# Talisha

def plot_circular_bars(df):
    top10 = df.nlargest(10, 'artist_popularity').copy()
    top10['followers_norm'] = (top10['followers'] / top10['followers'].max()) * 100
    labels = top10['artist_name']
    pop_values = top10['artist_popularity']
    fol_values = top10['followers_norm']

    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)
    width = (2 * np.pi) / num_vars / 3

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.bar(angles, pop_values, width=width, color='skyblue', label='Popularity', alpha=0.7)
    ax.bar(angles + width, fol_values, width=width, color='purple', label='Followers (Scaled)', alpha=0.7)

    ax.set_xticks(angles + width / 2)
    ax.set_xticklabels(labels, fontsize=10)
    plt.title("Top 10 Artists: Popularity vs Followers", va='bottom')
    plt.legend(loc='upper right')
    return fig

def scatterplot_popularity(df):
    top25 = df.nlargest(25, 'artist_popularity')
    plt.figure(figsize=(12, 8))
    plt.scatter(top25['followers'], top25['artist_popularity'], color='purple')
    for i, row in top25.iterrows():
        plt.annotate(row['artist_name'], (row['followers'], row['artist_popularity']),
                     fontsize=9, alpha=0.7)
    plt.xscale('log')

    plt.title("Top 25 Artists: Popularity vs. Followers ")
    plt.xlabel("Followers ")
    plt.ylabel("Popularity")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.show()




##########################################################################################################################
# Guste
# Analysis of popularity regarding the collaborations
# AI usage: fixing query, syntax mistakes

query_collabs = """
SELECT 
    album_popularity,
    CASE 
        WHEN artist_1 IS NOT NULL AND artist_1 != '' THEN 'Collaboration' 
        ELSE 'Solo' 
    END AS track_type
FROM albums_data
"""
cursor.execute(query_collabs)
rows = cursor.fetchall()
df_counts = pd.DataFrame(rows, columns=['album_popularity','track_type'])


# Count of Solo VS Collaborations
type_counts = df_counts['track_type'].value_counts()

print("\nNumber of Collaborations VS Solo tracks:")
print(type_counts)

plt.figure(figsize = (8, 6))
type_counts.plot(kind = 'bar', color = ['purple', 'skyblue'], alpha = 0.8)

plt.title('Solo Tracks vs. Collaborations', fontsize = 14)
plt.xlabel('Track Type')
plt.ylabel('Number of Tracks')
plt.xticks(rotation = 0)
plt.grid(axis = 'y', linestyle = '--', alpha = 0.6)

plt.tight_layout()
plt.show()


# Popularity analysis
popularity_analysis = df_counts.groupby('track_type')['album_popularity'].mean()

print("\nComaprison of popularity of track types")
print(popularity_analysis)

plt.figure(figsize=(8, 6))
popularity_analysis.plot(kind = 'bar', color = ['purple','skyblue'], alpha = 0.8)

plt.title('Album popularity: Solo VS Collaborations', fontsize = 14)
plt.xlabel('Track Type')
plt.ylabel('Average Album Popularity')
plt.xticks(rotation = 0)
plt.grid(axis = 'y', linestyle = '--', alpha = 0.6)

plt.tight_layout()
plt.show()




##########################################################################################################################
# Mia
#Monthly aggregation based on popularity instead of streams
# Help from AI to merge the dataframes

df_tracks = pd.read_sql_query("SELECT id, track_popularity FROM tracks_data", connection)
df_dates = pd.read_sql_query("SELECT track_id, track_name, release_date FROM albums_data", connection)

df_monthly = pd.merge(df_tracks, df_dates, left_on='id', right_on='track_id')

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





##########################################################################################################################
# Talisha
# All time favorites

query_timeless = """
SELECT 
    a.track_name, 
    r.name AS artist_name,
    a.album_popularity,
    r.artist_popularity, 
    a.release_date
FROM albums_data a
JOIN artist_data r ON a.artist_id = r.id
"""

df_timeless = pd.read_sql_query(query_timeless, connection)
df_timeless['release_date'] = pd.to_datetime(df_timeless['release_date'], errors='coerce')
df = df_timeless.dropna(subset=['release_date'])
df_filtered = df.loc[(df['release_date'] <= '1990-01-01')]
df_alltimers = df_filtered.nlargest(20, 'album_popularity')
print(df_alltimers[['track_name', 'artist_name', 'album_popularity']])





##########################################################################################################################
# Talisha
# Ouliers analysis
#AI: Filtering only artist with existing artist data entry

query_breakout = """
SELECT 
    a.track_name, 
    a.album_popularity, 
    r.artist_popularity
FROM albums_data a
INNER JOIN artist_data r ON a.artist_id = r.id
WHERE r.artist_popularity > 0
"""

df_breakout = pd.read_sql_query(query_breakout, connection)
df_breakout['pop_gap'] = df_breakout['album_popularity'] - df_breakout['artist_popularity']

top_breakouts = df_breakout.nlargest(20, ['pop_gap'])

print(top_breakouts[['track_name', 'artist_popularity', 'album_popularity', 'pop_gap']])
print("Average popularity gap:")
print(df_breakout['pop_gap'].mean())




##########################################################################################################################
# Guste
#Spotify popularity is determined on a scale from 1 to 100 and is time=sensitive, 
#while followers accumulate over time. Are both relevant statistics in their own right?
#Investigate the relation between them.

#Included AI: checking for mistakes (log1p, syntax)
def relation_popularity_followers(df):
    X = np.log1p(df["followers"])
    Y = df["artist_popularity"]

    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    print(model.summary())

    sns.regplot(x = np.log1p(df["followers"]), y = df["artist_popularity"], line_kws = {"color": "darkmagenta"})
    plt.xlabel("log(Followers + 1)")
    plt.ylabel("Popularity")
    plt.title("Popularity VS Logarithm of Followers")
    plt.show()

def over_performers(df):
    # 1. Deduplicate: One row per artist with their max stats
    # We filter for popularity > 5 to remove 'junk' uploads like 'dumbbb...'
    df_unique = df[df['artist_popularity'] > 5].groupby('artist_name').agg({
        'followers': 'max',
        'artist_popularity': 'max'
    }).reset_index()

    # 2. Run Regression on unique artists
    X = np.log1p(df_unique["followers"])
    Y = df_unique["artist_popularity"]
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    
    df_unique["residual"] = model.resid
    
    # 3. Return Top 3 unique over-performers
    return df_unique.sort_values(by="residual", ascending=False).head(3)[["artist_name", "artist_popularity", "followers"]]



def legacy_artists(df):
    # 1. Deduplicate: One row per artist
    # We filter followers > 1000 so we only look at established artists
    df_unique = df[df['followers'] > 1000].groupby('artist_name').agg({
        'followers': 'max',
        'artist_popularity': 'max'
    }).reset_index()

    # 2. Run Regression
    X = np.log1p(df_unique["followers"])
    Y = df_unique["artist_popularity"]
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    
    df_unique["residual"] = model.resid
    
    # 3. Return Top 3 unique legacy artists
    return df_unique.sort_values(by="residual", ascending=True).head(3)[["artist_name", "artist_popularity", "followers"]]


##########################################################################################################################
#Mia
# Artist Tier popularity and Folowers
def plot_artist_tiers(df):

    bins = [0, 1000, 10000, 100000, 1000000, float('inf')]
    labels = ['Garage', 'Local', 'Regional', 'National', 'Global']
    df['Artist_Tier'] = pd.cut(df['followers'], bins=bins, labels=labels)

    # 2. Calculate the average popularity per tier
    tier_means = df.groupby('Artist_Tier', observed=True)['artist_popularity'].mean()


    plt.figure(figsize=(10, 6))
    tier_means.plot(kind='bar', color='skyblue', edgecolor='black')
    
    plt.title("Executive Insight: Average Popularity Across Artist Tiers")
    plt.xlabel("Artist Market Tier (Based on Followers)")
    plt.ylabel("Average Popularity Score (0-100)")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout() 
    plt.show()


if __name__ == "__main__":  
    plot_artist_tiers(data)
    scatterplot_popularity(data)
    plot_circular_bars(data)
    print(top10_followers(data))


connection.close()
















