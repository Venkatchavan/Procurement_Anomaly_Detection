"""
Streamlit Dashboard for Public Procurement Transparency
Interactive dashboard for exploring procurement data and anomalies.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Page configuration
st.set_page_config(
    page_title="Procurement Transparency Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-critical {
        background-color: #ffebee;
        color: #c62828;
    }
    .risk-high {
        background-color: #fff3e0;
        color: #ef6c00;
    }
    .risk-medium {
        background-color: #fff9c4;
        color: #f57f17;
    }
    .risk-low {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load procurement and anomaly data."""
    try:
        df = pd.read_csv("../data/processed/anomaly_detection_results.csv",
                        parse_dates=['award_date', 'publish_date'])
        return df
    except FileNotFoundError:
        # Generate sample data if file doesn't exist
        st.warning("Data file not found. Generating sample data...")
        return generate_sample_data()


def generate_sample_data(n=500):
    """Generate sample data for demonstration."""
    np.random.seed(42)
    
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', periods=n)
    
    data = {
        'contract_id': [f'FI-2024-{i:05d}' for i in range(n)],
        'contract_title': [f'Contract {i}' for i in range(n)],
        'contract_value': np.random.lognormal(11, 1.5, n),
        'vendor_name': np.random.choice(['Vendor A', 'Vendor B', 'Vendor C', 'Vendor D', 'Vendor E'], n),
        'contracting_authority': np.random.choice(['City of Helsinki', 'City of Espoo', 'Ministry of Finance'], n),
        'cpv_description': np.random.choice(['Construction', 'IT Services', 'Consulting', 'Healthcare'], n),
        'award_date': dates,
        'risk_score': np.random.uniform(0, 100, n),
        'risk_category': np.random.choice(['Low', 'Medium', 'High', 'Critical'], n, p=[0.6, 0.25, 0.1, 0.05]),
        'iso_anomaly': np.random.choice([0, 1], n, p=[0.95, 0.05]),
        'lof_anomaly': np.random.choice([0, 1], n, p=[0.95, 0.05]),
        'any_anomaly': np.random.choice([0, 1], n, p=[0.9, 0.1]),
        'is_sustainable': np.random.choice([True, False], n, p=[0.15, 0.85])
    }
    
    return pd.DataFrame(data)


def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Public Procurement Transparency Dashboard</h1>', 
                unsafe_allow_html=True)
    st.markdown("### *Data-Driven Anti-Corruption and Sustainability Analytics*")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    min_date = df['award_date'].min().date()
    max_date = df['award_date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Category filter
    categories = ['All'] + sorted(df['cpv_description'].unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    # Risk filter
    risk_levels = st.sidebar.multiselect(
        "Risk Level",
        options=['Low', 'Medium', 'High', 'Critical'],
        default=['High', 'Critical']
    )
    
    # Anomaly filter
    show_anomalies_only = st.sidebar.checkbox("Show Anomalies Only", value=False)
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['award_date'].dt.date >= date_range[0]) &
            (filtered_df['award_date'].dt.date <= date_range[1])
        ]
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['cpv_description'] == selected_category]
    
    if risk_levels:
        filtered_df = filtered_df[filtered_df['risk_category'].isin(risk_levels)]
    
    if show_anomalies_only:
        filtered_df = filtered_df[filtered_df['any_anomaly'] == 1]
    
    # Main content
    if len(filtered_df) == 0:
        st.warning("No data matches the selected filters.")
        return
    
    # KPI Section
    st.header("📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Contracts",
            f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df)}" if len(filtered_df) != len(df) else None
        )
    
    with col2:
        total_value = filtered_df['contract_value'].sum()
        st.metric(
            "Total Value",
            f"€{total_value/1e6:.1f}M"
        )
    
    with col3:
        anomaly_rate = (filtered_df['any_anomaly'].sum() / len(filtered_df) * 100)
        st.metric(
            "Anomaly Rate",
            f"{anomaly_rate:.1f}%",
            delta=f"{anomaly_rate - 10:.1f}%" if anomaly_rate > 10 else None,
            delta_color="inverse"
        )
    
    with col4:
        if 'is_sustainable' in filtered_df.columns:
            sustainability_rate = filtered_df['is_sustainable'].mean() * 100
            st.metric(
                "Sustainability",
                f"{sustainability_rate:.1f}%",
                delta=f"{sustainability_rate - 15:.1f}%" if sustainability_rate > 0 else None
            )
        else:
            st.metric("Sustainability", "N/A")
    
    with col5:
        unique_vendors = filtered_df['vendor_name'].nunique()
        st.metric(
            "Unique Vendors",
            f"{unique_vendors:,}"
        )
    
    st.markdown("---")
    
    # Two column layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Time series chart
        st.subheader("📉 Contract Value Trends")
        
        monthly_data = filtered_df.set_index('award_date').resample('ME').agg({
            'contract_value': 'sum',
            'contract_id': 'count'
        }).reset_index()
        monthly_data.columns = ['Month', 'Total Value', 'Count']
        
        fig_trends = go.Figure()
        fig_trends.add_trace(go.Scatter(
            x=monthly_data['Month'],
            y=monthly_data['Total Value'] / 1e6,
            mode='lines+markers',
            name='Total Value (M€)',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='%{x}<br>Value: €%{y:.2f}M<extra></extra>'
        ))
        
        fig_trends.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Value (Million EUR)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_trends, width='stretch')
    
    with col_right:
        # Risk distribution pie chart
        st.subheader("⚠️ Risk Distribution")
        
        risk_counts = filtered_df['risk_category'].value_counts()
        
        colors = {
            'Low': '#4caf50',
            'Medium': '#ffeb3b',
            'High': '#ff9800',
            'Critical': '#f44336'
        }
        
        fig_risk = go.Figure(data=[go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            marker=dict(colors=[colors.get(cat, '#999') for cat in risk_counts.index]),
            hole=0.4,
            hovertemplate='%{label}<br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
        )])
        
        fig_risk.update_layout(height=400)
        st.plotly_chart(fig_risk, width='stretch')
    
    # Vendor analysis
    st.markdown("---")
    st.header("🏢 Vendor Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Vendors by Contract Value")
        
        vendor_stats = filtered_df.groupby('vendor_name').agg({
            'contract_value': 'sum',
            'contract_id': 'count'
        }).sort_values('contract_value', ascending=False).head(10)
        
        fig_vendors = px.bar(
            vendor_stats.reset_index(),
            x='contract_value',
            y='vendor_name',
            orientation='h',
            labels={'contract_value': 'Total Value (EUR)', 'vendor_name': 'Vendor'},
            color='contract_id',
            color_continuous_scale='Blues'
        )
        fig_vendors.update_layout(height=400)
        st.plotly_chart(fig_vendors, width='stretch')
    
    with col2:
        st.subheader("Category Distribution")
        
        category_stats = filtered_df.groupby('cpv_description')['contract_value'].sum().sort_values(ascending=False).head(10)
        
        fig_categories = px.bar(
            category_stats.reset_index(),
            x='cpv_description',
            y='contract_value',
            labels={'contract_value': 'Total Value (EUR)', 'cpv_description': 'Category'},
            color='contract_value',
            color_continuous_scale='Viridis'
        )
        fig_categories.update_layout(height=400)
        st.plotly_chart(fig_categories, width='stretch')
    
    # High-risk contracts table
    st.markdown("---")
    st.header("🚨 High-Risk Contracts")
    
    high_risk_df = filtered_df[filtered_df['risk_category'].isin(['High', 'Critical'])].sort_values('risk_score', ascending=False)
    
    if len(high_risk_df) > 0:
        display_cols = ['contract_id', 'contract_title', 'vendor_name', 'contracting_authority',
                       'contract_value', 'risk_score', 'risk_category', 'award_date']
        
        # Format the dataframe
        display_df = high_risk_df[display_cols].copy()
        display_df['contract_value'] = display_df['contract_value'].apply(lambda x: f"€{x:,.2f}")
        display_df['risk_score'] = display_df['risk_score'].apply(lambda x: f"{x:.1f}")
        display_df['award_date'] = display_df['award_date'].dt.date
        
        st.dataframe(
            display_df.head(20),
            width='stretch',
            height=400
        )
        
        # Download button
        csv = high_risk_df.to_csv(index=False)
        st.download_button(
            label="📥 Download High-Risk Contracts CSV",
            data=csv,
            file_name=f"high_risk_contracts_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No high-risk contracts found with current filters.")
    
    # Anomaly scatter plot
    st.markdown("---")
    st.header("🔍 Anomaly Detection View")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='contract_value',
        y='risk_score',
        color='risk_category',
        color_discrete_map=colors,
        size='contract_value',
        hover_data=['contract_id', 'vendor_name', 'contracting_authority'],
        labels={'contract_value': 'Contract Value (EUR)', 'risk_score': 'Risk Score'},
        title="Contract Value vs Risk Score"
    )
    
    fig_scatter.update_xaxes(type="log")
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, width='stretch')
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Public Procurement Transparency Dashboard | Data-Driven Anti-Corruption Analytics</p>
            <p>Built with Streamlit | Data source: Finnish Open Data Portal (avoindata.fi)</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
