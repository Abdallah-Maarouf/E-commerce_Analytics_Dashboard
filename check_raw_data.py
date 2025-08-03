#!/usr/bin/env python3
"""
Check raw data for repeat customers
"""

import pandas as pd

def check_raw_data():
    """Check the raw original data for repeat customers"""
    
    print("=== CHECKING RAW ORIGINAL DATA ===")
    
    # Load raw orders data
    orders = pd.read_csv('data/olist_orders_dataset.csv')
    print(f"Total orders in raw data: {len(orders):,}")
    print(f"Unique customers in raw data: {orders['customer_id'].nunique():,}")
    
    # Check customer order frequency
    customer_order_counts = orders['customer_id'].value_counts()
    print(f"\nCustomer order frequency distribution:")
    frequency_dist = customer_order_counts.value_counts().sort_index()
    print(frequency_dist.head(10))
    
    # Check for repeat customers
    repeat_customers = customer_order_counts[customer_order_counts > 1]
    print(f"\nCustomers with multiple orders: {len(repeat_customers):,}")
    
    if len(repeat_customers) > 0:
        print("Top 10 customers by order count:")
        for customer_id, order_count in repeat_customers.head(10).items():
            print(f"Customer {customer_id}: {order_count} orders")
        
        print(f"\nRepeat customer rate: {len(repeat_customers) / len(customer_order_counts) * 100:.2f}%")
        
        # Show some sample orders from repeat customers
        sample_customer = repeat_customers.index[0]
        sample_orders = orders[orders['customer_id'] == sample_customer]
        print(f"\nSample orders from customer {sample_customer}:")
        print(sample_orders[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp']])
    else:
        print("No repeat customers found in the raw dataset")
        print("This confirms that every customer made exactly one order")

if __name__ == "__main__":
    check_raw_data()