import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Lebanon Public Transportation Dashboard",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Lebanon Public Transportation & Infrastructure Dashboard")
st.markdown("""
This interactive dashboard analyzes public transportation and infrastructure quality across Lebanon.
Use the filters below to explore different aspects of the data and discover insights.
""")

# Load your data (you'll need to upload the CSV file to your GitHub repo)
@st.cache_data
def load_data():
    # You need to replace this with the actual path to your CSV file in GitHub
    # For now, creating sample data based on your visualizations
    # IMPORTANT: Replace this with: df = pd.read_csv('public_transportation.csv')
    
    # Sample data structure based on your notebook
    np.random.seed(42)
    
    regions = ['Marjeyoun_District', 'Batroun_District', 'Zgharta_District', 'North_Governorate', 
               'Matn_District', 'Tyre_District', 'Beqaa_Governorate', 'Sidon_District']
    
    data = []
    for region in regions:
        for i in range(50):  # 50 areas per region
            data.append({
                'refArea': f'/lebanon/{region.lower()}',
                'Governorate': region,
                'The main means of public transport - buses': np.random.choice([0, 1], p=[0.9, 0.1]),
                'The main means of public transport - vans': np.random.choice([0, 1], p=[0.7, 0.3]),
                'The main means of public transport - taxis': np.random.choice([0, 1], p=[0.3, 0.7]),
                'State of the main roads - good': np.random.choice([0, 1], p=[0.8, 0.2]),
                'State of the main roads - bad': np.random.choice([0, 1], p=[0.7, 0.3]),
                'State of the secondary roads - bad': np.random.choice([0, 1], p=[0.6, 0.4]),
                'State of agricultural roads - bad': np.random.choice([0, 1], p=[0.4, 0.6]),
            })
    
    return pd.DataFrame(data)

# Load data
df = load_data()
    # Load your actual CSV file
    df = pd.read_csv('public transportation.csv')

# Interactive Feature 1: Region Selection
st.sidebar.header("🎛️ Interactive Filters")
st.sidebar.subheader("Region Selection")

available_regions = df['Governorate'].unique()
selected_regions = st.sidebar.multiselect(
    "Select regions to analyze:",
    options=available_regions,
    default=available_regions[:4]  # Show first 4 by default
)

# Interactive Feature 2: Transportation Mode Focus
st.sidebar.subheader("Transportation Analysis")
transport_focus = st.sidebar.radio(
    "Focus analysis on:",
    options=["All Transport Modes", "Buses Only", "Vans Only", "Taxis Only"]
)

# Filter data based on selections
filtered_df = df[df['Governorate'].isin(selected_regions)]

# Main Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚌 Distribution of Main Public Transportation Modes")
    
    # Calculate transport mode totals for selected regions
    transport_modes = {
        'Buses': filtered_df['The main means of public transport - buses'].sum(),
        'Vans': filtered_df['The main means of public transport - vans'].sum(),
        'Taxis': filtered_df['The main means of public transport - taxis'].sum()
    }
    
    # Remove modes with zero values
    transport_modes = {k: v for k, v in transport_modes.items() if v > 0}
    
    if transport_modes:
        fig1 = px.pie(
            values=list(transport_modes.values()),
            names=list(transport_modes.keys()),
            title='Public Transportation Distribution in Selected Regions',
            color_discrete_sequence=['#e74c3c', '#9b59b6', '#1abc9c'],
            hole=0.4
        )
        
        fig1.update_traces(
            textposition='inside',
            textinfo='percent+label+value',
            textfont_size=12
        )
        
        fig1.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Show insights
        dominant_mode = max(transport_modes, key=transport_modes.get)
        st.info(f"**Dominant Transport Mode**: {dominant_mode} ({transport_modes[dominant_mode]} areas)")
    else:
        st.warning("No transportation data available for selected regions.")

with col2:
    st.subheader("🛣️ Road Quality by Region")
    
    # Calculate average road quality scores by region
    road_quality = filtered_df.groupby("Governorate")["State of the main roads - good"].mean().reset_index()
    road_quality = road_quality.sort_values("State of the main roads - good", ascending=False)
    
    if not road_quality.empty:
        fig2 = px.bar(
            road_quality,
            x="Governorate",
            y="State of the main roads - good",
            title="Good Main Roads by Region",
            labels={"Governorate": "Region", "State of the main roads - good": "Quality Score"}, 
            text="State of the main roads - good",
            color="State of the main roads - good",
            color_continuous_scale="RdYlGn"
        )
        
        fig2.update_traces(texttemplate='%{text:.2f}', textposition="outside")
        fig2.update_layout(
            height=400,
            showlegend=False,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Show insights
        best_region = road_quality.iloc[0]['Governorate']
        best_score = road_quality.iloc[0]['State of the main roads - good']
        st.success(f"**Best Roads**: {best_region} (Score: {best_score:.2f})")
    else:
        st.warning("No road quality data available for selected regions.")

# Additional Analysis Row
st.subheader("📊 Infrastructure Problem Analysis")

col3, col4 = st.columns(2)

with col3:
    st.subheader("🚨 Infrastructure Priority Matrix")
    
    # Calculate infrastructure problems
    infrastructure_problems = []
    infrastructure_mapping = {
        'Main Roads': 'State of the main roads - bad',
        'Secondary Roads': 'State of the secondary roads - bad',
        'Agricultural Roads': 'State of agricultural roads - bad'
    }
    
    for service, bad_col in infrastructure_mapping.items():
        if bad_col in filtered_df.columns:
            bad_count = filtered_df[bad_col].sum()
            total_areas = len(filtered_df)
            if total_areas > 0:
                problem_percentage = (bad_count / total_areas) * 100
                infrastructure_problems.append({
                    'Service': service,
                    'Problem_Severity': problem_percentage,
                    'Areas_Affected': bad_count
                })
    
    if infrastructure_problems:
        problem_df = pd.DataFrame(infrastructure_problems)
        problem_df = problem_df.sort_values('Problem_Severity', ascending=True)
        
        fig3 = px.bar(
            problem_df,
            x='Problem_Severity',
            y='Service',
            orientation='h',
            title='Infrastructure Issues by Severity',
            labels={
                'Problem_Severity': 'Percentage of Areas with Poor Service (%)',
                'Service': 'Infrastructure Type'
            },
            color='Problem_Severity',
            color_continuous_scale='Reds',
            text='Problem_Severity'
        )
        
        fig3.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        
        fig3.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No infrastructure data available for analysis.")

with col4:
    st.subheader("📈 Transportation vs Road Quality")
    
    # Create correlation analysis
    if not filtered_df.empty:
        # Group by region and calculate averages
        region_analysis = filtered_df.groupby('Governorate').agg({
            'State of the main roads - good': 'mean',
            'The main means of public transport - buses': 'sum',
            'The main means of public transport - vans': 'sum',
            'The main means of public transport - taxis': 'sum'
        }).reset_index()
        
        # Create scatter plot
        fig4 = px.scatter(
            region_analysis,
            x='State of the main roads - good',
            y='The main means of public transport - taxis',
            size='The main means of public transport - buses',
            color='Governorate',
            title='Road Quality vs Transportation Usage',
            labels={
                'State of the main roads - good': 'Road Quality Score',
                'The main means of public transport - taxis': 'Taxi Usage'
            },
            hover_data=['The main means of public transport - vans']
        )
        
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("No data available for correlation analysis.")

# Summary Statistics
st.subheader("📋 Summary Statistics")

if not filtered_df.empty:
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        total_areas = len(filtered_df)
        st.metric("Total Areas Analyzed", total_areas)
    
    with col6:
        avg_road_quality = filtered_df['State of the main roads - good'].mean()
        st.metric("Average Road Quality", f"{avg_road_quality:.2f}")
    
    with col7:
        total_transport = (filtered_df['The main means of public transport - buses'].sum() + 
                          filtered_df['The main means of public transport - vans'].sum() + 
                          filtered_df['The main means of public transport - taxis'].sum())
        st.metric("Total Transport Services", total_transport)
    
    with col8:
        selected_region_count = len(selected_regions)
        st.metric("Regions Selected", selected_region_count)

# Data Explorer
with st.expander("🔍 Data Explorer"):
    st.subheader("Raw Data (First 100 rows)")
    st.dataframe(filtered_df.head(100), use_container_width=True)

# Footer with insights
st.markdown("---")
st.markdown("""
**Key Interactive Features:**
- **Region Filter**: Select specific regions to focus your analysis
- **Transportation Mode Focus**: Choose which transport modes to emphasize
- **Dynamic Updates**: All visualizations update based on your selections
- **Correlation Analysis**: Explore relationships between road quality and transport usage

**Insights You Can Discover:**
- Which regions have the best/worst road infrastructure
- How transportation preferences vary by region  
- Which infrastructure issues need urgent attention
- The relationship between road quality and transport mode preferences
""")