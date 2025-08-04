#!/usr/bin/env python3
"""
Test script for the geographic visualization fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_geographic_visualization():
    """Test the updated geographic visualization"""
    try:
        from dashboard.pages.executive_overview import load_executive_data, create_geographic_revenue_map
        
        print("Loading data...")
        data = load_executive_data()
        
        if not data:
            print("❌ Failed to load data")
            return False
        
        print("Creating geographic visualization...")
        fig = create_geographic_revenue_map(data['market_data'])
        
        if fig:
            print("✅ Geographic visualization created successfully")
            print(f"Chart type: {type(fig).__name__}")
            
            # Check if it has data
            if hasattr(fig, 'data') and len(fig.data) > 0:
                print(f"Number of data traces: {len(fig.data)}")
                print("✅ Chart contains data")
                return True
            else:
                print("❌ Chart has no data")
                return False
        else:
            print("❌ Failed to create visualization")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_data_structure():
    """Test the market data structure"""
    try:
        import pandas as pd
        
        market_data = pd.read_csv('data/feature_engineered/market_expansion.csv')
        
        print(f"Market data shape: {market_data.shape}")
        print(f"Unique states: {market_data['state'].nunique()}")
        print(f"States with revenue data: {market_data[market_data['state_revenue'] > 0]['state'].nunique()}")
        
        # Show top states by revenue
        state_revenue = market_data.groupby('state')['state_revenue'].first().sort_values(ascending=False).head(10)
        print("\nTop 10 states by revenue:")
        for state, revenue in state_revenue.items():
            print(f"  {state}: R$ {revenue:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Geographic Visualization Fix ===")
    
    print("\n1. Testing data structure...")
    data_ok = test_data_structure()
    
    print("\n2. Testing geographic visualization...")
    viz_ok = test_geographic_visualization()
    
    if data_ok and viz_ok:
        print("\n✅ All tests passed! Geographic visualization is fixed.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")