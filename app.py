import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Spotify Dashboard", layout="wide")

# --- 1. THE DIAGNOSTIC TEST ---
def run_db_diagnostic():
    db_path = 'data/spotify_database.db'
    st.sidebar.subheader("Connection Diagnostics")
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        st.sidebar.write(f"✅ Found Tables: `{tables}`")
        
        # Get column names for 'artist_data'
        if 'artist_data' in tables:
            cursor.execute("PRAGMA table_info(artist_data);")
            columns = [col[1] for col in cursor.fetchall()]
            st.sidebar.write(f"✅ Found Columns: `{columns}`")
        else:
            st.sidebar.error("❌ Table 'artist_data' NOT found in DB!")
            
        conn.close()
    else:
        st.sidebar.error(f"❌ Database file not found at: {db_path}")

# Run the test in the sidebar so it's always visible while you develop
run_db_diagnostic()

# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    conn = sqlite3.connect('data/spotify_database.db')
    try:
        df = pd.read_sql_query("SELECT * FROM artist_data", conn)
        return df
    except Exception as e:
        st.error(f"SQL Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

data = load_data()

# --- 3. THE "WHAT AM I SEEING?" TEST ---
with st.expander("🔍 Inspect Raw Data Schema (Debug)"):
    if not data.empty:
        st.write("### DataFrame Info")
        st.write(f"Total Rows: {len(data)}")
        st.write("Column Names Found by Pandas:")
        st.json(list(data.columns))
        st.write("First 5 rows of data:")
        st.dataframe(data.head())
    else:
        st.warning("DataFrame is currently empty.")

# --- 4. MAIN APP LOGIC ---
st.title("🎵 Spotify Artist Analytics")

if not data.empty:
    # Use a case-insensitive check to be safe
    cols_lower = [c.lower() for c in data.columns]
    
    if 'artist_popularity' in cols_lower:
        # Find the actual case-sensitive name
        idx = cols_lower.index('artist_popularity')
        real_col_name = data.columns[idx]
        
        min_pop = st.slider("Select Min Popularity", 0, 100, 50)
        filtered = data[data[real_col_name] >= min_pop]
        st.success(f"Showing {len(filtered)} artists")
        st.dataframe(filtered)
    else:
        st.error("The column 'artist_popularity' is missing from the database.")
        st.info(f"Available columns are: {list(data.columns)}")