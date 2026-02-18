import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm

# 1. Page Configuration (Looks professional for "Spotify Owners")
st.set_page_config(page_title="Spotify Executive Radar", layout="wide")

st.title("🎵 Spotify 2023 Strategy Dashboard")
st.markdown("---")

# 2. Data Loading (Use a sample or your actual file)
@st.cache_data # This keeps the app fast
def load_data():
    df = pd.read_csv(r'C:\Users\miaen\OneDrive\DE\Spotify\Spotify-project\data\artist_data.csv')
    # Basic Cleaning
    df['log_followers'] = np.log10(df['followers'] + 1)
    return df

data = load_data()

# 3. Sidebar Navigation (Satisfies "Ease of Use" rubric)
st.sidebar.header("Filter Options")
min_pop = st.sidebar.slider("Minimum Popularity", 0, 100, 50)
selected_data = data[data['artist_popularity'] >= min_pop]

# 4. The Regression Logic
X = sm.add_constant(selected_data['log_followers'])
y = selected_data['artist_popularity']
model = sm.OLS(y, X).fit()
selected_data['residual'] = model.resid

# 5. Dashboard Layout: Columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Popularity vs. Followers (OLS)")
    # Using Plotly for interactivity (Hover to see names!)
    fig = px.scatter(selected_data, x="log_followers", y="artist_popularity", 
                     hover_name="name", color="residual",
                     color_continuous_scale="RdYlGn",
                     title="Model Residuals: Green = Overperforming")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🚀 The Viral Radar (Creative Insight)")
    # Showing over-performers (high residuals)
    over_performers = selected_data.nlargest(10, 'residual')[['name', 'artist_popularity', 'followers']]
    st.write("Top 10 Artists Outperforming their Fanbase:")
    st.table(over_performers)

# 6. Extra Feature: Genre Analysis
st.subheader("Genre Market Share")
# You'd use your 'Melt' logic here to show a Treemap!