#!/usr/bin/env python3
"""
Validation script for the Streamlit dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_dashboard_structure():
    """Validate that all dashboard components exist"""
    required_files = [
        'app.py',
        'dashboard/__init__.py',
        'dashboard/components/__init__.py',
        'dashboard/components/styling.py',
        'dashboard/components/navigation.py',
        'dashboard/components/ui_components.py',
        'dashboard/pages/__init__.py',
        'dashboard/pages/executive_overview.py',
        'dashboard/pages/market_expansion.py',
        'dashboard/pages/customer_analytics.py',
        'dashboard/pages/seasonal_intelligence.py',
        'dashboard/pages/payment_operations.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ All required dashboard files exist")
        return True

def validate_data_files():
    """Validate that all required data files exist"""
    required_data = [
        'data/feature_engineered/market_expansion.csv',
        'data/feature_engineered/customer_analytics.csv'
    ]
    
    missing_data = []
    for file in required_data:
        if not os.path.exists(file):
            missing_data.append(file)
    
    if missing_data:
        print("❌ Missing data files:")
        for file in missing_data:
            print(f"  - {file}")
        return False
    else:
        print("✅ All required data files exist")
        return True

def validate_imports():
    """Validate that all imports work correctly"""
    try:
        # Test main app imports
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test dashboard component imports
        from dashboard.components.styling import apply_dark_theme, get_theme_colors
        from dashboard.components.navigation import setup_sidebar_navigation
        from dashboard.components.ui_components import create_metric_card
        print("✅ Dashboard components import successful")
        
        # Test page imports
        from dashboard.pages import executive_overview
        print("✅ Executive overview page import successful")
        
        # Test data processing imports
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Data processing libraries import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import validation failed: {e}")
        return False

def validate_executive_functionality():
    """Validate executive overview functionality"""
    try:
        from dashboard.pages.executive_overview import load_executive_data
        
        # Test data loading
        data = load_executive_data()
        if not data:
            print("❌ Executive data loading failed")
            return False
        
        # Validate key metrics
        required_keys = [
            'total_revenue', 'total_customers', 'avg_order_value', 
            'high_value_rate', 'avg_delivery_days', 'delivery_reliability',
            'total_states', 'expansion_opportunities'
        ]
        
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            print(f"❌ Missing data keys: {missing_keys}")
            return False
        
        print("✅ Executive overview functionality validated")
        print(f"  - Revenue: R$ {data['total_revenue']:,.2f}")
        print(f"  - Customers: {data['total_customers']:,}")
        print(f"  - High-value rate: {data['high_value_rate']:.1f}%")
        print(f"  - States covered: {data['total_states']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Executive functionality validation failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Dashboard Validation ===")
    
    print("\n1. Validating dashboard structure...")
    structure_ok = validate_dashboard_structure()
    
    print("\n2. Validating data files...")
    data_ok = validate_data_files()
    
    print("\n3. Validating imports...")
    imports_ok = validate_imports()
    
    print("\n4. Validating executive overview functionality...")
    exec_ok = validate_executive_functionality()
    
    print("\n=== Validation Summary ===")
    if all([structure_ok, data_ok, imports_ok, exec_ok]):
        print("✅ All validations passed! Dashboard is ready for deployment.")
        print("\nTo run the dashboard:")
        print("  streamlit run app.py")
    else:
        print("❌ Some validations failed. Please fix the issues above.")