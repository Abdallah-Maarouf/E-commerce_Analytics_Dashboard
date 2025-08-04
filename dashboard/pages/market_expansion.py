"""
Market Expansion Dashboard Page
Interactive geographic analysis and expansion opportunities
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.components.navigation import show_page_header
from dashboard.components.ui_components import (
    create_metric_card, create_info_card, show_loading_state, 
    create_section_divider, create_highlight_box, create_progress_bar
)
from dashboard.components.styling import get_theme_colors
from market_expansion import MarketExpansionAnalyzer

@st.cache_data(ttl=3600)
def load_market_expansion_data():
    """Load and analyze market expansion data with caching"""
    try:
        analyzer = MarketExpansionAnalyzer()
        
        # Load data
        if not analyzer.load_data():
            return None
            
        # Run all analyses
        analyzer.analyze_market_penetration()
        analyzer.calculate_untapped_potential()
        analyzer.evaluate_seller_distribution()
        analyzer.analyze_delivery_performance_by_geography()
        expansion_opportunities, recommendations = analyzer.generate_expansion_opportunity_matrix()
        
        return {
            'state_summary': analyzer.state_summary,
            'expansion_opportunities': expansion_opportunities,
            'recommendations': recommendations,
            'insights': analyzer.insights
        }
    except Exception as e:
        st.error(f"Error loading market expansion data: {str(e)}")
        return None

def create_brazil_market_penetration_map(state_data):
    """Create interactive Brazil market visualization using horizontal bar chart"""
    colors = get_theme_colors()
    
    # Sort states by customer count for better visualization
    sorted_data = state_data.sort_values('customer_count', ascending=True).tail(20)  # Top 20 states
    
    # Create horizontal bar chart as an alternative to map
    fig = go.Figure()
    
    # Add bars with color based on market opportunity score
    fig.add_trace(go.Bar(
        y=sorted_data['state'],
        x=sorted_data['customer_count'],
        orientation='h',
        marker=dict(
            color=sorted_data['market_opportunity_score'],
            colorscale=[
                [0, colors['accent_pink']],
                [0.3, colors['accent_orange']],
                [0.6, colors['accent_blue']],
                [1.0, colors['accent_green']]
            ],
            colorbar=dict(
                title=dict(
                    text="Market Opportunity Score",
                    font=dict(color=colors['text_primary'])
                ),
                tickfont=dict(color=colors['text_secondary'])
            )
        ),
        text=[f"{val:,}" for val in sorted_data['customer_count']],
        textposition='outside',
        textfont=dict(color=colors['text_primary']),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Customers: %{x:,}<br>" +
            "Revenue: R$ %{customdata[0]:,.0f}<br>" +
            "Market Score: %{customdata[1]:.3f}<br>" +
            "Delivery Days: %{customdata[2]:.1f}<br>" +
            "Expansion Priority: %{customdata[3]}<br>" +
            "<extra></extra>"
        ),
        customdata=list(zip(
            sorted_data['total_revenue'],
            sorted_data['market_opportunity_score'],
            sorted_data['avg_delivery_days'],
            sorted_data['expansion_priority']
        ))
    ))
    
    fig.update_layout(
        title=dict(
            text="Brazilian Market Penetration by State (Top 20)",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Customer Count",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="State",
            color=colors['text_secondary'],
            categoryorder='total ascending'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=600,
        margin=dict(l=80, r=50, t=80, b=50)
    )
    
    return fig

def create_expansion_opportunity_matrix(state_data):
    """Create expansion opportunity matrix visualization"""
    colors = get_theme_colors()
    
    # Filter to show only states with meaningful data
    filtered_data = state_data[
        (state_data['market_size_score'].notna()) & 
        (state_data['growth_potential_score'].notna()) &
        (state_data['combined_opportunity_score'] > 0)
    ].copy()
    
    # Create scatter plot matrix
    fig = go.Figure()
    
    # Color mapping for expansion priority
    priority_colors = {
        'High Priority': colors['accent_green'],
        'Medium Priority': colors['accent_blue'],
        'Low Priority': colors['accent_orange'],
        'Optimization Priority': colors['accent_purple'],
        'Maintain & Optimize': colors['accent_pink'],
        'Not Recommended': colors['border_color']
    }
    
    for priority in filtered_data['expansion_priority'].unique():
        priority_data = filtered_data[filtered_data['expansion_priority'] == priority]
        
        if len(priority_data) == 0:
            continue
            
        fig.add_trace(go.Scatter(
            x=priority_data['market_size_score'],
            y=priority_data['growth_potential_score'],
            mode='markers+text',
            name=priority,
            text=priority_data['state'],
            textposition='middle right',
            textfont=dict(size=9, color=colors['text_primary']),
            marker=dict(
                size=np.maximum(priority_data['combined_opportunity_score'] * 40 + 8, 12),
                color=priority_colors.get(priority, colors['accent_blue']),
                opacity=0.8,
                line=dict(width=1, color=colors['text_primary'])
            ),
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Market Size Score: %{x:.3f}<br>" +
                "Growth Potential: %{y:.3f}<br>" +
                "Combined Score: %{customdata[0]:.3f}<br>" +
                "Priority: " + priority + "<br>" +
                "Population: %{customdata[1]:,}<br>" +
                "Untapped Revenue: R$ %{customdata[2]:,.0f}<br>" +
                "<extra></extra>"
            ),
            customdata=list(zip(
                priority_data['combined_opportunity_score'],
                priority_data['population'].fillna(0),
                priority_data['untapped_revenue_potential'].fillna(0)
            ))
        ))
    
    fig.update_layout(
        title=dict(
            text="Market Expansion Opportunity Matrix",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Market Size Score (Population + Economic Strength)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color'],
            range=[-0.05, 1.05]
        ),
        yaxis=dict(
            title="Growth Potential Score (Untapped Opportunity)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color'],
            range=[-0.05, 1.05]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500,
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0.8)',
            bordercolor=colors['border_color'],
            borderwidth=1,
            font=dict(color=colors['text_primary'], size=10)
        )
    )
    
    # Add quadrant lines
    fig.add_hline(y=0.5, line_dash="dash", line_color=colors['border_color'], opacity=0.5)
    fig.add_vline(x=0.5, line_dash="dash", line_color=colors['border_color'], opacity=0.5)
    
    # Add quadrant labels with better positioning
    fig.add_annotation(x=0.25, y=0.85, text="High Growth<br>Small Market", 
                      showarrow=False, font=dict(color=colors['text_secondary'], size=9),
                      bgcolor='rgba(0,0,0,0.5)', bordercolor=colors['border_color'])
    fig.add_annotation(x=0.75, y=0.85, text="High Growth<br>Large Market", 
                      showarrow=False, font=dict(color=colors['text_secondary'], size=9),
                      bgcolor='rgba(0,0,0,0.5)', bordercolor=colors['border_color'])
    fig.add_annotation(x=0.25, y=0.15, text="Low Growth<br>Small Market", 
                      showarrow=False, font=dict(color=colors['text_secondary'], size=9),
                      bgcolor='rgba(0,0,0,0.5)', bordercolor=colors['border_color'])
    fig.add_annotation(x=0.75, y=0.15, text="Low Growth<br>Large Market", 
                      showarrow=False, font=dict(color=colors['text_secondary'], size=9),
                      bgcolor='rgba(0,0,0,0.5)', bordercolor=colors['border_color'])
    
    return fig

def create_seller_distribution_analysis(state_data):
    """Create seller distribution vs customer demand analysis"""
    colors = get_theme_colors()
    
    # Filter states with meaningful data and get top 15
    valid_states = state_data[
        (state_data['customer_count'] > 0) & 
        (state_data['seller_count'] >= 0) &
        (state_data['customer_to_seller_ratio'].notna())
    ].copy()
    
    if len(valid_states) == 0:
        # Fallback: show a message
        fig = go.Figure()
        fig.add_annotation(
            text="No valid seller distribution data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color=colors['text_secondary'])
        )
        fig.update_layout(
            title="Seller Distribution Analysis",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
    
    top_states = valid_states.nlargest(15, 'customer_count')
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Customer to Seller Ratio by State', 'Seller Gap Analysis'),
        vertical_spacing=0.15
    )
    
    # Customer to Seller Ratio
    fig.add_trace(
        go.Bar(
            x=top_states['state'],
            y=top_states['customer_to_seller_ratio'].fillna(0),
            name='Customer:Seller Ratio',
            marker_color=colors['accent_blue'],
            text=[f"{ratio:.0f}:1" if pd.notna(ratio) and ratio > 0 else "N/A" 
                  for ratio in top_states['customer_to_seller_ratio']],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Add optimal ratio line
    fig.add_hline(y=30, line_dash="dash", line_color=colors['accent_green'], 
                  annotation_text="Optimal Ratio (30:1)", row=1, col=1)
    
    # Seller Gap Analysis
    seller_gap_values = top_states['seller_gap'].fillna(0)
    fig.add_trace(
        go.Bar(
            x=top_states['state'],
            y=seller_gap_values,
            name='Additional Sellers Needed',
            marker_color=colors['accent_orange'],
            text=[f"{gap:.0f}" if gap > 0 else "0" for gap in seller_gap_values],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=dict(
            text=f"Seller Distribution Analysis - Top {len(top_states)} States",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=700,
        showlegend=False
    )
    
    # Update axes
    fig.update_xaxes(color=colors['text_secondary'], gridcolor=colors['border_color'])
    fig.update_yaxes(color=colors['text_secondary'], gridcolor=colors['border_color'])
    
    return fig

def create_delivery_performance_geographic_analysis(state_data):
    """Create delivery performance analysis by geography"""
    colors = get_theme_colors()
    
    # Filter states with valid delivery data and get top 15 by total orders
    valid_delivery_data = state_data[
        (state_data['avg_delivery_days'].notna()) & 
        (state_data['on_time_rate'].notna()) &
        (state_data['total_orders'] > 0)
    ].copy()
    
    if len(valid_delivery_data) == 0:
        # Fallback: create a simple bar chart of delivery days
        top_states = state_data.nlargest(15, 'total_orders')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_states['state'],
            y=top_states['avg_delivery_days'].fillna(0),
            marker_color=colors['accent_blue'],
            text=[f"{days:.1f}d" if pd.notna(days) else "N/A" for days in top_states['avg_delivery_days']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=dict(
                text="Average Delivery Days by State",
                font=dict(color=colors['text_primary'], size=18),
                x=0.5
            ),
            xaxis=dict(
                title="State",
                color=colors['text_secondary'],
                gridcolor=colors['border_color']
            ),
            yaxis=dict(
                title="Average Delivery Days",
                color=colors['text_secondary'],
                gridcolor=colors['border_color']
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=colors['text_primary']),
            height=500
        )
        
        return fig
    
    # Get top states with valid data
    top_states = valid_delivery_data.nlargest(15, 'total_orders')
    
    fig = go.Figure()
    
    # Delivery performance scatter plot
    fig.add_trace(go.Scatter(
        x=top_states['avg_delivery_days'],
        y=top_states['on_time_rate'] * 100,
        mode='markers+text',
        text=top_states['state'],
        textposition='top center',
        textfont=dict(size=9, color=colors['text_primary']),
        marker=dict(
            size=np.maximum(np.sqrt(top_states['total_orders']) / 15, 8),  # Size based on order volume
            color=top_states['delivery_efficiency_score'].fillna(0.5),
            colorscale=[
                [0, colors['accent_pink']],
                [0.5, colors['accent_orange']],
                [1, colors['accent_green']]
            ],
            opacity=0.8,
            line=dict(width=1, color=colors['text_primary']),
            colorbar=dict(
                title=dict(
                    text="Delivery Efficiency",
                    font=dict(color=colors['text_primary'])
                ),
                tickfont=dict(color=colors['text_secondary'])
            )
        ),
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Avg Delivery Days: %{x:.1f}<br>" +
            "On-Time Rate: %{y:.1f}%<br>" +
            "Total Orders: %{customdata[0]:,}<br>" +
            "Efficiency Score: %{customdata[1]:.3f}<br>" +
            "<extra></extra>"
        ),
        customdata=list(zip(
            top_states['total_orders'],
            top_states['delivery_efficiency_score'].fillna(0.5)
        ))
    ))
    
    fig.update_layout(
        title=dict(
            text="Delivery Performance by State (Top 15 by Order Volume)",
            font=dict(color=colors['text_primary'], size=18),
            x=0.5
        ),
        xaxis=dict(
            title="Average Delivery Days",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        yaxis=dict(
            title="On-Time Delivery Rate (%)",
            color=colors['text_secondary'],
            gridcolor=colors['border_color']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_primary']),
        height=500
    )
    
    # Add performance quadrant lines if we have enough data
    if len(top_states) > 3:
        avg_delivery = top_states['avg_delivery_days'].mean()
        avg_ontime = top_states['on_time_rate'].mean() * 100
        
        fig.add_hline(y=avg_ontime, line_dash="dash", line_color=colors['border_color'], opacity=0.5,
                     annotation_text=f"Avg On-Time: {avg_ontime:.1f}%")
        fig.add_vline(x=avg_delivery, line_dash="dash", line_color=colors['border_color'], opacity=0.5,
                     annotation_text=f"Avg Delivery: {avg_delivery:.1f}d")
    
    return fig

def create_expansion_recommendations_panel(recommendations):
    """Create actionable expansion recommendations panel"""
    colors = get_theme_colors()
    
    st.markdown("### 🎯 Top Expansion Recommendations")
    
    # Display top 5 recommendations
    for i, rec in enumerate(recommendations[:5], 1):
        with st.expander(f"#{i} {rec['state']} - {rec['priority']}", expanded=(i <= 2)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Opportunity Score:** {rec['opportunity_score']:.3f}")
                st.markdown("**Key Recommendations:**")
                for recommendation in rec['recommendations']:
                    st.markdown(f"• {recommendation}")
            
            with col2:
                st.markdown("**Key Metrics:**")
                metrics = rec['key_metrics']
                st.metric("Customers", f"{metrics['customers']:,}")
                st.metric("Sellers", f"{metrics['sellers']:,}")
                if metrics['untapped_customers'] > 0:
                    st.metric("Untapped Customers", f"{metrics['untapped_customers']:,}")
                if metrics['seller_gap'] > 0:
                    st.metric("Seller Gap", f"{metrics['seller_gap']:,}")
                if metrics['avg_delivery_days'] > 0:
                    st.metric("Avg Delivery", f"{metrics['avg_delivery_days']:.1f} days")

def render():
    """Render the Market Expansion page"""
    show_page_header(
        "Market Expansion",
        "Geographic growth opportunities and market analysis",
        "🗺️"
    )
    
    # Load data
    with st.spinner("Loading market expansion analysis..."):
        data = load_market_expansion_data()
    
    if data is None:
        st.error("Unable to load market expansion data. Please check data files and analysis modules.")
        return
    
    state_data = data['state_summary']
    recommendations = data['recommendations']
    insights = data['insights']
    
    # Debug information (can be removed in production)
    with st.expander("🔍 Data Quality Check", expanded=False):
        st.write(f"**States loaded:** {len(state_data)}")
        st.write(f"**States with customers > 0:** {(state_data['customer_count'] > 0).sum()}")
        st.write(f"**States with revenue > 0:** {(state_data['total_revenue'] > 0).sum()}")
        st.write(f"**Recommendations generated:** {len(recommendations)}")
        
        # Show sample of state data
        st.write("**Sample state data:**")
        sample_cols = ['state', 'customer_count', 'total_revenue', 'expansion_priority']
        available_cols = [col for col in sample_cols if col in state_data.columns]
        if available_cols:
            st.dataframe(state_data[available_cols].head(10))
    
    # Key Market Expansion Metrics
    create_section_divider("Market Expansion Overview")
    
    # Calculate key metrics
    total_states = len(state_data)
    high_priority_states = len(state_data[state_data['expansion_priority'] == 'High Priority'])
    medium_priority_states = len(state_data[state_data['expansion_priority'] == 'Medium Priority'])
    optimization_priority_states = len(state_data[state_data['expansion_priority'] == 'Optimization Priority'])
    total_untapped_revenue = state_data['untapped_revenue_potential'].fillna(0).sum()
    total_seller_gap = state_data['seller_gap'].fillna(0).sum()
    avg_opportunity_score = state_data['combined_opportunity_score'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "States Analyzed", 
            total_states, 
            icon="🗺️"
        )
    
    with col2:
        # Show the most relevant priority metric based on what's available
        if high_priority_states > 0:
            create_metric_card(
                "High Priority States", 
                high_priority_states, 
                icon="🎯"
            )
        elif medium_priority_states > 0:
            create_metric_card(
                "Medium Priority States", 
                medium_priority_states, 
                icon="🎯"
            )
        elif optimization_priority_states > 0:
            create_metric_card(
                "Optimization Priority", 
                optimization_priority_states, 
                icon="⚡"
            )
        else:
            create_metric_card(
                "Avg Opportunity Score", 
                f"{avg_opportunity_score:.3f}", 
                icon="📊"
            )
    
    with col3:
        create_metric_card(
            "Untapped Revenue", 
            total_untapped_revenue, 
            icon="💰"
        )
    
    with col4:
        create_metric_card(
            "Total Seller Gap", 
            total_seller_gap, 
            icon="👥"
        )
    
    # Interactive Brazil Map
    create_section_divider("Geographic Market Penetration")
    
    st.plotly_chart(
        create_brazil_market_penetration_map(state_data), 
        use_container_width=True
    )
    
    # Expansion Opportunity Matrix
    create_section_divider("Expansion Opportunity Analysis")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.plotly_chart(
            create_expansion_opportunity_matrix(state_data), 
            use_container_width=True
        )
    
    with col_right:
        # Priority distribution
        priority_dist = state_data['expansion_priority'].value_counts()
        
        st.markdown("#### Expansion Priority Distribution")
        for priority, count in priority_dist.items():
            percentage = (count / len(state_data)) * 100
            create_progress_bar(
                count, 
                len(state_data), 
                label=f"{priority}: {count} states",
                color=get_theme_colors()['accent_blue']
            )
    
    # Seller Distribution Analysis
    create_section_divider("Seller Distribution vs Customer Demand")
    
    st.plotly_chart(
        create_seller_distribution_analysis(state_data), 
        use_container_width=True
    )
    
    # Delivery Performance Analysis
    create_section_divider("Delivery Performance by Geography")
    
    st.plotly_chart(
        create_delivery_performance_geographic_analysis(state_data), 
        use_container_width=True
    )
    
    # Actionable Recommendations
    create_section_divider("Actionable Expansion Recommendations")
    
    create_expansion_recommendations_panel(recommendations)
    
    # Key Insights Summary
    create_section_divider("Key Market Insights")
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        # Market penetration insights
        penetration_insights = [insight for insight in insights if insight['category'] == 'Market Penetration']
        if penetration_insights:
            create_info_card(
                "Market Penetration Analysis",
                "\n\n".join([insight['insight'] for insight in penetration_insights]),
                icon="📊"
            )
    
    with col_insight2:
        # Untapped potential insights
        potential_insights = [insight for insight in insights if insight['category'] == 'Untapped Potential']
        if potential_insights:
            create_info_card(
                "Untapped Market Potential",
                "\n\n".join([insight['insight'] for insight in potential_insights]),
                icon="💎"
            )
    
    # Seller distribution insights
    seller_insights = [insight for insight in insights if insight['category'] == 'Seller Distribution']
    if seller_insights:
        create_info_card(
            "Seller Distribution Strategy",
            "\n\n".join([insight['insight'] for insight in seller_insights]),
            icon="🏪"
        )
    
    # Delivery performance insights
    delivery_insights = [insight for insight in insights if insight['category'] == 'Delivery Performance']
    if delivery_insights:
        create_info_card(
            "Delivery Performance Optimization",
            "\n\n".join([insight['insight'] for insight in delivery_insights]),
            icon="🚚"
        )
    
    # Strategic Summary - Dynamic based on actual data
    create_section_divider("Strategic Market Expansion Summary")
    
    # Build priority summary
    if high_priority_states > 0:
        priority_summary = f"{high_priority_states} high-priority states identified"
    elif medium_priority_states > 0:
        priority_summary = f"{medium_priority_states} medium-priority states identified"
    elif optimization_priority_states > 0:
        priority_summary = f"{optimization_priority_states} states ready for optimization"
    else:
        priority_summary = f"{total_states} states analyzed for expansion potential"
    
    # Format numbers safely
    revenue_formatted = f"R$ {total_untapped_revenue:,.0f}" if total_untapped_revenue > 0 else "R$ 0"
    seller_gap_formatted = f"{total_seller_gap:,.0f}" if total_seller_gap > 0 else "0"
    
    summary_content = f"""
**Market Opportunity Analysis:**

📈 **Market Status**: {priority_summary} with {revenue_formatted} in untapped revenue potential.

🏪 **Seller Network Gap**: {seller_gap_formatted} additional sellers needed across all markets to achieve optimal customer-to-seller ratios.

🎯 **Strategic Focus**: Analysis reveals varying expansion priorities across Brazilian states, with opportunities ranging from market optimization in established areas to selective expansion in underserved regions.

🚚 **Operational Considerations**: Delivery performance varies significantly by geography - infrastructure investment needed in remote states to maintain service quality standards.

💡 **Recommended Actions**: 
- Prioritize states with highest combined opportunity scores
- Establish strategic local partnerships for market entry
- Gradually expand seller network while monitoring delivery performance
- Focus on operational excellence in existing markets before major expansion
"""
    
    create_info_card(
        "Strategic Market Expansion Summary",
        summary_content,
        icon="🎯"
    )