import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
from ANALYSIS_popularity import top10_followers, legacy_artists, over_performers
import numpy as np
import plotly.express as px
import statsmodels.api as sm
from styling import apply_design, editorial_header, theme_plotly


st.set_page_config(layout="wide", page_title="Eras Overview Dashboard")
apply_design()

BRAND_COLORS = {"bg": "#83AD6C", "primary": "#753696", "text": "#220C10"}
brand_pie_colors = [
    "#5E2B78",  
    "#753696",  
    "#9B6BB8",  
    "#C98FA8",  
    "#E2B4BD",  
    "#D8A7B4",  
    "#A8C98F",  
    "#83AD6F",  
    "#6F8F5B",  
    "#220C10"   
]

@st.cache_data
def load_era_data(eras):
    all_data = []
    db_path = 'data/spotify_cleaned.db' 

    conn = sqlite3.connect(db_path)

    era_map = {
        "1980s": (1980, 1989), 
        "1990s": (1990, 1999), 
        "2000s": (2000, 2009), 
        "2010s": (2010, 2019), 
        "2020s": (2020, 2029)
    }
    
    for era in eras:
        start, end = era_map[era]
        query = f"""
        SELECT 
            f.*, 
            a.album_name, a.release_date, a.track_name, 
            r.name as artist_name, r.genre_0 as genre, r.artist_popularity, r.followers
        FROM features_data f
        JOIN albums_data a ON f.id = a.track_id
        JOIN artist_data r ON a.artist_id = r.id
        WHERE CAST(SUBSTR(a.release_date, 1, 4) AS INTEGER) BETWEEN {start} AND {end}
        """
        temp_df = pd.read_sql_query(query, conn)
        temp_df['era_label'] = era 
        all_data.append(temp_df)
    
    conn.close()
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()


st.sidebar.title("Filter the Context")
era_choices = st.sidebar.multiselect(
    "Select Eras to Display", 
    ["1980s", "1990s", "2000s", "2010s", "2020s"], 
    default=["2010s"]
)

editorial_header("Data Engineering Analysis", "Spotify Eras Dashboard")

if era_choices:

    final_df = load_era_data(era_choices)

    all_eras = ["1980s", "1990s", "2000s", "2010s", "2020s"]
    full_df = load_era_data(all_eras)
    current_artists = set(final_df['artist_name'].unique())
        
       
    current_min_year = final_df['release_date'].str.slice(0, 4).astype(int).min()
        
        
    full_df['release_year'] = full_df['release_date'].str.slice(0, 4).astype(int)
    past_artists = set(full_df[full_df['release_year'] < current_min_year]['artist_name'].unique())
        
       
    new_artists = current_artists - past_artists
    num_new = len(new_artists)
    
    if not final_df.empty:
        st.write(f"Showing analysis for: **{', '.join(era_choices)}** ({len(final_df)} tracks found)")
        
       
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # top 10 artists based on popularity
            st.subheader("Top 10 Artists by Popularity")

            artist_stats = final_df.groupby('artist_name').agg({'artist_popularity': 'max'}).reset_index()

            top_10_followers = artist_stats.sort_values(by='artist_popularity', ascending=False).head(10)
            top_10_followers.columns = ['Artist', 'Popularity']

            st.table(top_10_followers.reset_index(drop=True))

        with col2:
            #Regression used in part 1 of the Assignment
            st.divider()
            st.header("Executive Regression Analysis")
            col_stars, col_legacy = st.columns(2)

            with col_stars:
                st.subheader(" Rising Stars")
                st.caption("High Popularity vs. Low Follower Count ")
    
                stars_df = over_performers(final_df)
    
                stars_df.columns = ['Artist', 'Popularity', 'Followers']
                stars_df.index = range(1, len(stars_df) + 1) 
                st.table(stars_df)

            with col_legacy:
                st.subheader(" Legacy Artists")
                st.caption("High Follower Count vs. Low Popularity ")
    
                legacy_df = legacy_artists(final_df)
    
                legacy_df.columns = ['Artist', 'Popularity', 'Followers']
                legacy_df.index = range(1, len(legacy_df) + 1)
                st.table(legacy_df)

        st.divider()

        col3, col4 = st.columns([2, 1]) 
        
        with col3:
            #Pie chart with 10 most common genres
            st.subheader("Genre Breakdown")

            genre_counts = final_df['genre'].replace('', np.nan).dropna().value_counts().reset_index()
            genre_counts.columns = ['Genre', 'Count']


            top_genres = genre_counts.head(6)

            fig_pie = px.pie(
                top_genres, 
                values='Count', 
                names='Genre',
                color_discrete_sequence=brand_pie_colors, 
                hole=0.4  
            )


            fig_pie.update_layout(
                showlegend=True,
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=BRAND_COLORS['text'])
            )

            st.plotly_chart(theme_plotly(fig_pie), use_container_width=True)
            
        with col4:
            # some statistics
            st.subheader("Quick Stats")

            st.metric("Total Unique Genres", final_df['genre'].nunique())
            st.metric("Total Number of Tracks", final_df['track_name'].count())
            ##somehow make sure if this is correct or not!!!!!!!!!!!!!!!!!
            st.metric(
                label="New Artists in this Era", 
                value=num_new, 
                help="Artists who didn't appear in any eras earlier than your current selection."
            )
            

        
        st.divider()
        avg_dance = final_df['danceability'].mean()
        avg_energy = final_df['energy'].mean()
        avg_key = final_df['key'].mean()
        avg_loudness = final_df['loudness'].mean()
        avg_mode = final_df['mode'].mean()
        avg_instrumental = final_df['instrumentalness'].mean()
        avg_liveness = final_df['liveness'].mean()
        avg_acoustic = final_df['acousticness'].mean()
        avg_valence = final_df['valence'].mean()
        avg_speech = final_df['speechiness'].mean()
        avg_tempo = final_df['tempo'].mean()

        st.divider()
        # different boxes for the features 
        st.subheader(f"Average Features for: {', '.join(era_choices)}")

        features_list = [
            ("danceability", "Danceability"), ("energy", "Energy"), 
            ("key", "Key"), ("loudness", "Loudness"), 
            ("mode", "Mode"), ("speechiness", "Speechiness"),
            ("acousticness", "Acousticness"), ("instrumentalness", "Instrumental"),
            ("liveness", "Liveness"), ("valence", "Valence"), ("tempo", "Tempo")
        ]

        all_eras = ["1980s", "1990s", "2000s", "2010s", "2020s"]
        full_df = load_era_data(all_eras)

        cols = st.columns(4)

        for i, (feat_col, feat_label) in enumerate(features_list):
            current_avg = final_df[feat_col].mean()
            era_ranks = full_df.groupby('era_label')[feat_col].mean().sort_values()
            
           # rank the era vs the current avg to determine if it is high, low etc.
            rank = (era_ranks < current_avg).sum() + 1
            
            if rank == 5:
                delta_val = " Highest"
                colour_logic = "green"
            elif rank >= 3:
                delta_val = " High"
                colour_logic = "yellow"
            elif rank >= 2:
                delta_val = "- Low"
                colour_logic = "orange"
            else:
                delta_val = "- Lowest"
                colour_logic = "red"

            
            with cols[i % 4]:
                
                display_value = f"{int(current_avg)}" if feat_col == "tempo" else f"{current_avg:.2f}"
                st.metric(
                    label=feat_label, 
                    value=display_value, 
                    delta=delta_val,
                    delta_color=colour_logic 
                )
        st.divider()
        # Line chart for number of tracks released per year in the chosen era
        st.subheader(" Annual Release Volume")
        st.caption("Total number of songs released per year across the selected eras.")

        final_df['release_year'] = pd.to_datetime(final_df['release_date'], errors='coerce').dt.year

        yearly_counts = final_df.dropna(subset=['release_year'])
        yearly_counts = yearly_counts.groupby('release_year').size().reset_index(name='Total Releases')


        fig_line = px.line(
            yearly_counts, 
            x="release_year", 
            y="Total Releases",
            markers=True,
            title="Volume of Tracks Released"
        )

        fig_line.update_traces(
            line_color=BRAND_COLORS['primary'], 
            line_width=3,
            marker=dict(size=8, color=BRAND_COLORS['text']) 
        )

        fig_line.update_layout(
            height=500, 
            hovermode="x unified",
           
            xaxis=dict(
                title="Year",
                showgrid=False,
                dtick=1
            ),
            yaxis=dict(
                title="Number of Songs",
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)'
            ),
            font=dict(color=BRAND_COLORS['text'])
        )   

        st.plotly_chart(fig_line, use_container_width=True)


    else:
        st.warning("The selected filters returned no data from the database.")
else:
    st.info("Please select at least one decade in the sidebar to populate the dashboard.")