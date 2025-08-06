"""
Customer Analytics Dashboard Page
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.components.navigation import show_page_header
from dashboard.components.ui_components import (
    create_metric_card, create_info_card, show_loading_state, 
    create_section_divider, create_highlight_box
)
from dashboard.components.styling import get_theme_colors

def load_customer_analytics_data():
    """Load and prepare customer analytics data"""
    try:
        # Load customer analytics data
        customer_data = pd.read_csv('data/feature_engineered/customer_analytics.csv')
        
        # Convert date columns
        customer_data['last_order_date'] = pd.to_datetime(customer_data['last_order_date'])
        customer_data['first_order_date'] = pd.to_datetime(customer_data['first_order_date'])
        
        # Handle missing values
        customer_data['total_revenue'] = customer_data['total_revenue'].fillna(0)
        customer_data['avg_delivery_experience'] = customer_data['avg_delivery_experience'].fillna(customer_data['avg_delivery_experience'].mean())
        customer_data['delivery_reliability'] = customer_data['delivery_reliability'].fillna(1.0)
        
        # Calculate key metrics
        total_customers = len(customer_data)
        total_revenue = customer_data['total_revenue'].sum()
        avg_clv = customer_data['total_revenue'].mean()
        high_value_customers = len(customer_data[customer_data['clv_category'].isin(['VIP', 'High Value'])])
        high_value_rate = (high_value_customers / total_customers) * 100
        avg_delivery_days = customer_data['avg_delivery_experience'].mean()
        delivery_reliability_rate = customer_data['delivery_reliability'].mean() * 100
        
        return {
            'customer_data': customer_data,
            'total_customers': total_customers,
            'total_revenue': total_revenue,
            'avg_clv': avg_clv,
            'high_value_rate': high_value_rate,
            'avg_delivery_days': avg_delivery_days,
            'delivery_reliability_rate': delivery_reliability_rate
        }
    except Exception as e:
        st.error(f"Error loading customer analytics data: {str(e)}")
        return None

def create_rfm_segmentation_chart(customer_data):
    """Create RFM segmentation visualization with horizontal bar chart"""
    colors = get_theme_colors()
    
    # RFM segment analysis
    segment_analysis = customer_data.groupby('customer_segment').agg({
        'customer_id': 'count',
        'total_revenue': ['sum', 'mean'],
        'recency_score': 'mean',
        'frequency_score': 'mean',
        'monetary_score': 'mean'
    }).round(2)
    
    # Flatten column names
    segment_analysis.columns = [
        'customer_count', 'total_revenue', 'avg_revenue',
        'avg_recency', 'avg_frequency', 'avg_monetary'
    ]
    
    segment_analysis['percentage'] = (
        segment_analysis['customer_count'] / len(customer_data) * 100
    ).round(2)
    
    segment_analysis = segment_analysis.reset_index().sort_values('customer_count', ascending=True)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Add bars with gradient colors based on revenue
    fig.add_trace(go.Bar(
        y=segment_analysis['customer_segment'],
        x=segment_analysis['customer_count'],
        orientation='h',
        marker=dict(
            color=segment_analysis['avg_revenue'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Avg Revenue (R$)",
                    font=dict(color=colors['text_primary'])
                ),
                tickfont=dict(color=colors['text_secondary']),
                x=1.02
            ),
            line=dict(width=1, color=colors['border_color'])
        ),
        text=[f"{count:,} customers<br>({pct:.1f}%)<br>R$ {rev:.0f} avg" 
              for count, pct, rev in zip(segment_analysis['customer_count'], 
                                       segment_analysis['percentage'],
                                       segment_analysis['avg_revenue'])],
        textposition='outside',
        textfont=dict(color=colors['text_primary'], size=11),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Customers: %{x:,}<br>" +
            "Percentage: %{customdata[0]:.1f}%<br>" +
            "Total Revenue: R$ %{customdata[1]:,.0f}<br>" +
            "Avg Revenue: R$ %{customdata[2]:.2f}<br>" +
            "Recency Score: %{customdata[3]:.1f}<br>" +
            "Frequency Score: %{customdata[4]:.1f}<br>" +
            "Monetary Score: %{customdata[5]:.1f}<br>" +
            "<extra></extra>"
        ),
        customdata=list(zip(
            segment_analysis['percentage'],
            segment_analysis['total_revenue'],
            segment_analysis['avg_revenue'],
            segment_analysis['avg_recency'],
            segment_analysis['avg_frequency'],
            segment_analysis['avg_monetary']
        ))
    ))
    
    fig.update_layout(
        title=dict(
            text="Customer Segmentation Distribution",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Number of Customers",
            color=colors['text_secondary'],
            gridcolor=colors['border_color'],
            tickformat=',d'
        ),
        yaxis=dict(
            title="Customer Segment",
            color=colors['text_secondary'],
            categoryorder='total ascending'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500,
        margin=dict(l=150, r=100, t=80, b=50)
    )
    
    return fig, segment_analysis

def create_rfm_scatter_analysis(customer_data):
    """Create RFM scatter plot analysis"""
    colors = get_theme_colors()
    
    # Sample data for scatter plot (take a sample for better visualization)
    sample_data = customer_data.sample(n=min(2000, len(customer_data)), random_state=42)
    
    # Create scatter plot
    fig = go.Figure()
    
    # Define colors for each segment
    segment_colors = {
        'New Customers': colors['accent_blue'],
        'Loyal Customers': colors['accent_green'],
        'At Risk': colors['accent_orange'],
        'Cannot Lose Them': colors['accent_pink'],
        'Potential Loyalists': colors['accent_purple'],
        'Others': colors['text_secondary']
    }
    
    # Add scatter points for each segment
    for segment in sample_data['customer_segment'].unique():
        segment_data = sample_data[sample_data['customer_segment'] == segment]
        
        fig.add_trace(go.Scatter(
            x=segment_data['recency_score'],
            y=segment_data['monetary_score'],
            mode='markers',
            name=segment,
            marker=dict(
                size=segment_data['frequency_score'] * 3,  # Size based on frequency
                color=segment_colors.get(segment, colors['text_secondary']),
                opacity=0.7,
                line=dict(width=1, color=colors['border_color'])
            ),
            hovertemplate=(
                f"<b>{segment}</b><br>" +
                "Recency Score: %{x}<br>" +
                "Monetary Score: %{y}<br>" +
                "Frequency Score: %{customdata[0]}<br>" +
                "Revenue: R$ %{customdata[1]:.2f}<br>" +
                "<extra></extra>"
            ),
            customdata=list(zip(segment_data['frequency_score'], segment_data['total_revenue']))
        ))
    
    fig.update_layout(
        title=dict(
            text="RFM Score Analysis (Sample of 2,000 customers)",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Recency Score (Lower = More Recent)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="Monetary Score (Higher = More Valuable)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(color=colors['text_primary'])
        )
    )
    
    return fig

def create_clv_distribution_chart(customer_data):
    """Create CLV distribution visualization"""
    colors = get_theme_colors()
    
    # CLV category analysis
    clv_analysis = customer_data.groupby('clv_category').agg({
        'customer_id': 'count',
        'total_revenue': ['sum', 'mean']
    }).round(2)
    
    clv_analysis.columns = ['customer_count', 'total_revenue', 'avg_revenue']
    clv_analysis['percentage'] = (
        clv_analysis['customer_count'] / len(customer_data) * 100
    ).round(2)
    
    clv_analysis = clv_analysis.reset_index()
    
    # Create bar chart for CLV distribution
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=clv_analysis['clv_category'],
        y=clv_analysis['customer_count'],
        marker_color=[colors['accent_green'], colors['accent_blue'], colors['accent_purple'], colors['accent_orange']][:len(clv_analysis)],
        text=[f"{count:,}<br>({pct:.1f}%)" for count, pct in zip(clv_analysis['customer_count'], clv_analysis['percentage'])],
        textposition='outside',
        textfont=dict(color=colors['text_primary']),
        hovertemplate=(
            "<b>%{x}</b><br>" +
            "Customers: %{y:,}<br>" +
            "Avg Revenue: R$ %{customdata:.2f}<br>" +
            "<extra></extra>"
        ),
        customdata=clv_analysis['avg_revenue']
    ))
    
    fig.update_layout(
        title=dict(
            text="Customer Lifetime Value Distribution",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="CLV Category",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="Number of Customers",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=400
    )
    
    return fig, clv_analysis

def create_customer_journey_funnel(customer_data):
    """Create customer journey funnel visualization"""
    colors = get_theme_colors()
    
    # Customer status analysis
    status_counts = customer_data['customer_status'].value_counts()
    
    # Create funnel data
    funnel_data = []
    total_customers = len(customer_data)
    
    for status in ['Active', 'Inactive', 'Churned']:
        count = status_counts.get(status, 0)
        percentage = (count / total_customers) * 100
        funnel_data.append({
            'stage': status,
            'count': count,
            'percentage': percentage
        })
    
    funnel_df = pd.DataFrame(funnel_data)
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=funnel_df['stage'],
        x=funnel_df['count'],
        textinfo="value+percent initial",
        textfont=dict(color=colors['text_primary'], size=14),
        marker=dict(
            color=[colors['accent_green'], colors['accent_orange'], colors['accent_pink']],
            line=dict(width=2, color=colors['border_color'])
        ),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Customers: %{x:,}<br>" +
            "Percentage: %{percentInitial}<br>" +
            "<extra></extra>"
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="Customer Journey Funnel",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=400
    )
    
    return fig, funnel_df

def create_delivery_impact_analysis(customer_data):
    """Create delivery experience impact visualization"""
    colors = get_theme_colors()
    
    # Create delivery speed categories
    customer_data_copy = customer_data.copy()
    customer_data_copy['delivery_speed_category'] = pd.cut(
        customer_data_copy['avg_delivery_experience'],
        bins=[0, 7, 14, 21, 30, float('inf')],
        labels=['Very Fast (≤7d)', 'Fast (8-14d)', 'Normal (15-21d)', 'Slow (22-30d)', 'Very Slow (>30d)']
    )
    
    # Analyze delivery impact
    delivery_impact = customer_data_copy.groupby('delivery_speed_category').agg({
        'customer_id': 'count',
        'total_revenue': 'mean',
        'delivery_reliability': 'mean'
    }).round(2)
    
    delivery_impact.columns = ['customer_count', 'avg_revenue', 'avg_reliability']
    delivery_impact = delivery_impact.reset_index()
    
    # Create scatter plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=delivery_impact['avg_reliability'],
        y=delivery_impact['avg_revenue'],
        mode='markers+text',
        marker=dict(
            size=[count/100 for count in delivery_impact['customer_count']],
            color=delivery_impact['avg_revenue'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title=dict(text="Avg Revenue (R$)", font=dict(color=colors['text_primary'])),
                tickfont=dict(color=colors['text_secondary'])
            ),
            line=dict(width=2, color=colors['border_color'])
        ),
        text=delivery_impact['delivery_speed_category'],
        textposition="middle center",
        textfont=dict(color=colors['text_primary'], size=10),
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Avg Revenue: R$ %{y:.2f}<br>" +
            "Reliability: %{x:.2f}<br>" +
            "Customers: %{customdata:,}<br>" +
            "<extra></extra>"
        ),
        customdata=delivery_impact['customer_count']
    ))
    
    fig.update_layout(
        title=dict(
            text="Delivery Experience Impact on Customer Value",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Delivery Reliability",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="Average Revenue (R$)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=400
    )
    
    return fig, delivery_impact

def create_segment_recommendations(segment_analysis, clv_analysis):
    """Create customer segment recommendations"""
    recommendations = []
    
    # Analyze top segments
    top_segments = segment_analysis.nlargest(3, 'total_revenue')
    
    for _, segment in top_segments.iterrows():
        segment_name = segment['customer_segment']
        customer_count = segment['customer_count']
        avg_revenue = segment['avg_revenue']
        percentage = segment['percentage']
        
        if segment_name == 'New Customers':
            recommendation = f"""
            **{segment_name}** ({customer_count:,} customers, {percentage:.1f}%)
            - Average Revenue: R$ {avg_revenue:.2f}
            - **Strategy**: Focus on onboarding and first-purchase experience optimization
            - **Action**: Implement welcome campaigns and delivery experience improvements
            """
        elif segment_name == 'Cannot Lose Them':
            recommendation = f"""
            **{segment_name}** ({customer_count:,} customers, {percentage:.1f}%)
            - Average Revenue: R$ {avg_revenue:.2f}
            - **Strategy**: Immediate retention campaigns and personalized offers
            - **Action**: Priority customer service and exclusive benefits program
            """
        elif segment_name == 'Others':
            recommendation = f"""
            **{segment_name}** ({customer_count:,} customers, {percentage:.1f}%)
            - Average Revenue: R$ {avg_revenue:.2f}
            - **Strategy**: Segmentation refinement and targeted engagement
            - **Action**: Analyze purchase patterns for micro-segmentation opportunities
            """
        else:
            recommendation = f"""
            **{segment_name}** ({customer_count:,} customers, {percentage:.1f}%)
            - Average Revenue: R$ {avg_revenue:.2f}
            - **Strategy**: Maintain engagement and prevent churn
            - **Action**: Regular communication and value-added services
            """
        
        recommendations.append(recommendation)
    
    return recommendations

def render():
    """Render the Customer Analytics page"""
    show_page_header(
        "Customer Analytics",
        "Customer insights, segmentation, and lifetime value analysis",
        "👥"
    )
    
    # Load data
    with st.spinner("Loading customer analytics data..."):
        data = load_customer_analytics_data()
    
    if data is None:
        st.error("Unable to load customer analytics data. Please check data files.")
        return
    
    customer_data = data['customer_data']
    
    # Key Performance Indicators
    create_section_divider("Customer Analytics KPIs")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "Total Customers", 
            data['total_customers'], 
            icon="👥"
        )
    
    with col2:
        create_metric_card(
            "Total Revenue", 
            data['total_revenue'], 
            icon="💰"
        )
    
    with col3:
        create_metric_card(
            "Avg Customer Value", 
            data['avg_clv'], 
            icon="💎"
        )
    
    with col4:
        create_metric_card(
            "High-Value Rate", 
            data['high_value_rate'], 
            icon="⭐"
        )
    
    # Second row of KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        create_metric_card(
            "Avg Delivery Days", 
            data['avg_delivery_days'], 
            icon="🚚"
        )
    
    with col6:
        create_metric_card(
            "Delivery Reliability", 
            data['delivery_reliability_rate'], 
            icon="✅"
        )
    
    with col7:
        active_customers = len(customer_data[customer_data['customer_status'] == 'Active'])
        create_metric_card(
            "Active Customers", 
            active_customers, 
            icon="🟢"
        )
    
    with col8:
        vip_customers = len(customer_data[customer_data['clv_category'] == 'VIP'])
        create_metric_card(
            "VIP Customers", 
            vip_customers, 
            icon="👑"
        )
    
    # RFM Segmentation Analysis
    create_section_divider("RFM Customer Segmentation")
    
    # Main segmentation chart
    rfm_chart, segment_analysis = create_rfm_segmentation_chart(customer_data)
    st.plotly_chart(rfm_chart, use_container_width=True)
    
    # RFM scatter analysis
    col_scatter, col_details = st.columns([2, 1])
    
    with col_scatter:
        rfm_scatter = create_rfm_scatter_analysis(customer_data)
        st.plotly_chart(rfm_scatter, use_container_width=True)
    
    with col_details:
        # Display segment details
        st.subheader("Top Segments")
        top_segments = segment_analysis.nlargest(4, 'customer_count')
        for _, segment in top_segments.iterrows():
            st.metric(
                label=f"{segment['customer_segment']}",
                value=f"{segment['customer_count']:,}",
                delta=f"{segment['percentage']:.1f}% of customers"
            )
    
    # CLV Analysis
    create_section_divider("Customer Lifetime Value Analysis")
    
    col_clv_left, col_clv_right = st.columns(2)
    
    with col_clv_left:
        clv_chart, clv_analysis = create_clv_distribution_chart(customer_data)
        st.plotly_chart(clv_chart, use_container_width=True)
    
    with col_clv_right:
        # CLV insights
        st.subheader("CLV Insights")
        for _, clv_cat in clv_analysis.iterrows():
            st.metric(
                label=f"{clv_cat['clv_category']} Customers",
                value=f"{clv_cat['customer_count']:,}",
                delta=f"R$ {clv_cat['avg_revenue']:.2f} avg"
            )
    
    # Customer Journey and Delivery Impact
    create_section_divider("Customer Journey & Delivery Impact")
    
    col_journey_left, col_journey_right = st.columns(2)
    
    with col_journey_left:
        journey_chart, journey_data = create_customer_journey_funnel(customer_data)
        st.plotly_chart(journey_chart, use_container_width=True)
    
    with col_journey_right:
        delivery_chart, delivery_impact = create_delivery_impact_analysis(customer_data)
        st.plotly_chart(delivery_chart, use_container_width=True)
    
    # Customer Segment Recommendations
    create_section_divider("Strategic Recommendations")
    
    recommendations = create_segment_recommendations(segment_analysis, clv_analysis)
    
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        st.info(recommendations[0])
        if len(recommendations) > 2:
            st.success(recommendations[2])
    
    with col_rec2:
        if len(recommendations) > 1:
            st.warning(recommendations[1])
    
    # Key Insights Summary
    st.markdown("---")
    st.header("Key Customer Analytics Insights")
    
    # Calculate key insights
    high_value_percentage = (len(customer_data[customer_data['clv_category'].isin(['VIP', 'High Value'])]) / len(customer_data)) * 100
    avg_delivery_impact = customer_data.groupby('clv_category')['avg_delivery_experience'].mean()
    top_segment = segment_analysis.iloc[0]
    
    st.subheader("📊 Customer Analytics Summary")
    
    st.markdown(f"""
    **Customer Portfolio**: {data['total_customers']:,} total customers generating R$ {data['total_revenue']:,.2f} in revenue with an average customer value of R$ {data['avg_clv']:.2f}.
    
    **High-Value Concentration**: {high_value_percentage:.1f}% of customers are classified as High-Value or VIP, indicating strong customer acquisition quality and market positioning.
    
    **Segmentation Insights**: The largest segment is "{top_segment['customer_segment']}" with {top_segment['customer_count']:,} customers ({top_segment['percentage']:.1f}%) contributing R$ {top_segment['total_revenue']:,.2f} in total revenue.
    
    **Delivery Experience Impact**: Average delivery time of {data['avg_delivery_days']:.1f} days with {data['delivery_reliability_rate']:.1f}% reliability rate. VIP customers experience {avg_delivery_impact.get('VIP', 0):.1f} days average delivery time.
    
    **Strategic Focus**: Prioritize retention of high-value segments, optimize delivery experience for customer satisfaction, and implement targeted campaigns for each customer segment to maximize lifetime value.
    """)