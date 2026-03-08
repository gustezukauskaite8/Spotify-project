import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def load_features_data():
    conn = sqlite3.connect('data/spotify_database.db')
    query = """
    SELECT 
        a.release_date, 
        a.track_name, 
        t.track_popularity,
        f.danceability, f.energy, f.acousticness, f.valence, f.speechiness, f.loudness, f.tempo, f.key, f.instrumentalness, f.liveness
    FROM albums_data a
    JOIN tracks_data t ON a.track_id = t.id
    JOIN features_data f ON a.track_id = f.id
    """
    df = pd.read_sql(query, conn)
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['year'] = df['release_date'].dt.year
    conn.close()
    return df
df = load_features_data()
st.sidebar.title("Feature Analysis")
features_list = ['danceability', 'energy', 'acousticness', 'valence', 'speechiness', 'tempo', 'key', 'instrumentalness', 'liveness']
selected_feature = st.sidebar.selectbox("Select a Feature", features_list)

st.header(f"Analysis of {selected_feature.capitalize()}")


avg_score = df[selected_feature].mean()
st.metric(label=f"Global Average {selected_feature.capitalize()}", value=f"{avg_score:.3f}")

st.subheader(f"Top 5 Songs: Highest {selected_feature.capitalize()}")
top_5_features = df.nlargest(5, selected_feature)[['track_name', selected_feature, 'track_popularity']]
st.table(top_5_features.reset_index(drop=True))

st.subheader("Feature Evolution Over Time")
evolution = df.groupby('year')[selected_feature].mean().reset_index()
fig_line = px.line(evolution, x='year', y=selected_feature, title=f"{selected_feature} Trends (1960-2023)")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader(f"Correlation: {selected_feature.capitalize()} vs Others")


corr_matrix = df[features_list].corr()
feature_corr = corr_matrix[[selected_feature]].sort_values(by=selected_feature, ascending=False)
fig_heat, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(feature_corr, annot=True, cmap='coolwarm', center=0, ax=ax)
ax.set_title(f"How {selected_feature} correlates with other features")
st.pyplot(fig_heat)