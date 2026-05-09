import streamlit as st
import pandas as pd
import plotly.express as px
from sql_queries import PatentQueries
import os

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Live",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Query Engine
@st.cache_resource
def get_queries():
    return PatentQueries()

# Data fetching with caching
@st.cache_data(ttl=600) # Cache for 10 minutes
def fetch_all_data():
    q = get_queries()
    return {
        "companies": q.q2_top_companies(10),
        "inventors": q.q1_top_inventors(10),
        "countries": q.q3_top_countries(),
        "trends": q.q4_trends_over_time(),
        "recent": q.q5_join_query(15)
    }

# App Header
st.title("🛡️ GLOBAL PATENT INTELLIGENCE")
st.subheader("Live Analytics & Innovation Tracking")
st.markdown("---")

try:
    with st.spinner("Connecting to Railway MySQL..."):
        data = fetch_all_data()

    # --- KPI Metrics Row ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_patents = data["trends"]["patent_count"].sum() if not data["trends"].empty else 0
    total_cos = len(data["companies"])
    total_inv = len(data["inventors"])
    growth = data["trends"]["yoy_growth"].iloc[0] if not data["trends"].empty else 0

    with col1:
        st.metric("Total Patents", f"{total_patents:,}")
    with col2:
        st.metric("Top Companies", total_cos)
    with col3:
        st.metric("Top Inventors", total_inv)
    with col4:
        st.metric("YoY Growth", f"{growth}%" if growth else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Visualizations Row 1 ---
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.write("#### 🏢 Top Innovative Companies")
        fig_cos = px.bar(
            data["companies"], 
            x="patent_count", 
            y="name", 
            orientation='h',
            color="patent_count",
            color_continuous_scale="Viridis",
            labels={"patent_count": "Patents", "name": "Company"}
        )
        fig_cos.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=400)
        st.plotly_chart(fig_cos, use_container_width=True)

    with row1_col2:
        st.write("#### 📅 Filing Trends Over Time")
        fig_trends = px.area(
            data["trends"].sort_values("year"), 
            x="year", 
            y="patent_count",
            labels={"patent_count": "Patents", "year": "Year"},
            color_discrete_sequence=["#00CC96"]
        )
        fig_trends.update_layout(height=400)
        st.plotly_chart(fig_trends, use_container_width=True)

    # --- Visualizations Row 2 ---
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.write("#### 🌍 Global Distribution (Top 10 Countries)")
        fig_geo = px.pie(
            data["countries"].head(10), 
            values="patent_count", 
            names="country",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    with row2_col2:
        st.write("#### 👨‍🔬 Leading Inventors")
        fig_inv = px.bar(
            data["inventors"], 
            x="name", 
            y="patent_count",
            color="patent_count",
            labels={"patent_count": "Patents", "name": "Inventor"}
        )
        st.plotly_chart(fig_inv, use_container_width=True)

    # --- Data Explorer ---
    st.markdown("---")
    st.write("#### 🔍 Recent Patent Filings & Relationships")
    st.dataframe(data["recent"], use_container_width=True)

except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    st.info("Ensure your MYSQL_URL is correctly set in your environment variables.")

st.markdown("---")
st.caption("Data Source: PatentsView • Backend: Railway MySQL • UI: Streamlit")
