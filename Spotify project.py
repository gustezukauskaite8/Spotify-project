
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px



data = pd.read_csv('data/artist_data.csv')

def unique_arists(df):
    result = df['name'].nunique()
    return print(result)

def top10_followers(df):
    large10_followers = df.nlargest(10, "followers")
    return large10_followers[['name', 'followers']]

def top10_popularity(df):
    large10_popularity = df.nlargest(10, "artist_popularity")
    return large10_popularity[['name', 'artist_popularity']]

def topfollow_barcharts(df):
    largest_followers_plot= top10_followers(df).plot(kind="bar")
    return largest_followers_plot




def plot_circular_bars(df):
    top10 = df.nlargest(10, 'artist_popularity').copy()
    top10['followers_norm'] = (top10['followers'] / top10['followers'].max()) * 100
    labels = top10['name']
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
    plt.show()

def scatterplot_popularity(df):
    top25 = df.nlargest(25, 'artist_popularity')
    plt.figure(figsize=(12, 8))
    plt.scatter(top25['followers'], top25['artist_popularity'], color='purple')
    for i, row in top25.iterrows():
        plt.annotate(row['name'], (row['followers'], row['artist_popularity']),
                     fontsize=9, alpha=0.7)
    plt.xscale('log')

    plt.title("Top 25 Artists: Popularity vs. Followers ")
    plt.xlabel("Followers ")
    plt.ylabel("Popularity")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.show()


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
        for i in range(0, 6):
            column_name = f'genre_{i}'
            if column_name in row and pd.notna(row[column_name]):
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

plot_artist_tiers(data)


scatterplot_popularity(data)
#plot_circular_bars(data)
#print(top10_followers(data))
#print(topfollow_barcharts(data))
#data = genre_count(data)
#print(top10_genre('pop',data))
#plot_genre_boxplot(data) 