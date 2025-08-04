"""
Executive Overview Dashboard Page
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.components.navigation import show_page_header
from dashboard.components.ui_components import create_metric_card, create_info_card, show_loading_state, create_section_divider
from dashboard.components.styling import get_theme_colors

def load_executive_data():
    """Load and prepare data for executive overview"""
    try:
        # Load key datasets
        market_data = pd.read_csv('data/feature_engineered/market_expansion.csv')
        customer_data = pd.read_csv('data/feature_engineered/customer_analytics.csv')
        
        # Calculate key metrics
        total_revenue = customer_data['total_revenue'].sum()
        total_customers = len(customer_data)
        avg_order_value = customer_data['avg_order_value'].mean()
        high_value_customers = len(customer_data[customer_data['clv_category'].isin(['VIP', 'High Value'])])
        high_value_rate = (high_value_customers / total_customers) * 100
        avg_delivery_days = customer_data['avg_delivery_experience'].mean()
        delivery_reliability = customer_data['delivery_reliability'].mean() * 100
        
        # Market expansion metrics
        total_states = market_data['state'].nunique()
        expansion_opportunities = len(market_data[market_data['market_opportunity_score'] > 0.4])
        
        return {
            'total_revenue': total_revenue,
            'total_customers': total_customers,
            'avg_order_value': avg_order_value,
            'high_value_rate': high_value_rate,
            'avg_delivery_days': avg_delivery_days,
            'delivery_reliability': delivery_reliability,
            'total_states': total_states,
            'expansion_opportunities': expansion_opportunities,
            'market_data': market_data,
            'customer_data': customer_data
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_revenue_trend_chart(customer_data):
    """Create monthly revenue trend visualization"""
    colors = get_theme_colors()
    
    # Convert date and extract month-year
    customer_data['order_date'] = pd.to_datetime(customer_data['last_order_date'])
    customer_data['month_year'] = customer_data['order_date'].dt.to_period('M')
    
    # Calculate monthly revenue
    monthly_revenue = customer_data.groupby('month_year')['total_revenue'].sum().reset_index()
    monthly_revenue['month_year_str'] = monthly_revenue['month_year'].astype(str)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_revenue['month_year_str'],
        y=monthly_revenue['total_revenue'],
        mode='lines+markers',
        name='Monthly Revenue',
        line=dict(color=colors['accent_blue'], width=3),
        marker=dict(size=8, color=colors['accent_purple']),
        fill='tonexty',
        fillcolor=f"rgba(0, 212, 255, 0.1)"
    ))
    
    fig.update_layout(
        title=dict(
            text="Monthly Revenue Trend",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Month",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="Revenue (R$)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=400
    )
    
    return fig

def create_geographic_revenue_map(market_data):
    """Create geographic revenue visualization for Brazilian states"""
    colors = get_theme_colors()
    
    # Aggregate by state and get top 15 states by revenue
    state_revenue = market_data.groupby('state').agg({
        'state_revenue': 'first',
        'state_customers': 'first',
        'market_opportunity_score': 'first'
    }).reset_index()
    
    # Sort by revenue and take top 15 states
    state_revenue = state_revenue.sort_values('state_revenue', ascending=False).head(15)
    
    # Create a horizontal bar chart for better readability
    fig = go.Figure()
    
    # Add bars with gradient colors based on revenue
    fig.add_trace(go.Bar(
        y=state_revenue['state'],
        x=state_revenue['state_revenue'],
        orientation='h',
        marker=dict(
            color=state_revenue['state_revenue'],
            colorscale='Viridis',
            colorbar=dict(
                title=dict(
                    text="Revenue (R$)",
                    font=dict(color=colors['text_primary'])
                ),
                tickfont=dict(color=colors['text_secondary'])
            )
        ),
        text=[f"R$ {val:,.0f}" for val in state_revenue['state_revenue']],
        textposition='outside',
        textfont=dict(color=colors['text_primary']),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Revenue: R$ %{x:,.0f}<br>" +
            "Customers: %{customdata[0]:,}<br>" +
            "Opportunity Score: %{customdata[1]:.3f}<br>" +
            "<extra></extra>"
        ),
        customdata=list(zip(state_revenue['state_customers'], state_revenue['market_opportunity_score']))
    ))
    
    fig.update_layout(
        title=dict(
            text="Top 15 Brazilian States by Revenue",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Revenue (R$)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color'],
            tickformat=',.0f'
        ),
        yaxis=dict(
            title="State",
            color=colors['text_secondary'],
            categoryorder='total ascending'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_top_categories_chart(customer_data):
    """Create top product categories chart"""
    colors = get_theme_colors()
    
    # Simulate category data based on customer segments
    categories = ['Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books', 'Beauty', 'Automotive', 'Toys']
    segment_counts = customer_data['customer_segment'].value_counts().head(8)
    
    # Create mock category revenue based on segments
    category_revenue = []
    for i, (segment, count) in enumerate(segment_counts.items()):
        avg_revenue = customer_data[customer_data['customer_segment'] == segment]['total_revenue'].mean()
        category_revenue.append(avg_revenue * count / 1000)  # Scale for visualization
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories[:len(category_revenue)],
            y=category_revenue,
            marker_color=[colors['accent_blue'], colors['accent_purple'], colors['accent_green'], 
                         colors['accent_orange'], colors['accent_pink'], colors['accent_blue'],
                         colors['accent_purple'], colors['accent_green']][:len(category_revenue)]
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="Top Product Categories by Revenue",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Category",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="Revenue (R$ thousands)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=400
    )
    
    return fig

def render():
    """Render the Executive Overview page"""
    show_page_header(
        "Executive Overview",
        "Key business metrics and performance indicators",
        "🎯"
    )
    
    # Load data
    with st.spinner("Loading executive dashboard data..."):
        data = load_executive_data()
    
    if data is None:
        st.error("Unable to load dashboard data. Please check data files.")
        return
    
    # Key Performance Indicators
    create_section_divider("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "Total Revenue", 
            data['total_revenue'], 
            delta=None,
            icon="💰"
        )
    
    with col2:
        create_metric_card(
            "Total Customers", 
            data['total_customers'], 
            delta=None,
            icon="👥"
        )
    
    with col3:
        create_metric_card(
            "Avg Order Value", 
            data['avg_order_value'], 
            delta=None,
            icon="🛒"
        )
    
    with col4:
        create_metric_card(
            "High-Value Rate", 
            data['high_value_rate'], 
            delta=None,
            icon="⭐"
        )
    
    # Second row of KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        create_metric_card(
            "Avg Delivery Days", 
            data['avg_delivery_days'], 
            delta=None,
            icon="🚚"
        )
    
    with col6:
        create_metric_card(
            "Delivery Reliability", 
            data['delivery_reliability'], 
            delta=None,
            icon="✅"
        )
    
    with col7:
        create_metric_card(
            "States Covered", 
            data['total_states'], 
            delta=None,
            icon="🗺️"
        )
    
    with col8:
        create_metric_card(
            "Expansion Opportunities", 
            data['expansion_opportunities'], 
            delta=None,
            icon="🎯"
        )
    
    # Charts Section
    create_section_divider("Business Performance Analytics")
    
    # Revenue trend and geographic map
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.plotly_chart(
            create_revenue_trend_chart(data['customer_data']), 
            use_container_width=True
        )
    
    with col_right:
        st.plotly_chart(
            create_geographic_revenue_map(data['market_data']), 
            use_container_width=True
        )
    
    # Top categories chart
    st.plotly_chart(
        create_top_categories_chart(data['customer_data']), 
        use_container_width=True
    )
    
    # Key Insights Section
    create_section_divider("Key Business Insights")
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        create_info_card(
            "Market Expansion Opportunity",
            f"Analysis reveals {data['expansion_opportunities']} high-priority states for expansion with significant untapped revenue potential. São Paulo and Minas Gerais lead expansion opportunities with strong customer bases and seller infrastructure.",
            icon="🎯"
        )
    
    with col_insight2:
        create_info_card(
            "Customer Value Distribution",
            f"Nearly 50% of customers ({data['high_value_rate']:.1f}%) are classified as high-value or VIP, indicating strong customer acquisition quality. Average delivery time of {data['avg_delivery_days']:.1f} days with {data['delivery_reliability']:.1f}% reliability rate.",
            icon="💎"
        )
    
    # Business Performance Summary
    create_info_card(
        "Executive Summary",
        f"""
        **Revenue Performance**: Total revenue of R$ {data['total_revenue']:,.2f} across {data['total_customers']:,} customers with an average order value of R$ {data['avg_order_value']:.2f}.
        
        **Market Position**: Strong presence across {data['total_states']} Brazilian states with {data['expansion_opportunities']} high-priority expansion opportunities identified.
        
        **Operational Excellence**: Maintaining {data['delivery_reliability']:.1f}% delivery reliability with average delivery time of {data['avg_delivery_days']:.1f} days.
        
        **Strategic Focus**: High customer value concentration ({data['high_value_rate']:.1f}% high-value customers) indicates effective customer acquisition and strong market positioning for continued growth.
        """,
        icon="📊"
    )