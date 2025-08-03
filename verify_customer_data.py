#!/usr/bin/env python3
"""
Verify customer data and repeat purchase patterns
"""

import pandas as pd
import numpy as np

def verify_customer_data():
    """Verify the customer data and check for repeat purchases"""
    
    print("=== VERIFYING CUSTOMER DATA ===")
    
    # Load original cleaned orders data
    orders = pd.read_csv('data/cleaned/cleaned_orders.csv')
    print(f"Total orders in cleaned data: {len(orders):,}")
    print(f"Unique customers in orders: {orders['customer_id'].nunique():,}")
    
    # Check customer order frequency
    customer_order_counts = orders['customer_id'].value_counts()
    print(f"\nCustomer order frequency distribution:")
    frequency_dist = customer_order_counts.value_counts().sort_index()
    print(frequency_dist)
    
    # Check for repeat customers
    repeat_customers = customer_order_counts[customer_order_counts > 1]
    print(f"\nCustomers with multiple orders: {len(repeat_customers):,}")
    
    if len(repeat_customers) > 0:
        print("Top 10 customers by order count:")
        print(repeat_customers.head(10))
        
        print(f"\nRepeat customer rate: {len(repeat_customers) / len(customer_order_counts) * 100:.2f}%")
    else:
        print("No repeat customers found in the dataset")
    
    # Now check the feature engineered data
    print("\n=== CHECKING FEATURE ENGINEERED DATA ===")
    customer_analytics = pd.read_csv('data/feature_engineered/customer_analytics.csv')
    
    print(f"Customers in analytics data: {len(customer_analytics):,}")
    print(f"Unique customers: {customer_analytics['customer_id'].nunique():,}")
    
    # Check total_orders distribution
    print(f"\nTotal orders distribution in analytics data:")
    print(customer_analytics['total_orders'].value_counts().sort_index())
    
    # Check if there's a mismatch
    analytics_repeat = customer_analytics[customer_analytics['total_orders'] > 1]
    print(f"\nCustomers with multiple orders in analytics: {len(analytics_repeat):,}")
    
    if len(analytics_repeat) > 0:
        print("Sample customers with multiple orders:")
        print(analytics_repeat[['customer_id', 'total_orders', 'is_repeat_customer']].head())
    
    # Check the discrepancy
    if len(orders) != len(customer_analytics):
        print(f"\n⚠️  DISCREPANCY FOUND:")
        print(f"Orders data has {len(orders):,} records")
        print(f"Analytics data has {len(customer_analytics):,} records")
        print(f"Difference: {abs(len(orders) - len(customer_analytics)):,}")

if __name__ == "__main__":
    verify_customer_data()