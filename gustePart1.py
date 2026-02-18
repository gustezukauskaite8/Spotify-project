import pandas as pd 
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv("artist_data.csv")

#how many unique artists there are in the dataset
#determine the top 10 artists both by popularity and by number of followers. 
#Display the results in a suitable graph.

def unique_artists(df):
    result = df["name"].unique()
    return result

def top_10_popularity(df):
    artists = df.nlargest(10, "artist_popularity")
    return artists

def top_10_followers(df):
    artists = df.nlargest(10, "followers")
    return artists

#finish!
def top_10_chart(df):
    artists_popularity = top_10_popularity(df)
    artists_followers = top_10_followers(df)

print(len(unique_artists(data)))

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
    X = np.log1p(df["followers"])
    Y = df["artist_popularity"]

    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    df["residual"] = model.resid
    over_performers = df.sort_values(by = "residual", ascending = False).head(10)
    print("\n Over-Performers (High Popularity - Low Followers)")
    print(over_performers[["name", "artist_popularity", "followers"]])

def legacy_artists(df):
    X = np.log1p(df["followers"])
    Y = df["artist_popularity"]

    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    df["residual"] = model.resid
    legacy_artist = df.sort_values(by = "residual", ascending = True).head(10)
    print("\n Legacy artists (Low Popularity - High Followers)")
    print(legacy_artist[["name", "artist_popularity", "followers"]])

