"""
E-commerce Analytics Dashboard
Main Streamlit application with dark theme and navigation
"""

import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard.components.styling import apply_dark_theme, get_theme_colors
from dashboard.components.navigation import setup_sidebar_navigation
from dashboard.components.ui_components import show_loading_state, show_error_message
from dashboard.pages import executive_overview, market_expansion, customer_analytics, seasonal_intelligence, payment_operations

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark theme styling
apply_dark_theme()

def main():
    """Main application function with error handling and routing"""
    try:
        # Setup sidebar navigation
        selected_page = setup_sidebar_navigation()
        
        # Page routing
        if selected_page == "Executive Overview":
            executive_overview.render()
        elif selected_page == "Market Expansion":
            market_expansion.render()
        elif selected_page == "Customer Analytics":
            customer_analytics.render()
        elif selected_page == "Seasonal Intelligence":
            seasonal_intelligence.render()
        elif selected_page == "Payment & Operations":
            payment_operations.render()
        else:
            # Default to executive overview
            executive_overview.render()
            
    except Exception as e:
        show_error_message(f"Application Error: {str(e)}")
        st.error("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()