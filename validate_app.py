"""
Validation script to check if the Streamlit app can be imported and basic functions work
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_app():
    """Validate that the app can be imported and basic functions work"""
    try:
        # Test imports
        from dashboard.components.styling import get_theme_colors, apply_dark_theme
        from dashboard.components.navigation import setup_sidebar_navigation, show_page_header
        from dashboard.components.ui_components import create_metric_card, create_info_card
        from dashboard.pages import executive_overview
        
        print("✅ All imports successful")
        
        # Test theme colors
        colors = get_theme_colors()
        assert 'primary_bg' in colors
        assert 'accent_blue' in colors
        print("✅ Theme colors working")
        
        # Test that pages have render functions
        assert hasattr(executive_overview, 'render')
        print("✅ Page modules have render functions")
        
        print("\n🎉 App validation successful!")
        print("\nTo run the dashboard:")
        print("streamlit run app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    validate_app()