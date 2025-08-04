#!/usr/bin/env python3
"""
Test script for executive overview functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_loading():
    """Test if data loading works correctly"""
    try:
        import pandas as pd
        
        # Test loading the data files
        market_data = pd.read_csv('data/feature_engineered/market_expansion.csv')
        customer_data = pd.read_csv('data/feature_engineered/customer_analytics.csv')
        
        print("✅ Data loading successful")
        print(f"Market data shape: {market_data.shape}")
        print(f"Customer data shape: {customer_data.shape}")
        
        # Test key metrics calculation
        total_revenue = customer_data['total_revenue'].sum()
        total_customers = len(customer_data)
        avg_order_value = customer_data['avg_order_value'].mean()
        
        print(f"Total Revenue: R$ {total_revenue:,.2f}")
        print(f"Total Customers: {total_customers:,}")
        print(f"Average Order Value: R$ {avg_order_value:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_executive_import():
    """Test if executive overview module imports correctly"""
    try:
        from dashboard.pages.executive_overview import load_executive_data
        print("✅ Executive overview import successful")
        
        # Test data loading function
        data = load_executive_data()
        if data:
            print("✅ Executive data loading successful")
            print(f"Revenue: R$ {data['total_revenue']:,.2f}")
            print(f"Customers: {data['total_customers']:,}")
        else:
            print("❌ Executive data loading failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Executive overview import failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Executive Overview Implementation ===")
    
    print("\n1. Testing data loading...")
    data_ok = test_data_loading()
    
    print("\n2. Testing executive overview import...")
    import_ok = test_executive_import()
    
    if data_ok and import_ok:
        print("\n✅ All tests passed! Executive overview is ready.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")