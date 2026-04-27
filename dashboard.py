import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stMetric {
        background-color: #1e212b;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    h1, h2, h3 {
        color: #FFFFFF;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    @media (prefers-color-scheme: light) {
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
        }
        [data-testid="stMetricLabel"] * {
            color: #FFFFFF !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("GLOBAL PATENT INTELLIGENCE DASHBOARD")
st.markdown("### Analyzing Innovation Trends & Key Players ")
st.markdown("---")

# Data loading with caching
@st.cache_data
def load_data(filename):
    file_path = os.path.join("output", filename)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    # Return empty DataFrame if file doesn't exist
    return pd.DataFrame()

# Load all CSVs
df_patents = load_data("clean_patents.csv")
df_top_companies = load_data("top_companies.csv")
df_top_inventors = load_data("top_inventors.csv")
df_top_countries = load_data("top_countries.csv")
df_yearly_trends = load_data("yearly_trends.csv")

# Ensure we have data
if df_top_companies.empty or df_top_inventors.empty:
    st.error("Data files not found! Please run the ETL pipeline first using `python run_pipeline.py`.")
    st.stop()

# --- KPI Metrics Row ---
col1, col2, col3, col4 = st.columns(4)
total_patents = len(df_patents) if not df_patents.empty else df_yearly_trends['patent_count'].sum() if 'patent_count' in df_yearly_trends.columns else 100
total_companies = len(df_top_companies)
total_inventors = len(df_top_inventors)

# Handle NaN in growth (happens if we only have 1 year of data in the sample)
if not df_yearly_trends.empty and 'yoy_growth' in df_yearly_trends.columns:
    val = df_yearly_trends['yoy_growth'].iloc[0]
    top_growth = f"{val:.1f}%" if pd.notna(val) else "N/A"
else:
    top_growth = "N/A"

with col1:
    st.metric("Total Patents Analyzed", f"{total_patents:,}")
with col2:
    st.metric("Companies Tracked", f"{total_companies:,}")
with col3:
    st.metric("Inventors Found", f"{total_inventors:,}")
with col4:
    st.metric("Latest YoY Growth", top_growth)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Row 1 ---
colA, colB = st.columns(2)

with colA:
    st.subheader(" Top Innovative Companies")
    if 'name' in df_top_companies.columns and 'patent_count' in df_top_companies.columns:
        st.bar_chart(data=df_top_companies.set_index('name')['patent_count'])
    
with colB:
    st.subheader(" Top Inventors")
    if 'name' in df_top_inventors.columns and 'patent_count' in df_top_inventors.columns:
        st.bar_chart(data=df_top_inventors.set_index('name')['patent_count'])

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Row 2 ---
colC, colD = st.columns(2)

with colC:
    st.subheader(" Leading Countries by Innovation")
    if 'country' in df_top_countries.columns and 'patent_count' in df_top_countries.columns:
        # Use a bar chart as mapping isn't cleanly supported without lat/lon
        st.bar_chart(data=df_top_countries.set_index('country')['patent_count'])

with colD:
    st.subheader(" Patent Filing Trends Over Time")
    if 'year' in df_yearly_trends.columns and 'patent_count' in df_yearly_trends.columns:
        st.line_chart(data=df_yearly_trends.set_index('year')['patent_count'])

# --- Data Table View ---
st.markdown("---")
st.subheader(" Raw Data Explorer")
tab1, tab2, tab3 = st.tabs(["Top Companies Details", "Inventor Analytics", "Country Data"])

with tab1:
    st.dataframe(df_top_companies, use_container_width=True)
with tab2:
    st.dataframe(df_top_inventors, use_container_width=True)
with tab3:
    st.dataframe(df_top_countries, use_container_width=True)

st.caption("Data source: USPTO / PatentDataPipeline • Powered by Streamlit")
