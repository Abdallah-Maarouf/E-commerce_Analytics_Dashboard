#!/usr/bin/env python3
"""
Test script for payment operations dashboard page
"""

import sys
sys.path.append('.')

def test_payment_operations():
    """Test the payment operations dashboard functionality"""
    try:
        from dashboard.pages.payment_operations import load_payment_operations_data
        
        print("Testing payment operations data loading...")
        data = load_payment_operations_data()
        
        if data:
            print("✅ Data loaded successfully!")
            print(f"Total orders: {data['total_orders']:,}")
            print(f"Total revenue: R$ {data['total_revenue']:,.2f}")
            print(f"Avg delivery days: {data['avg_delivery_days']:.1f}")
            print(f"On-time delivery rate: {data['on_time_delivery_rate']:.1f}%")
            print(f"Avg satisfaction: {data['avg_satisfaction']:.2f}")
            print(f"Avg installments: {data['avg_installments']:.1f}")
            
            # Test payment data structure
            payment_data = data['payment_data']
            print(f"\nPayment data shape: {payment_data.shape}")
            print(f"Payment types: {payment_data['payment_type'].value_counts().to_dict()}")
            print(f"States covered: {payment_data['customer_state'].nunique()