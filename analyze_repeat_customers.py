#!/usr/bin/env python3
"""
Quick analysis script to understand repeat customer patterns
"""

import pandas as pd
import numpy as np

def analyze_repeat_customers():
    """Analyze repeat customer patterns in the feature engineered data"""
    
    # Load the customer analytics data
    df = pd.read_csv('data/feature_engineered/customer_analytics.csv')
    
    print("=== CUSTOMER ANALYTICS DATA ANALYSIS ===")
    print(f"Total customers: {len(df):,}")
    print()
    
    # Analyze total orders distribution
    print("=== TOTAL ORDERS DISTRIBUTION ===")
    orders_dist = df['total_orders'].value_counts().sort_index()
    print(orders_dist.head(10))
    print()
    
    # Analyze repeat customers
    print("=== REPEAT CUSTOMER ANALYSIS ===")
    repeat_customers = df['is_repeat_customer'].value_counts()
    print("Repeat customer distribution:")
    print(repeat_customers)
    print(f"Repeat customer rate: {repeat_customers.get(True, 0) / len(df) * 100:.2f}%")
    print()
    
    # Check customers with multiple orders
    multi_order_customers = df[df['total_orders'] > 1]
    print(f"Customers with multiple orders: {len(multi_order_customers):,}")
    
    if len(multi_order_customers) > 0:
        print("Sample of multi-order customers:")
        print(multi_order_customers[['customer_id', 'total_orders', 'is_repeat_customer', 'customer_segment']].head())
        print()
        
        # Check if there's a mismatch in the repeat customer flag
        mismatch = multi_order_customers[multi_order_customers['is_repeat_customer'] == False]
        if len(mismatch) > 0:
            print(f"⚠️  ISSUE FOUND: {len(mismatch)} customers have multiple orders but is_repeat_customer=False")
    
    # Let's also check the raw cleaned data to verify
    print("\n=== CHECKING RAW CLEANED DATA ===")
    try:
        orders_df = pd.read_csv('data/cleaned/cleaned_orders.csv')
        customer_order_counts = orders_df['customer_id'].value_counts()
        
        print(f"Total unique customers in orders: {len(customer_order_counts):,}")
        print("Order count distribution from raw data:")
        print(customer_order_counts.value_counts().sort_index().head(10))
        
        repeat_customers_raw = (customer_order_counts > 1).sum()
        repeat_rate_raw = repeat_customers_raw / len(customer_order_counts) * 100
        print(f"Repeat customers from raw data: {repeat_customers_raw:,} ({repeat_rate_raw:.2f}%)")
        
    except Exception as e:
        print(f"Error reading raw data: {e}")

if __name__ == "__main__":
    analyze_repeat_customers()