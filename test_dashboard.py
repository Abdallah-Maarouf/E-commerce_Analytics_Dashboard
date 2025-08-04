"""
Test script to verify dashboard framework components
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all dashboard components can be imported"""
    try:
        from dashboard.components.styling import apply_dark_theme, get_theme_colors
        from dashboard.components.navigation import setup_sidebar_navigation
        from dashboard.components.ui_components import create_metric_card, show_loading_state
        from dashboard.pages import executive_overview, market_expansion, customer_analytics
        print("✅ All dashboard components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_theme_colors():
    """Test theme color configuration"""
    try:
        from dashboard.components.styling import get_theme_colors
        colors = get_theme_colors()
        required_colors = ['primary_bg', 'secondary_bg', 'text_primary', 'accent_blue']
        
        for color in required_colors:
            if color not in colors:
                print(f"❌ Missing color: {color}")
                return False
        
        print("✅ Theme colors configured correctly")
        return True
    except Exception as e:
        print(f"❌ Theme color error: {e}")
        return False

def test_framework_structure():
    """Test that the framework structure is correct"""
    required_files = [
        'app.py',
        'dashboard/components/styling.py',
        'dashboard/components/navigation.py',
        'dashboard/components/ui_components.py',
        'dashboard/pages/executive_overview.py',
        'dashboard/pages/market_expansion.py',
        'dashboard/pages/customer_analytics.py',
        'dashboard/pages/seasonal_intelligence.py',
        'dashboard/pages/payment_operations.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required framework files present")
    return True

if __name__ == "__main__":
    print("Testing Dashboard Framework...")
    print("=" * 40)
    
    tests = [
        test_framework_structure,
        test_imports,
        test_theme_colors
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Dashboard framework is ready!")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")