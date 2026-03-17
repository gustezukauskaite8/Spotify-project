import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sqlite3
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from styling import apply_design, editorial_header, theme_plotly

st.set_page_config(page_title="AI Data Analyst", layout="wide")
apply_design()

editorial_header("Data Engineering Analysis", "Spotify data AI chatbot")
BRAND_COLORS = {"bg": "#83AD6C", "primary": "#753696", "secondary": "#E2B4BD", "text": "#220C10"}

# data
@st.cache_data
def load_combined_data(eras):
    all_data = []
    db_path = 'data/spotify_cleaned.db'
    
    conn = sqlite3.connect(db_path)
    era_map = {"1980s": (1980, 1989), "1990s": (1990, 1999), "2000s": (2000, 2009), "2010s": (2010, 2019), "2020s": (2020, 2029)}
    
    for era in eras:
        start, end = era_map[era]
        query = f"""
        SELECT f.*, a.album_name, a.release_date, a.track_name, r.name as artist_name, r.genre_0 as genre, r.artist_popularity
        FROM features_data f
        JOIN albums_data a ON f.id = a.track_id
        JOIN artist_data r ON a.artist_id = r.id
        WHERE CAST(SUBSTR(a.release_date, 1, 4) AS INTEGER) BETWEEN {start} AND {end}
        """
        temp_df = pd.read_sql_query(query, conn)
        temp_df = temp_df.loc[:, ~temp_df.columns.duplicated()].copy()
        temp_df['era_label'] = era 
        all_data.append(temp_df)
    conn.close()
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# sidebar with form structure
with st.sidebar:
    st.title(" Filter the Context")
    
    with st.form("filter_setup"):
        era_choices = st.multiselect(
            "Select Eras", 
            ["1980s", "1990s", "2000s", "2010s", "2020s"], 
            default=["1980s"]
        )
        artist_input = st.text_input("Focus on Artist (Optional)", value="All Artists")
        
        run_button = st.form_submit_button("Run Analysis")


if run_button:
    st.session_state['active_eras'] = era_choices
    st.session_state['active_artist'] = artist_input
    st.session_state['data_loaded'] = True


if st.session_state.get('data_loaded'):
    final_df = load_combined_data(st.session_state['active_eras'])
    
    artist_filter = st.session_state['active_artist']
    if artist_filter != "All Artists":
        final_df = final_df[final_df['artist_name'] == artist_filter].copy()
    #prove the AI is using the correct dataset
    st.write(f"Data Active: **{', '.join(st.session_state['active_eras'])}** | Total Rows: **{len(final_df)}**")

    # agent logic
    def create_agent(df):
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # only version that really worked
            google_api_key=st.secrets["GOOGLE_API_KEY"],
            temperature=0
        )

        actual_columns = ", ".join(df.columns.tolist())
        #AI usage: to help finish the prompt
        prefix = f"""
        You are a professional Spotify Data Consultant and Data Engineer.
        
        COLUMNS: {actual_columns}
        
        PROTOCOL:
        1. Use 'df'. Use 'artist_name', 'track_name', and 'genre'.
        2. Visuals: Bg: '{BRAND_COLORS['bg']}', Primary: '{BRAND_COLORS['primary']}'.
        3. Use plt/sns if you need to make a plot. Do not call st.pyplot().
        4. Provide a clear text 'Final Answer'.
        5. IMPORTANT: Your Final Answer must be a human-readable summary ONLY. 
           Do NOT include any Python code, 'import' statements, or backticks (```) in your final response. 
           The user cannot run code; they only want the answer and the chart if that helps you support the answer. DO NOT make a plot if this wasnt asked. 
           In this case, give a more explicit answer, so explain roughly what you did to make the conclusion. 
           DONT MAKE A CHART UNLESS ASKED
        6. stucture of answer if only text: 1 sentence summary, 2–4 key stats, 1 comparison or interpretation, 1 takeaway
        """
        #allow_dangerous_code is nessesary to run the python code created by llm
        return create_pandas_dataframe_agent(
            llm, df, verbose=True, allow_dangerous_code=True, 
            prefix=prefix, agent_type="tool-calling", 
            extra_vars={"plt": plt, "pd": pd, "sns": sns, "st": st, "np": np}
        )

    st.subheader("What would you like to know?")
    question = st.text_input("Example: 'Who are the most popular artists' or 'What artist has the highest tempo tracks'")

    if question:
        plt.close('all')
        plt.clf()
        
        if final_df.empty:
            st.error("No data found for current filters.")
        else:
            agent = create_agent(final_df)
            with st.spinner(f"Analyzing {len(final_df)} rows..."):
                try:
                    response = agent.invoke({"input": f"{question}. Answer in plain text and draw a chart if relevant."})
                    answer = response.get("output", "")
                
                    fig = plt.gcf()
                    
                    st.write("### Analysis Result:")
        
                    if answer:
                        if isinstance(answer, list):
                            answer = " ".join([str(i.get('text', '')) if isinstance(i, dict) else str(i) for i in answer])
                        st.markdown(f"<p style='color:{BRAND_COLORS['text']}; font-size:1.1rem;'>{answer}</p>", unsafe_allow_html=True)
                    
                    if len(fig.get_axes()) > 0:
                        fig.set_facecolor(BRAND_COLORS['bg'])
                        for ax in fig.get_axes():
                            ax.set_facecolor('white')
                        st.pyplot(fig, use_container_width=True)
                        plt.close(fig)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
else:
    st.info(" Set your eras and click **'Run Analysis'** in the sidebar to load the data.")
    st.stop()