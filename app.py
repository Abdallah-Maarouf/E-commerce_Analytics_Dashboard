"""
E-commerce Analytics Dashboard - Modern Responsive Version
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard.components.styling import apply_dark_theme
from dashboard.components.navigation import setup_sidebar_navigation
from dashboard.components.ui_components import show_error_message, create_info_banner

# Import pages
try:
    from dashboard.pages import executive_overview, market_expansion, customer_analytics, seasonal_intelligence, payment_operations
except ImportError as e:
    st.error(f"Error importing pages: {e}")
    st.stop()

# Modern page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide sidebar since we're using top navigation
    menu_items={
        'Get Help': 'https://github.com/your-username/ecommerce-analytics-dashboard',
        'Report a bug': 'https://github.com/your-username/ecommerce-analytics-dashboard/issues',
        'About': "# Modern E-commerce Analytics Dashboard\nBuilt with Streamlit • Responsive Design • Glass Morphism UI"
    }
)

# Apply modern theme immediately
apply_dark_theme()

# Force CSS injection for deployment
st.markdown("""
<style>
/* Ensure critical styles load first */
.stApp {
    background: linear-gradient(135deg, #1a1625 0%, #2a1f3d 100%) !important;
    color: #ffffff !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

def main():
    """Main application with modern top navigation"""
    try:
        # Create top navigation and get selected page (using updated function)
        selected_page = setup_sidebar_navigation()
        
        # Add some spacing after navigation
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Page routing with modern error handling
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
            # Modern welcome page
            st.markdown("""
            <div class="glass-card fade-in-up" style="text-align: center; padding: 3rem;">
                <h1>🚀 Welcome to Your Analytics Dashboard</h1>
                <p style="font-size: 1.2rem; margin-bottom: 2rem;">
                    Explore comprehensive insights from Brazilian e-commerce data
                </p>
                <p style="opacity: 0.8;">
                    Use the navigation tabs above to explore different aspects of the business
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        create_info_banner(
            f"Application Error: {str(e)}", 
            type="error"
        )
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <h3>🔧 Something went wrong</h3>
            <p>Please refresh the page or try again later.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()