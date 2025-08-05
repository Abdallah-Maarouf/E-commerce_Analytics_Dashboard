#!/usr/bin/env python3
"""
Test script for seasonal intelligence dashboard page
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_seasonal_imports():
    """Test if all required imports work"""
    try:
        # Test dashboard imports
        from dashboard.pages.seasonal_intelligence import render
        from dashboard.components.ui_components import create_metric_card
        from dashboard.components.styling import get_theme_colors
        
        print("✅ Dashboard imports successful")
        
        # Test seasonal analysis import
        from seasonal_analysis import SeasonalAnalysis
        print("✅ Seasonal analysis import successful")
        
        # Test data science imports
        import pandas as pd
        import numpy as np
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Data science imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_seasonal_analysis():
    """Test seasonal analysis functionality"""
    try:
        from seasonal_analysis impor