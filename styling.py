import streamlit as st

# 1. Constants
BRAND = {
    "pink": "#E2B4BD",
    "sage": "#83AD6C",
    "dark_green": "#506E40",
    "burgundy": "#220C10",
}

def apply_design():
    """Corrected, straightforward targeting for clear inputs"""
    st.markdown(f"""
        <style>
        /* 1. Global Look */
        .stApp {{
            background-color: {BRAND['sage']};
            color: {BRAND['burgundy']};
        }}

        /* Updated Card Style to prevent overflow */
        [data-testid="stMetric"], .stPlotlyChart {{
            background: rgba(255, 255, 255, 0.2); 
            border: 1px solid {BRAND['pink']};
            border-radius: 10px;
            padding: 15px;
            overflow: hidden; /* This clips any chart edges that try to poke out */
            box-sizing: border-box;
        }}

        /* Force Plotly container to respect the box width */
        .js-plotly-plot {{
            width: 100% !important;
        }}
        .stPlotlyChart > div > div {{
            padding-bottom: 40px !important;
        }}

        /* Ensure the iframe/container respects the height */
        [data-testid="stPlotlyChart"] {{
            margin-bottom: 20px !important;
            min-height: 450px; /* Forces a minimum height so it doesn't squash */
        }}
        /* 3. Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {BRAND['dark_green']} !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {BRAND['pink']} !important;
        }}

        /* --- THE FIX for Inputs --- */
        
        /* 4. Selectors and Input Boxes: Make the container WHITE */
        [data-baseweb="select"] {{
            background-color: white !important;
            border-radius: 8px;
        }}
        
        /* 5. The Tags (Pills): Keep them PINK, but make text DARK */
        [data-baseweb="tag"] {{
            background-color: {BRAND['pink']} !important;
        }}
        [data-baseweb="tag"] span {{
            color: black !important;
        }}

        /* 6. The Cursor and Typed Text: Make it BLACK */
        .stMultiSelect input, [data-baseweb="typeahead"] {{
            color: black !important;
        }}

        /* 7. Table Styling - Making them "Pop" like cards */
        [data-testid="stTable"], [data-testid="stDataFrame"] {{
            background-color: rgba(255, 255, 255, 0.15); /* Slightly lighter than background */
            border: 2px solid {BRAND['pink']}; /* Thicker border as requested */
            border-radius: 10px;
            padding: 10px;
        }}

        /* Styling the header row of the tables */
        [data-testid="stTable"] thead tr th {{
            background-color: {BRAND['dark_green']} ;
            color: #F5F5DC ;
            font-weight: bold !important;
            border-bottom: 3px solid {BRAND['pink']} ;
        }}

        /* Making table rows slightly transparent to let sage peek through */
        [data-testid="stTable"] tbody tr {{
            background-color: transparent !important;
            color: {BRAND['burgundy']} !important;
        }}

        /* Add a hover effect to rows for interactivity */
        [data-testid="stTable"] tbody tr:hover {{
            background-color: rgba(255, 255, 255, 0.1) !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def editorial_header(kicker, title):
    """Clean, semantic header"""
    st.markdown(f"""
        <div style="border-bottom: 3px solid {BRAND['pink']}; margin-bottom: 30px;">
            <p style="text-transform: uppercase; font-size: 0.7em; margin-bottom: 0;">{kicker}</p>
            <h1 style="margin-top: 0;">{title}</h1>
        </div>
    """, unsafe_allow_html=True)

def theme_plotly(fig):
    """Minimal Plotly transparent theme"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=BRAND['burgundy'],
        colorway=[BRAND['pink'], BRAND['dark_green'], BRAND['burgundy']],
        margin=dict(t=30, b=80, l=40, r=40), 
        xaxis=dict(
            automargin=False, # This is the "magic" line
            title_standoff=20 # Pushes the "Year" title away from the axis
        ),
        autosize=True
    )
    return fig