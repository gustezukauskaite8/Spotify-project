import pandas as pd

df = pd.read_csv('data/artist_data.csv')

def unique_artists(df):
    result = df['name'].nunique()
    return print(result)

def top10_followers(df):
    large10_followers = df.nlargest(10, "followers")
    return print(large10_followers)

def top10_popularity(df):
    large10_popularity = df.nlargest(10, "artist_popularity")
    return print(large10_popularity)




unique_artists(df)
top10_followers(df)
top10_popularity(df)
    
