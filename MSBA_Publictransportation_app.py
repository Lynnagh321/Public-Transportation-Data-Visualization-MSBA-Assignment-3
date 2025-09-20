
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Lebanon Transportation Infrastructure Analysis",
    layout="wide"
)

# Apply professional nude/beige theme styling
st.markdown("""
<style>
    .stApp {
        background-color: #f7f5f3;
        color: #2c2c2c;
    }
    .stSidebar {
        background-color: #ede9e6;
        border-right: 1px solid #d4cfc8;
    }
    .stSelectbox > div > div {
        background-color: #ffffff;
        border: 1px solid #d4cfc8;
        color: #2c2c2c;
    }
    .stMultiSelect > div > div {
        background-color: #ffffff;
        border: 1px solid #d4cfc8;
        color: #2c2c2c;
    }
    .stRadio > div {
        background-color: #f7f5f3;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e8e3de;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    h1 {
        color: #3d3d3d;
        font-weight: 600;
        border-bottom: 2px solid #d4cfc8;
        padding-bottom: 0.5rem;
    }
    h2 {
        color: #4a4a4a;
        font-weight: 500;
    }
    h3 {
        color: #5a5a5a;
        font-weight: 500;
    }
    .stExpander {
        background-color: #ffffff;
        border: 1px solid #e8e3de;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Lebanon Transportation Infrastructure Analysis")
st.markdown("""
This dashboard analyzes the relationship between road quality and transportation patterns across different regions in Lebanon. 
The interactive visualizations reveal how infrastructure quality impacts transportation choices and regional accessibility.
""")

# Load data function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('public transportation.csv')
        if 'refArea' in df.columns:
            df['Governorate'] = df['refArea'].str.extract(r'/([^/]+)$')
        df.columns = df.columns.str.strip()
        return df
    
    except FileNotFoundError:
        st.warning("Using sample data for demonstration. Upload 'public transportation.csv' for real data.")
        np.random.seed(42)
        regions = ['Marjeyoun_District', 'Batroun_District', 'Zgharta_District', 'North_Governorate', 
                   'Matn_District', 'Tyre_District', 'Beqaa_Governorate', 'Sidon_District']
        
        data = []
        for region in regions:
            for i in range(50):
                data.append({
                    'refArea': f'/lebanon/{region.lower()}',
                    'Governorate': region,
                    'The main means of public transport - buses': np.random.choice([0, 1], p=[0.9, 0.1]),
                    'The main means of public transport - vans': np.random.choice([0, 1], p=[0.7, 0.3]),
                    'The main means of public transport - taxis': np.random.choice([0, 1], p=[0.3, 0.7]),
                    'State of the main roads - good': np.random.choice([0, 1], p=[0.8, 0.2]),
                    'State of the main roads - bad': np.random.choice([0, 1], p=[0.7, 0.3]),
                    'State of the secondary roads - good': np.random.choice([0, 1], p=[0.75, 0.25]),
                    'State of agricultural roads - good': np.random.choice([0, 1], p=[0.6, 0.4]),
                })
        
        return pd.DataFrame(data)

# Load data
df = load_data()

# Sidebar - Interactive Feature 1: Region Selection
st.sidebar.header("Interactive Controls")
st.sidebar.subheader("Region Selection")

available_regions = df['Governorate'].unique()
selected_regions = st.sidebar.multiselect(
    "Select regions to analyze:",
    options=available_regions,
    default=available_regions  # Show all by default
)

# Interactive Feature 2: Road Type Focus
st.sidebar.subheader("Infrastructure Focus")
road_type = st.sidebar.selectbox(
    "Analyze road quality for:",
    options=[
        "State of the main roads - good",
        "State of the secondary roads - good", 
        "State of agricultural roads - good"
    ],
    format_func=lambda x: x.replace("State of the ", "").replace(" - good", "").title()
)

# Interactive Feature 3: Transportation Mode Weight
st.sidebar.subheader("Transportation Analysis")
transport_weight = st.sidebar.radio(
    "Primary transportation focus:",
    options=["Taxis", "Buses", "Vans"],
    help="This affects the size of bubbles in the scatter plot"
)

transport_column = f"The main means of public transport - {transport_weight.lower()}"

# Filter data based on selections
if selected_regions:
    filtered_df = df[df['Governorate'].isin(selected_regions)]
else:
    filtered_df = df

# Main content area
st.markdown("---")

# Context and insights section
st.subheader("Key Insights")
col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    if not filtered_df.empty:
        avg_road_quality = filtered_df[road_type].mean()
        total_regions = len(selected_regions) if selected_regions else len(available_regions)
        st.metric("Average Road Quality Score", f"{avg_road_quality:.3f}", 
                 help="Higher values indicate better road infrastructure")
        st.metric("Regions Analyzed", total_regions)
    
with col_insight2:
    if not filtered_df.empty:
        total_transport = filtered_df[transport_column].sum()
        transport_percentage = (total_transport / len(filtered_df)) * 100
        st.metric(f"Areas with {transport_weight}", total_transport)
        st.metric(f"{transport_weight} Coverage", f"{transport_percentage:.1f}%")

# Main visualizations
st.markdown("---")
st.subheader("Transportation Infrastructure Analysis")

# Layout for the two main visualizations
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Road Quality by Region")
    
    if not filtered_df.empty:
        # Calculate average road quality scores by region
        road_quality = filtered_df.groupby("Governorate")[road_type].mean().reset_index()
        road_quality = road_quality.sort_values(road_type, ascending=False)
        
        # Create bar chart
        fig1 = px.bar(
            road_quality,
            x="Governorate",
            y=road_type,
            title=f"{road_type.replace('State of the ', '').replace(' - good', '').title()} Quality by Region",
            labels={
                "Governorate": "Region", 
                road_type: "Quality Score"
            }, 
            text=road_type,
            color=road_type,
            color_continuous_scale="RdYlGn"
        )
        
        fig1.update_traces(texttemplate='%{text:.2f}', textposition="outside")
        fig1.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            title_x=0.5
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Show insights
        best_region = road_quality.iloc[0]['Governorate']
        worst_region = road_quality.iloc[-1]['Governorate']
        best_score = road_quality.iloc[0][road_type]
        worst_score = road_quality.iloc[-1][road_type]
        
        st.success(f"**Best Infrastructure**: {best_region} ({best_score:.3f})")
        st.error(f"**Needs Improvement**: {worst_region} ({worst_score:.3f})")
        
    else:
        st.warning("No data available. Please select at least one region.")

with col2:
    st.markdown("### Transportation vs Road Quality")
    
    if not filtered_df.empty:
        # Create correlation analysis
        region_analysis = filtered_df.groupby('Governorate').agg({
            road_type: 'mean',
            'The main means of public transport - buses': 'sum',
            'The main means of public transport - vans': 'sum',
            'The main means of public transport - taxis': 'sum'
        }).reset_index()
        
        # Create scatter plot
        fig2 = px.scatter(
            region_analysis,
            x=road_type,
            y='The main means of public transport - taxis',
            size=transport_column,
            color='Governorate',
            title='Road Quality vs Transportation Usage',
            labels={
                road_type: 'Road Quality Score',
                'The main means of public transport - taxis': 'Taxi Services',
                transport_column: f'{transport_weight} Services'
            },
            hover_data=['The main means of public transport - buses', 'The main means of public transport - vans'],
            size_max=30
        )
        
        fig2.update_layout(
            height=500,
            title_x=0.5
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Calculate correlation
        correlation = region_analysis[road_type].corr(region_analysis['The main means of public transport - taxis'])
        
        if correlation > 0.3:
            st.info(f"**Positive correlation detected**: Better roads tend to have more taxi services (r = {correlation:.3f})")
        elif correlation < -0.3:
            st.info(f"**Negative correlation detected**: Better roads tend to have fewer taxi services (r = {correlation:.3f})")
        else:
            st.info(f"**Weak correlation**: Road quality and taxi services show little relationship (r = {correlation:.3f})")
    
    else:
        st.warning("No data available. Please select at least one region.")

# Summary analysis
st.markdown("---")

# Data explorer
with st.expander("Raw Data Explorer"):
    st.markdown("**Filtered Dataset Preview**")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Governorate', road_type, 'The main means of public transport - buses', 
                        'The main means of public transport - vans', 'The main means of public transport - taxis']].head(20), 
            use_container_width=True
        )
    else:
        st.warning("No data to display. Please select at least one region.")