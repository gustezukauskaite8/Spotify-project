import pandas as pd
import matplotlib.pyplot as plt

file = pd.read_csv('artist_data.csv')

def top10popularity(x):
    data = file.nlargest(10,"artist_popularity")
    print(data[['name','artist_popularity']])

def top10followers(x):
    data = file.nlargest(10,"followers")
    print(data[['name','followers']])


def top10_by_genre(genre, sort_by):
    genre_cols = ['genre_0','genre_1','genre_2','genre_3','genre_4','genre_5','genre_6']
    filtered = file[file[genre_cols].eq(genre).any(axis=1)]
    top10 = filtered.nlargest(10, sort_by)
    print(top10[['name', sort_by]])

top10popularity(file)
top10followers(file)
top10_by_genre("comedy","artist_popularity")
