"""
Seasonal Intelligence Dashboard Page
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.components.navigation import show_page_header
from dashboard.components.ui_components import create_metric_card, create_info_card, show_loading_state, create_section_divider, create_highlight_box
from dashboard.components.styling import get_theme_colors

def load_seasonal_data():
    """Load and prepare seasonal intelligence data"""
    try:
        # Load seasonal intelligence datasets
        monthly_trends = pd.read_csv('data/feature_engineered/seasonal_intelligence_monthly_trends.csv')
        forecasts = pd.read_csv('data/feature_engineered/seasonal_intelligence_forecasts.csv')
        cultural_events = pd.read_csv('data/feature_engineered/seasonal_intelligence_cultural_events.csv')
        category_patterns = pd.read_csv('data/feature_engineered/seasonal_intelligence_category_patterns.csv')
        inventory_recommendations = pd.read_csv('data/feature_engineered/seasonal_intelligence_inventory_recommendations.csv')
        seasonal_variance = pd.read_csv('data/feature_engineered/seasonal_intelligence_seasonal_variance.csv')
        
        # Calculate key metrics
        total_revenue = seasonal_variance['total_revenue'].sum()
        peak_month = seasonal_variance.loc[seasonal_variance['total_revenue'].idxmax()]
        trough_month = seasonal_variance.loc[seasonal_variance['total_revenue'].idxmin()]
        seasonal_variance_cv = seasonal_variance['total_revenue'].std() / seasonal_variance['total_revenue'].mean()
        
        # Get high impact events
        high_impact_events = cultural_events[cultural_events['expected_impact'].isin(['high', 'very_high'])]
        
        # Get most seasonal categories
        most_seasonal = category_patterns.head(5)
        least_seasonal = category_patterns.tail(5)
        
        return {
            'monthly_trends': monthly_trends,
            'forecasts': forecasts,
            'cultural_events': cultural_events,
            'category_patterns': category_patterns,
            'inventory_recommendations': inventory_recommendations,
            'seasonal_variance': seasonal_variance,
            'total_revenue': total_revenue,
            'peak_month': peak_month,
            'trough_month': trough_month,
            'seasonal_variance_cv': seasonal_variance_cv,
            'high_impact_events': high_impact_events,
            'most_seasonal': most_seasonal,
            'least_seasonal': least_seasonal
        }
    except Exception as e:
        st.error(f"Error loading seasonal data: {str(e)}")
        return None

def create_monthly_trends_chart(seasonal_variance):
    """Create monthly seasonal trends visualization"""
    colors = get_theme_colors()
    
    # Create month names for better display
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    seasonal_variance['month_name'] = seasonal_variance['month'].map(month_names)
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=["Monthly Revenue and Order Trends"]
    )
    
    # Add revenue bars
    fig.add_trace(
        go.Bar(
            x=seasonal_variance['month_name'],
            y=seasonal_variance['total_revenue'],
            name='Revenue',
            marker_color=colors['accent_blue'],
            opacity=0.8,
            text=[f"R$ {val:,.0f}" for val in seasonal_variance['total_revenue']],
            textposition='outside',
            textfont=dict(color=colors['text_primary'])
        ),
        secondary_y=False
    )
    
    # Add orders line
    fig.add_trace(
        go.Scatter(
            x=seasonal_variance['month_name'],
            y=seasonal_variance['total_orders'],
            mode='lines+markers',
            name='Orders',
            line=dict(color=colors['accent_orange'], width=3),
            marker=dict(size=8, color=colors['accent_orange']),
            yaxis='y2'
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Monthly Seasonal Patterns",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update x and y axes
    fig.update_xaxes(
        title_text="Month",
        color=colors['text_secondary'],
        gridcolor=colors['border_color']
    )
    
    fig.update_yaxes(
        title_text="Revenue (R$)",
        color=colors['text_secondary'],
        gridcolor=colors['border_color'],
        secondary_y=False
    )
    
    fig.update_yaxes(
        title_text="Number of Orders",
        color=colors['text_secondary'],
        secondary_y=True
    )
    
    return fig

def create_holiday_impact_chart(cultural_events):
    """Create Brazilian holiday impact visualization"""
    colors = get_theme_colors()
    
    # Sort by revenue impact
    cultural_events_sorted = cultural_events.sort_values('revenue_vs_average', ascending=True)
    
    # Create color mapping based on impact
    color_map = {
        'very_high': colors['accent_pink'],
        'high': colors['accent_orange'],
        'medium': colors['accent_blue'],
        'low': colors['accent_green']
    }
    
    bar_colors = [color_map.get(impact, colors['accent_purple']) for impact in cultural_events_sorted['expected_impact']]
    
    fig = go.Figure(data=[
        go.Bar(
            y=cultural_events_sorted['event_name'],
            x=cultural_events_sorted['revenue_vs_average'],
            orientation='h',
            marker_color=bar_colors,
            text=[f"{val:+.1f}%" for val in cultural_events_sorted['revenue_vs_average']],
            textposition='outside',
            textfont=dict(color=colors['text_primary']),
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Revenue Impact: %{x:+.1f}%<br>" +
                "Expected Impact: %{customdata[0]}<br>" +
                "Event Type: %{customdata[1]}<br>" +
                "<extra></extra>"
            ),
            customdata=list(zip(cultural_events_sorted['expected_impact'], cultural_events_sorted['event_type']))
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="Brazilian Holiday & Cultural Event Impact",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Revenue Impact vs Average (%)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color'],
            zeroline=True,
            zerolinecolor=colors['border_color'],
            zerolinewidth=2
        ),
        yaxis=dict(
            title="Event",
            color=colors['text_secondary']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500
    )
    
    return fig

def create_forecasting_chart(forecasts):
    """Create demand forecasting visualization with confidence intervals"""
    colors = get_theme_colors()
    
    fig = go.Figure()
    
    # Add predicted revenue bars
    fig.add_trace(go.Bar(
        x=forecasts['month_name'],
        y=forecasts['predicted_revenue'],
        name='Predicted Revenue',
        marker_color=colors['accent_blue'],
        opacity=0.8,
        text=[f"R$ {val:,.0f}" for val in forecasts['predicted_revenue']],
        textposition='outside',
        textfont=dict(color=colors['text_primary'])
    ))
    
    # Add confidence interval as error bars
    fig.add_trace(go.Scatter(
        x=forecasts['month_name'],
        y=forecasts['predicted_revenue'],
        error_y=dict(
            type='data',
            symmetric=False,
            array=forecasts['revenue_upper_ci'] - forecasts['predicted_revenue'],
            arrayminus=forecasts['predicted_revenue'] - forecasts['revenue_lower_ci'],
            color=colors['accent_orange'],
            thickness=3,
            width=10
        ),
        mode='markers',
        marker=dict(size=0),
        name='95% Confidence Interval',
        showlegend=True
    ))
    
    # Add event annotations
    for i, row in forecasts.iterrows():
        fig.add_annotation(
            x=row['month_name'],
            y=row['predicted_revenue'] + (row['revenue_upper_ci'] - row['predicted_revenue']) + 50000,
            text=f"{row['event_name']}<br>({row['expected_impact']} impact)",
            showarrow=True,
            arrowhead=2,
            arrowcolor=colors['accent_purple'],
            font=dict(color=colors['text_primary'], size=10),
            bgcolor=colors['card_bg'],
            bordercolor=colors['border_color'],
            borderwidth=1
        )
    
    fig.update_layout(
        title=dict(
            text="3-Month Demand Forecast",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Month",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="Predicted Revenue (R$)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500
    )
    
    return fig

def create_category_seasonality_chart(category_patterns):
    """Create category seasonality analysis chart"""
    colors = get_theme_colors()
    
    # Get top 15 most seasonal categories
    top_seasonal = category_patterns.head(15)
    
    # Create color mapping based on seasonality level
    color_map = {
        'Very High Seasonality': colors['accent_pink'],
        'High Seasonality': colors['accent_orange'],
        'Moderate Seasonality': colors['accent_blue'],
        'Low Seasonality': colors['accent_green']
    }
    
    bar_colors = [color_map.get(level, colors['accent_purple']) for level in top_seasonal['seasonality_level']]
    
    fig = go.Figure(data=[
        go.Bar(
            y=top_seasonal['category'],
            x=top_seasonal['seasonality_score'],
            orientation='h',
            marker_color=bar_colors,
            text=[f"{val:.3f}" for val in top_seasonal['seasonality_score']],
            textposition='outside',
            textfont=dict(color=colors['text_primary']),
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Seasonality Score: %{x:.3f}<br>" +
                "Level: %{customdata[0]}<br>" +
                "Avg Monthly Revenue: R$ %{customdata[1]:,.0f}<br>" +
                "<extra></extra>"
            ),
            customdata=list(zip(top_seasonal['seasonality_level'], top_seasonal['avg_monthly_revenue']))
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="Top 15 Most Seasonal Product Categories",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Seasonality Score (Coefficient of Variation)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="Product Category",
            color=colors['text_secondary'],
            categoryorder='total ascending'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=600,
        margin=dict(l=200, r=50, t=80, b=50)
    )
    
    return fig

def create_inventory_recommendations_table(inventory_recommendations):
    """Create inventory optimization recommendations table"""
    colors = get_theme_colors()
    
    # Get top 15 categories by revenue
    top_categories = inventory_recommendations.head(15)
    
    # Create color mapping for risk levels
    risk_colors = {
        'High': colors['accent_pink'],
        'Medium': colors['accent_orange'],
        'Low': colors['accent_green']
    }
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Category', 'Seasonality Level', 'Inventory Strategy', 'Risk Level', 'Buffer Stock', 'Avg Monthly Revenue'],
            fill_color=colors['card_bg'],
            font=dict(color=colors['text_primary'], size=12),
            align='left',
            height=40
        ),
        cells=dict(
            values=[
                top_categories['category'],
                top_categories['seasonality_level'],
                top_categories['inventory_strategy'],
                top_categories['risk_level'],
                top_categories['buffer_stock_recommendation'],
                [f"R$ {val:,.0f}" for val in top_categories['avg_monthly_revenue']]
            ],
            fill_color=[
                [colors['secondary_bg']] * len(top_categories),
                [colors['secondary_bg']] * len(top_categories),
                [colors['secondary_bg']] * len(top_categories),
                [risk_colors.get(risk, colors['secondary_bg']) for risk in top_categories['risk_level']],
                [colors['secondary_bg']] * len(top_categories),
                [colors['secondary_bg']] * len(top_categories)
            ],
            font=dict(color=colors['text_primary'], size=11),
            align='left',
            height=35
        )
    )])
    
    fig.update_layout(
        title=dict(
            text="Inventory Optimization Recommendations",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        height=600,
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary'])
    )
    
    return fig

def render():
    """Render the Seasonal Intelligence page"""
    show_page_header(
        "Seasonal Intelligence",
        "Demand patterns, forecasting, and inventory optimization insights",
        "📈"
    )
    
    # Load data
    with st.spinner("Loading seasonal intelligence data..."):
        data = load_seasonal_data()
    
    if data is None:
        st.error("Unable to load seasonal intelligence data. Please check data files.")
        return
    
    # Key Seasonal Metrics
    create_section_divider("Seasonal Performance Metrics")
    
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
            "Peak Month", 
            f"Month {data['peak_month']['month']}", 
            delta=None,
            icon="📈"
        )
    
    with col3:
        create_metric_card(
            "Seasonal Variance", 
            f"{data['seasonal_variance_cv']:.1%}", 
            delta=None,
            icon="📊"
        )
    
    with col4:
        create_metric_card(
            "High Impact Events", 
            len(data['high_impact_events']), 
            delta=None,
            icon="🎯"
        )
    
    # Monthly Trends Analysis
    create_section_divider("Monthly Seasonal Patterns")
    
    st.plotly_chart(
        create_monthly_trends_chart(data['seasonal_variance']), 
        use_container_width=True
    )
    
    # Holiday Impact Analysis
    create_section_divider("Brazilian Holiday & Cultural Event Impact")
    
    st.plotly_chart(
        create_holiday_impact_chart(data['cultural_events']), 
        use_container_width=True
    )
    
    # Data Limitation Warning
    st.warning("""
    **⚠️ Data Limitation Warning**: Some holiday impacts may be misleading due to incomplete 2018 data:
    - **Christmas (-34.6%)**: Only 2017 data complete, missing 2018 holiday season
    - **Black Friday (-10.7%)**: Missing November 2018 data
    - **Independence Day (-45.4%)**: Accurate - genuinely low performance month
    - Dataset ends October 2018, missing key holiday seasons for complete analysis
    """)
    
    # Demand Forecasting
    create_section_divider("3-Month Demand Forecast")
    
    st.plotly_chart(
        create_forecasting_chart(data['forecasts']), 
        use_container_width=True
    )
    
    # Category Seasonality Analysis
    create_section_divider("Category Seasonality Analysis")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.plotly_chart(
            create_category_seasonality_chart(data['category_patterns']), 
            use_container_width=True
        )
    
    with col_right:
        create_info_card(
            "Most Seasonal Categories",
            f"""
            **Top 5 Most Seasonal:**
            1. {data['most_seasonal'].iloc[0]['category']} (CV: {data['most_seasonal'].iloc[0]['seasonality_score']:.3f})
            2. {data['most_seasonal'].iloc[1]['category']} (CV: {data['most_seasonal'].iloc[1]['seasonality_score']:.3f})
            3. {data['most_seasonal'].iloc[2]['category']} (CV: {data['most_seasonal'].iloc[2]['seasonality_score']:.3f})
            4. {data['most_seasonal'].iloc[3]['category']} (CV: {data['most_seasonal'].iloc[3]['seasonality_score']:.3f})
            5. {data['most_seasonal'].iloc[4]['category']} (CV: {data['most_seasonal'].iloc[4]['seasonality_score']:.3f})
            
            **Least Seasonal:**
            - {data['least_seasonal'].iloc[-1]['category']} (CV: {data['least_seasonal'].iloc[-1]['seasonality_score']:.3f})
            - {data['least_seasonal'].iloc[-2]['category']} (CV: {data['least_seasonal'].iloc[-2]['seasonality_score']:.3f})
            """,
            icon="📊"
        )
    
    # Inventory Optimization Recommendations
    create_section_divider("Inventory Optimization Recommendations")
    
    st.plotly_chart(
        create_inventory_recommendations_table(data['inventory_recommendations']), 
        use_container_width=True
    )
    
    # Key Insights and Recommendations
    create_section_divider("Strategic Insights & Recommendations")
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        create_info_card(
            "Peak Season Strategy",
            f"""
            **High-Impact Months Identified:**
            - **Mother's Day** (+31.5% revenue impact) - Highest performing event
            - **Father's Day** (+26.6% revenue impact) - Strong commercial opportunity
            - **Winter Vacation** (+24.5% revenue impact) - Seasonal demand peak
            
            **Preparation Timeline:**
            - Begin inventory buildup 4-8 weeks before major events
            - Focus on categories with high seasonality scores (CV > 0.8)
            - Implement dynamic pricing strategies during peak periods
            """,
            icon="🎯"
        )
    
    with col_insight2:
        create_info_card(
            "Inventory Risk Management",
            f"""
            **Risk Categories:**
            - **High Risk**: {len(data['inventory_recommendations'][data['inventory_recommendations']['risk_level'] == 'High'])} categories requiring careful management
            - **Medium Risk**: {len(data['inventory_recommendations'][data['inventory_recommendations']['risk_level'] == 'Medium'])} categories with moderate adjustments
            - **Low Risk**: {len(data['inventory_recommendations'][data['inventory_recommendations']['risk_level'] == 'Low'])} stable categories
            
            **Buffer Stock Strategy:**
            - High seasonality categories: 40-80% inventory adjustments
            - Stable categories: 20-30% buffer stock recommended
            - Balance portfolio with mix of seasonal and stable products
            """,
            icon="⚖️"
        )
    
    # Forecasting Model Performance
    create_info_card(
        "Forecasting Model Performance",
        f"""
        **3-Month Predictions:**
        - **November 2018 (Black Friday)**: Predicted R$ {data['forecasts'].iloc[0]['predicted_revenue']:,.0f} revenue with {data['forecasts'].iloc[0]['predicted_orders']:,} orders
        - **December 2018 (Christmas)**: Predicted R$ {data['forecasts'].iloc[1]['predicted_revenue']:,.0f} revenue with {data['forecasts'].iloc[1]['predicted_orders']:,} orders
        - **January 2019 (New Year)**: Predicted R$ {data['forecasts'].iloc[2]['predicted_revenue']:,.0f} revenue with {data['forecasts'].iloc[2]['predicted_orders']:,} orders
        
        **Note**: Confidence intervals are wide due to limited historical data. Model performance improves with more complete seasonal cycles.
        """,
        icon="🔮"
    )