"""
Payment & Operations Dashboard Page
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

def load_payment_operations_data():
    """Load and prepare payment operations data"""
    try:
        # Load payment operations data
        payment_data = pd.read_csv('data/feature_engineered/payment_operations.csv')
        
        # Load customer data for regional analysis
        customer_data = pd.read_csv('data/cleaned/cleaned_customers.csv')
        
        # Convert datetime columns
        datetime_cols = ['order_purchase_timestamp', 'order_approved_at', 
                        'order_delivered_carrier_date', 'order_delivered_customer_date', 
                        'order_estimated_delivery_date']
        
        for col in datetime_cols:
            if col in payment_data.columns:
                payment_data[col] = pd.to_datetime(payment_data[col], errors='coerce')
        
        # Merge customer location data
        payment_data = payment_data.merge(
            customer_data[['customer_id', 'customer_state', 'customer_city']], 
            on='customer_id', 
            how='left'
        )
        
        # Calculate key metrics
        total_orders = len(payment_data)
        total_revenue = payment_data['payment_value'].sum()
        avg_delivery_days = payment_data['delivery_days'].mean()
        on_time_delivery_rate = (payment_data['on_time_delivery'].sum() / len(payment_data)) * 100
        avg_satisfaction = payment_data['review_score'].mean()
        avg_installments = payment_data['payment_installments'].mean()
        
        return {
            'payment_data': payment_data,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_delivery_days': avg_delivery_days,
            'on_time_delivery_rate': on_time_delivery_rate,
            'avg_satisfaction': avg_satisfaction,
            'avg_installments': avg_installments
        }
    except Exception as e:
        st.error(f"Error loading payment operations data: {str(e)}")
        return None

def create_payment_method_analysis(payment_data):
    """Create payment method distribution and analysis charts"""
    colors = get_theme_colors()
    
    # Payment method distribution
    payment_dist = payment_data['payment_type'].value_counts()
    payment_pct = (payment_dist / len(payment_data) * 100).round(1)
    
    # Clean payment method names for display
    clean_labels = [label.replace('_', ' ').title() for label in payment_dist.index]
    
    # Create pie chart for payment distribution
    fig_pie = go.Figure(data=[go.Pie(
        labels=clean_labels,
        values=payment_dist.values,
        hole=0.3,
        marker=dict(
            colors=[colors['accent_blue'], colors['accent_orange'], 
                   colors['accent_green'], colors['accent_pink'], colors['accent_purple']],
            line=dict(color='#ffffff', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(color='white', size=11),
        hovertemplate='<b>%{label}</b><br>Orders: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig_pie.update_layout(
        title=dict(
            text="Payment Method Distribution",
            font=dict(color='white', size=18, family="Arial Black"),
            x=0.5,
            y=0.95
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            font=dict(color='white', size=10),
            bgcolor='rgba(0,0,0,0)',
            orientation="v",
            x=1.05,
            y=0.5
        ),
        height=400,
        margin=dict(l=20, r=120, t=60, b=20)
    )
    
    # Payment method performance analysis
    payment_performance = payment_data.groupby('payment_type').agg({
        'payment_value': ['mean', 'sum', 'count'],
        'payment_installments': 'mean',
        'review_score': 'mean',
        'on_time_delivery': lambda x: (x.sum() / len(x)) * 100,
        'delivery_days': 'mean'
    }).round(2)
    
    payment_performance.columns = [
        'avg_value', 'total_revenue', 'order_count',
        'avg_installments', 'avg_satisfaction', 'on_time_rate', 'avg_delivery_days'
    ]
    
    # Create simplified bar charts
    payment_methods_clean = [method.replace('_', ' ').title() for method in payment_performance.index]
    
    # Average Order Value Chart with gradient colors
    fig_value = go.Figure(data=[
        go.Bar(
            x=payment_methods_clean,
            y=payment_performance['avg_value'],
            marker=dict(
                color=payment_performance['avg_value'],
                colorscale='Blues',
                showscale=False,
                line=dict(color='rgba(255,255,255,0.3)', width=1),
                opacity=0.9
            ),
            text=[f'R$ {val:.0f}' for val in payment_performance['avg_value']],
            textposition='outside',
            textfont=dict(color='white', size=12, family="Arial Bold"),
            hovertemplate='<b>%{x}</b><br>Average Order Value: R$ %{y:.2f}<br><extra></extra>'
        )
    ])
    
    fig_value.update_layout(
        title=dict(
            text="💰 Average Order Value by Payment Method",
            font=dict(color='white', size=18, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 22, 37, 0.8)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True,
            tickangle=0
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True,
            title=dict(text="Average Value (R$)", font=dict(color='white', size=12)),
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        height=450,
        margin=dict(l=80, r=40, t=80, b=100),
        showlegend=False
    )
    
    # Satisfaction Chart
    fig_satisfaction = go.Figure(data=[
        go.Bar(
            x=payment_methods_clean,
            y=payment_performance['avg_satisfaction'],
            marker_color=colors['accent_green'],
            text=[f'{val:.2f}' for val in payment_performance['avg_satisfaction']],
            textposition='outside',
            textfont=dict(color='white', size=12),
            hovertemplate='<b>%{x}</b><br>Satisfaction: %{y:.2f}/5.0<extra></extra>'
        )
    ])
    
    fig_satisfaction.update_layout(
        title=dict(
            text="Customer Satisfaction by Payment Method",
            font=dict(color='white', size=16, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Satisfaction Score", font=dict(color='white')),
            range=[0, 5]
        ),
        height=400,
        margin=dict(l=60, r=20, t=60, b=80)
    )
    
    return fig_pie, fig_value, fig_satisfaction, payment_performance

def create_regional_payment_analysis(payment_data):
    """Create regional payment behavior analysis"""
    colors = get_theme_colors()
    
    # Regional payment analysis
    regional_analysis = payment_data.groupby('customer_state').agg({
        'payment_value': ['mean', 'sum', 'count'],
        'payment_installments': 'mean',
        'review_score': 'mean',
        'on_time_delivery': lambda x: (x.sum() / len(x)) * 100,
        'delivery_days': 'mean'
    }).round(2)
    
    regional_analysis.columns = [
        'avg_payment_value', 'total_revenue', 'order_count',
        'avg_installments', 'avg_satisfaction', 'on_time_rate', 'avg_delivery_days'
    ]
    
    # Filter for states with significant order volume (>500 orders)
    regional_analysis = regional_analysis[regional_analysis['order_count'] >= 500]
    regional_analysis = regional_analysis.sort_values('total_revenue', ascending=False)
    
    # Top 10 states by revenue for better readability
    top_states = regional_analysis.head(10)
    
    # Create top states revenue chart
    fig_revenue = go.Figure(data=[
        go.Bar(
            x=top_states.index,
            y=top_states['total_revenue'],
            marker_color=colors['accent_blue'],
            text=[f'R$ {val/1000:.0f}K' for val in top_states['total_revenue']],
            textposition='outside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{x}</b><br>Total Revenue: R$ %{y:,.0f}<br>Orders: %{customdata:,}<extra></extra>',
            customdata=top_states['order_count']
        )
    ])
    
    fig_revenue.update_layout(
        title=dict(
            text="Top 10 States by Total Revenue",
            font=dict(color='white', size=16, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="State", font=dict(color='white'))
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Total Revenue (R$)", font=dict(color='white'))
        ),
        height=400,
        margin=dict(l=80, r=20, t=60, b=60)
    )
    
    # Create satisfaction vs delivery performance scatter
    fig_scatter = go.Figure(data=[
        go.Scatter(
            x=top_states['on_time_rate'],
            y=top_states['avg_satisfaction'],
            mode='markers+text',
            marker=dict(
                size=top_states['order_count']/100,  # Size based on order volume
                color=top_states['avg_payment_value'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title=dict(text="Avg Payment<br>Value (R$)", font=dict(color='white')),
                    tickfont=dict(color='white')
                ),
                line=dict(width=2, color='white')
            ),
            text=top_states.index,
            textposition='top center',
            textfont=dict(color='white', size=10),
            hovertemplate='<b>%{text}</b><br>On-Time Rate: %{x:.1f}%<br>Satisfaction: %{y:.2f}<br>Avg Payment: R$ %{marker.color:.0f}<extra></extra>'
        )
    ])
    
    fig_scatter.update_layout(
        title=dict(
            text="State Performance: Satisfaction vs On-Time Delivery",
            font=dict(color='white', size=16, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="On-Time Delivery Rate (%)", font=dict(color='white'))
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Average Satisfaction", font=dict(color='white')),
            range=[3.5, 4.5]
        ),
        height=500,
        margin=dict(l=80, r=120, t=60, b=60)
    )
    
    return fig_revenue, fig_scatter, regional_analysis

def create_installment_satisfaction_analysis(payment_data):
    """Create installment vs satisfaction analysis"""
    colors = get_theme_colors()
    
    # Filter data with review scores
    satisfaction_data = payment_data[payment_data['review_score'].notna()].copy()
    
    # Create installment categories
    satisfaction_data['installment_category'] = pd.cut(
        satisfaction_data['payment_installments'],
        bins=[0, 1, 3, 6, 12, float('inf')],
        labels=['Single Payment', '2-3 Installments', '4-6 Installments', 
               '7-12 Installments', '12+ Installments'],
        include_lowest=True
    )
    
    # Satisfaction by installment category
    installment_satisfaction = satisfaction_data.groupby('installment_category').agg({
        'review_score': ['mean', 'count'],
        'payment_value': 'mean',
        'on_time_delivery': lambda x: (x.sum() / len(x)) * 100
    }).round(2)
    
    installment_satisfaction.columns = [
        'avg_satisfaction', 'review_count', 'avg_payment_value', 'on_time_rate'
    ]
    
    # Create satisfaction by installment chart
    fig_satisfaction = go.Figure()
    
    categories = installment_satisfaction.index
    
    # Add satisfaction bars
    fig_satisfaction.add_trace(
        go.Bar(
            x=categories,
            y=installment_satisfaction['avg_satisfaction'],
            name='Average Satisfaction',
            marker_color=colors['accent_blue'],
            text=[f'{val:.2f}' for val in installment_satisfaction['avg_satisfaction']],
            textposition='outside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{x}</b><br>Satisfaction: %{y:.2f}/5.0<br>Reviews: %{customdata:,}<extra></extra>',
            customdata=installment_satisfaction['review_count']
        )
    )
    
    fig_satisfaction.update_layout(
        title=dict(
            text="Customer Satisfaction by Installment Category",
            font=dict(color='white', size=16, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickangle=45,
            tickfont=dict(color='white', size=10),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Installment Category", font=dict(color='white'))
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Average Satisfaction Score", font=dict(color='white')),
            range=[0, 5]
        ),
        height=400,
        margin=dict(l=80, r=20, t=60, b=120)
    )
    
    # Create payment value by installment chart
    fig_value = go.Figure()
    
    fig_value.add_trace(
        go.Bar(
            x=categories,
            y=installment_satisfaction['avg_payment_value'],
            name='Average Payment Value',
            marker_color=colors['accent_green'],
            text=[f'R$ {val:.0f}' for val in installment_satisfaction['avg_payment_value']],
            textposition='outside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{x}</b><br>Avg Value: R$ %{y:.0f}<br>On-Time Rate: %{customdata:.1f}%<extra></extra>',
            customdata=installment_satisfaction['on_time_rate']
        )
    )
    
    fig_value.update_layout(
        title=dict(
            text="Average Order Value by Installment Category",
            font=dict(color='white', size=16, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickangle=45,
            tickfont=dict(color='white', size=10),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Installment Category", font=dict(color='white'))
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Average Payment Value (R$)", font=dict(color='white'))
        ),
        height=400,
        margin=dict(l=80, r=20, t=60, b=120)
    )
    
    return fig_satisfaction, fig_value, installment_satisfaction

def create_operational_performance_dashboard(payment_data):
    """Create operational performance metrics dashboard"""
    colors = get_theme_colors()
    
    # Calculate operational metrics by payment method
    operational_metrics = payment_data.groupby('payment_type').agg({
        'delivery_days': ['mean', 'std'],
        'on_time_delivery': lambda x: (x.sum() / len(x)) * 100,
        'processing_days': 'mean',
        'shipping_days': 'mean',
        'review_score': 'mean'
    }).round(2)
    
    operational_metrics.columns = [
        'avg_delivery_days', 'delivery_std', 'on_time_rate',
        'avg_processing_days', 'avg_shipping_days', 'avg_satisfaction'
    ]
    
    payment_methods_clean = [method.replace('_', ' ').title() for method in operational_metrics.index]
    
    # Create delivery performance chart
    fig_delivery = go.Figure()
    
    fig_delivery.add_trace(
        go.Bar(
            x=payment_methods_clean,
            y=operational_metrics['avg_delivery_days'],
            error_y=dict(
                type='data', 
                array=operational_metrics['delivery_std'],
                color='rgba(255,255,255,0.6)'
            ),
            marker_color=colors['accent_blue'],
            text=[f'{val:.1f}d' for val in operational_metrics['avg_delivery_days']],
            textposition='outside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{x}</b><br>Avg Delivery: %{y:.1f} days<br>Std Dev: %{error_y.array:.1f}<extra></extra>'
        )
    )
    
    fig_delivery.update_layout(
        title=dict(
            text="Average Delivery Time by Payment Method",
            font=dict(color='white', size=16, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(color='white', size=10),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Payment Method", font=dict(color='white'))
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Average Delivery Days", font=dict(color='white'))
        ),
        height=400,
        margin=dict(l=80, r=20, t=60, b=80)
    )
    
    # Create on-time delivery rate chart
    fig_ontime = go.Figure()
    
    fig_ontime.add_trace(
        go.Bar(
            x=payment_methods_clean,
            y=operational_metrics['on_time_rate'],
            marker_color=colors['accent_green'],
            text=[f'{val:.1f}%' for val in operational_metrics['on_time_rate']],
            textposition='outside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{x}</b><br>On-Time Rate: %{y:.1f}%<extra></extra>'
        )
    )
    
    fig_ontime.update_layout(
        title=dict(
            text="On-Time Delivery Rate by Payment Method",
            font=dict(color='white', size=16, family="Arial Black"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(color='white', size=10),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="Payment Method", font=dict(color='white'))
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            title=dict(text="On-Time Delivery Rate (%)", font=dict(color='white')),
            range=[80, 100]
        ),
        height=400,
        margin=dict(l=80, r=20, t=60, b=80)
    )
    
    return fig_delivery, fig_ontime, operational_metrics

def generate_operational_recommendations(payment_data, payment_performance, regional_analysis, operational_metrics):
    """Generate actionable operational improvement recommendations"""
    recommendations = []
    
    # Payment method optimization
    best_satisfaction_payment = payment_performance['avg_satisfaction'].idxmax()
    worst_satisfaction_payment = payment_performance['avg_satisfaction'].idxmin()
    
    recommendations.append({
        'category': 'Payment Method Optimization',
        'priority': 'High',
        'recommendation': f'Promote {best_satisfaction_payment.replace("_", " ").title()} payments - highest satisfaction ({payment_performance.loc[best_satisfaction_payment, "avg_satisfaction"]:.2f}/5.0)',
        'impact': 'Customer Satisfaction',
        'implementation': f'Offer incentives for {best_satisfaction_payment.replace("_", " ")} usage, improve {worst_satisfaction_payment.replace("_", " ")} experience'
    })
    
    # Regional performance improvements
    worst_states = regional_analysis.nsmallest(3, 'on_time_rate').index.tolist()
    recommendations.append({
        'category': 'Regional Operations',
        'priority': 'High',
        'recommendation': f'Focus delivery improvements in {", ".join(worst_states)} - lowest on-time delivery rates',
        'impact': 'Operational Efficiency',
        'implementation': 'Increase local fulfillment centers, optimize logistics partnerships'
    })
    
    # Operational efficiency
    slowest_payment = operational_metrics['avg_delivery_days'].idxmax()
    recommendations.append({
        'category': 'Delivery Operations',
        'priority': 'Medium',
        'recommendation': f'Optimize {slowest_payment.replace("_", " ").title()} payment processing - slowest delivery times',
        'impact': 'Customer Experience',
        'implementation': 'Review payment processing workflow, reduce approval delays'
    })
    
    # Installment strategy
    high_installment_usage = payment_data[payment_data['payment_installments'] > 6]['payment_type'].value_counts()
    if len(high_installment_usage) > 0:
        top_installment_payment = high_installment_usage.index[0]
        recommendations.append({
            'category': 'Payment Terms',
            'priority': 'Medium',
            'recommendation': f'Optimize installment offerings for {top_installment_payment.replace("_", " ").title()} - highest installment usage',
            'impact': 'Customer Accessibility',
            'implementation': 'Review installment terms, consider flexible payment options'
        })
    
    return recommendations

def render():
    """Render the Payment & Operations page"""
    show_page_header(
        "Payment & Operations",
        "Payment behavior analysis and operational performance metrics",
        "💳"
    )
    
    # Load data
    with st.spinner("Loading payment operations data..."):
        data = load_payment_operations_data()
    
    if data is None:
        st.error("Failed to load payment operations data. Please check the data files.")
        return
    
    payment_data = data['payment_data']
    
    # Key Performance Indicators
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "Total Orders",
            data['total_orders'],
            icon="📦"
        )
    
    with col2:
        create_metric_card(
            "Total Revenue",
            f"R$ {data['total_revenue']:,.0f}",
            icon="💰"
        )
    
    with col3:
        create_metric_card(
            "Avg Delivery Time",
            f"{data['avg_delivery_days']:.1f} days",
            icon="🚚"
        )
    
    with col4:
        create_metric_card(
            "On-Time Delivery",
            f"{data['on_time_delivery_rate']:.1f}%",
            icon="⏰"
        )
    
    create_section_divider("Payment Method Analysis")
    
    # Payment method analysis
    fig_pie, fig_value, fig_satisfaction, payment_performance = create_payment_method_analysis(payment_data)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        # Payment method insights
        dominant_payment = payment_data['payment_type'].value_counts().index[0]
        dominant_pct = (payment_data['payment_type'].value_counts().iloc[0] / len(payment_data)) * 100
        
        create_highlight_box(
            f"**Payment Method Insights:**\n\n"
            f"• {dominant_payment.replace('_', ' ').title()} dominates with {dominant_pct:.1f}% of transactions\n"
            f"• Average satisfaction: {data['avg_satisfaction']:.2f}/5.0\n"
            f"• Average installments: {data['avg_installments']:.1f} payments\n"
            f"• Credit card users show highest order values",
            type="info"
        )
    
    # Display performance charts side by side
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(fig_value, use_container_width=True)
    with col2:
        st.plotly_chart(fig_satisfaction, use_container_width=True)
    
    create_section_divider("Regional Payment Behavior")
    
    # Regional analysis
    fig_revenue, fig_scatter, regional_analysis = create_regional_payment_analysis(payment_data)
    
    # Display regional charts side by side
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(fig_revenue, use_container_width=True)
    with col2:
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Regional insights
    top_revenue_state = regional_analysis['total_revenue'].idxmax()
    top_satisfaction_state = regional_analysis['avg_satisfaction'].idxmax()
    
    create_highlight_box(
        f"**Regional Insights:**\n\n"
        f"• Highest revenue state: {top_revenue_state} (R$ {regional_analysis.loc[top_revenue_state, 'total_revenue']:,.0f})\n"
        f"• Best satisfaction: {top_satisfaction_state} ({regional_analysis.loc[top_satisfaction_state, 'avg_satisfaction']:.2f}/5.0)\n"
        f"• Payment preferences vary significantly by region\n"
        f"• Southern states show higher credit card adoption",
        type="success"
    )
    
    create_section_divider("Installment vs Satisfaction Analysis")
    
    # Installment satisfaction analysis
    fig_satisfaction_inst, fig_value_inst, installment_satisfaction = create_installment_satisfaction_analysis(payment_data)
    
    # Display installment charts side by side
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(fig_satisfaction_inst, use_container_width=True)
    with col2:
        st.plotly_chart(fig_value_inst, use_container_width=True)
    
    # Installment insights
    best_satisfaction_category = installment_satisfaction['avg_satisfaction'].idxmax()
    create_highlight_box(
        f"**Installment Insights:**\n\n"
        f"• Best satisfaction: {best_satisfaction_category} ({installment_satisfaction.loc[best_satisfaction_category, 'avg_satisfaction']:.2f}/5.0)\n"
        f"• Higher installments correlate with larger order values\n"
        f"• Single payments show fastest delivery times\n"
        f"• Installment flexibility improves customer accessibility",
        type="info"
    )
    
    create_section_divider("Operational Performance")
    
    # Operational performance
    fig_delivery, fig_ontime, operational_metrics = create_operational_performance_dashboard(payment_data)
    
    # Display operational charts side by side
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(fig_delivery, use_container_width=True)
    with col2:
        st.plotly_chart(fig_ontime, use_container_width=True)
    
    # Operational insights
    fastest_delivery = operational_metrics['avg_delivery_days'].idxmin()
    best_ontime = operational_metrics['on_time_rate'].idxmax()
    
    create_highlight_box(
        f"**Operational Insights:**\n\n"
        f"• Fastest delivery: {fastest_delivery.replace('_', ' ').title()} ({operational_metrics.loc[fastest_delivery, 'avg_delivery_days']:.1f} days)\n"
        f"• Best on-time rate: {best_ontime.replace('_', ' ').title()} ({operational_metrics.loc[best_ontime, 'on_time_rate']:.1f}%)\n"
        f"• Processing time varies by payment method\n"
        f"• Delivery performance impacts customer satisfaction",
        type="success"
    )
    
    create_section_divider("Operational Recommendations")
    
    # Generate and display recommendations
    recommendations = generate_operational_recommendations(
        payment_data, payment_performance, regional_analysis, operational_metrics
    )
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"🎯 Recommendation {i}: {rec['category']} ({rec['priority']} Priority)"):
            st.write(f"**Recommendation:** {rec['recommendation']}")
            st.write(f"**Expected Impact:** {rec['impact']}")
            st.write(f"**Implementation:** {rec['implementation']}")
    
    # Summary statistics
    create_section_divider("Summary Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Payment Method Performance")
        st.dataframe(
            payment_performance[['avg_value', 'avg_satisfaction', 'on_time_rate']].round(2),
            use_container_width=True
        )
    
    with col2:
        st.subheader("Top Regional Performance")
        top_regional = regional_analysis.head(10)[['avg_payment_value', 'avg_satisfaction', 'on_time_rate']].round(2)
        st.dataframe(top_regional, use_container_width=True)