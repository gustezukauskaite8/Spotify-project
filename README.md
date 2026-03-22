# Spotify Data Analysis Dashboard
## Overview

This repository contains Python scripts used to clean, analyze, and visualize Spotify data stored in a SQLite database (data/spotify_database.db). The project explores patterns in music features, genres, popularity, artists, and albums, and presents insights through analyses and a Streamlit dashboard.

## Main Components

### Cleaning_all.py
Cleans the raw Spotify database by removing missing or invalid records, standardizing artist names, fixing ID mappings, and preparing a cleaned dataset for analysis.

### Analysis_eras.py / Talisha_Eras_Profiling.py
Analyzes music characteristics across decades. Creates heatmaps and bar charts showing how audio features such as energy, danceability, and valence evolve over time.

### Analysis_features.py / CHOSEN_analysis_features.py
Explores track-level audio features. Includes feature distributions, correlations, popularity analysis, mood quadrants (valence vs energy), and identification of artists that dominate top feature values.

### Analysis_genres.py
Examines genre patterns, including feature profiles of common and popular genres and combinations of genres that frequently appear together.

### Analysis_popularity.py
Investigates artist and track popularity. Includes follower analysis, collaboration vs. solo comparisons, popularity trends, regression analysis, and artist tier classification.

### CHOSEN_analysis_album.py
Performs album-level analysis and supports interactive exploration using Streamlit. Users can search for albums and view summaries of their audio features.

## Streamlit Dashboard Tabs

### TAB_artists.py
Interactive artist dashboard showing top songs, genre information, average audio features (radar chart), and a timeline of album releases.

### TAB_features_talisha.py
Feature analysis dashboard where users can explore trends, top songs, correlations, and global averages for selected audio features.

### TAB_genres_guste.py
Genre analysis dashboard that displays genre statistics, top artists and songs, feature profiles, genre combinations, and popularity comparisons.

### AI analyst.py (BETA)
This dashboard features an integrated AI chatbot that acts as an Spotify data consultant/analyst. It allows users to ask questions about the data in natural language. It is powered by the Gemini 2.5 Flash engine via the LangChain pandas_dataframe_agent. This agent receives a filtered dataset based on the users choices. It then takes a question as input and converts it to Python code to perform computations, analysis and visualisation in real time. 
#### Important! BETA
This feature is currently in Beta. As an LLM based tool, it may occasionally hallucinate or provide incorrect statistical interpretations. This chatbot was tested enough to work as an extra feature for the dashboard. 
