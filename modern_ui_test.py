"""
Test the new modern UI components and navigation
"""

import streamlit as st
import sys
import os
import plotly.express as px
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard.components.modern_styling import apply_modern_theme, get_modern_theme_colors
from dashboard.components.modern_navigation import create_top_navigation
from dashboard.components.modern_ui_components import (
    create_modern_kpi_card, 
    create_modern_chart_container, 
    apply_modern_chart_theme,
    create_info_banner
)

# Page configuration
st.set_page_config(
    page_title="Modern UI Test",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply modern theme
apply_modern_theme()

def main():
    """Test the modern UI components"""
    
    # Create top navigation
    selected_page = create_top_navigation()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Welcome banner
    create_info_banner(
        "🎉 Welcome to the new modern UI! This design features glass morphism, responsive layouts, and smooth animations.",
        type="success",
        dismissible=True
    )
    
    # Test KPI cards
    st.markdown("## 📊 Modern KPI Cards")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_modern_kpi_card(
            title="Total Revenue",
            value="R$ 13.6M",
            delta="+15.2%",
            icon="💰",
            description="Last 30 days"
        )
    
    with col2:
        create_modern_kpi_card(
            title="Active Customers",
            value="99,441",
            delta="+8.7%",
            icon="👥",
            description="Unique customers"
        )
    
    with col3:
        create_modern_kpi_card(
            title="Avg Order Value",
            value="R$ 120.65",
            delta="-2.1%",
            icon="🛒",
            description="Per transaction"
        )
    
    with col4:
        create_modern_kpi_card(
            title="Satisfaction",
            value="4.09/5",
            delta="+0.3",
            icon="⭐",
            description="Customer rating"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Test charts
    st.markdown("## 📈 Modern Chart Containers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        def create_sample_line_chart():
            # Sample data
            dates = pd.date_range('2023-01-01', periods=12, freq='M')
            values = np.random.randint(50000, 150000, 12)
            df = pd.DataFrame({'Date': dates, 'Revenue': values})
            
            fig = px.line(df, x='Date', y='Revenue', title='Monthly Revenue Trend')
            fig = apply_modern_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        
        create_modern_chart_container(
            title="Revenue Trends",
            chart_content=create_sample_line_chart,
            description="Monthly revenue performance over time"
        )
    
    with col2:
        def create_sample_bar_chart():
            # Sample data
            categories = ['Electronics', 'Fashion', 'Home', 'Sports', 'Books']
            values = np.random.randint(10000, 50000, 5)
            df = pd.DataFrame({'Category': categories, 'Sales': values})
            
            fig = px.bar(df, x='Category', y='Sales', title='Sales by Category')
            fig = apply_modern_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        
        create_modern_chart_container(
            title="Category Performance",
            chart_content=create_sample_bar_chart,
            description="Sales distribution across product categories"
        )
    
    # Full width chart
    def create_sample_area_chart():
        # Sample data
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        values = np.cumsum(np.random.randn(30)) + 100
        df = pd.DataFrame({'Date': dates, 'Cumulative Sales': values})
        
        fig = px.area(df, x='Date', y='Cumulative Sales', title='Cumulative Sales Growth')
        fig = apply_modern_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    create_modern_chart_container(
        title="Growth Analytics",
        chart_content=create_sample_area_chart,
        description="Cumulative sales performance with trend analysis",
        full_width=True
    )
    
    # Test responsive grid
    st.markdown("## 🎯 Responsive Features")
    
    create_info_banner(
        "📱 This UI is fully responsive! Try resizing your browser window or viewing on mobile devices.",
        type="info"
    )
    
    # Test different banner types
    col1, col2 = st.columns(2)
    
    with col1:
        create_info_banner("✅ Success message example", type="success")
        create_info_banner("⚠️ Warning message example", type="warning")
    
    with col2:
        create_info_banner("ℹ️ Info message example", type="info")
        create_info_banner("❌ Error message example", type="error")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; opacity: 0.8;">
        <p>🎨 Modern UI Test Complete • Glass Morphism • Responsive Design • Smooth Animations</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()