"""
Fix the payment analysis by properly merging customer location data
"""

import pandas as pd
import numpy as np

def fix_payment_operations_data():
    """Fix the payment operations dataset by properly merging customer location data."""
    
    print("🔄 Fixing payment operations dataset with proper customer location data...")
    
    # Load the payment operations data
    payment_data = pd.read_csv('data/feature_engineered/payment_operations.csv')
    print(f"Original payment data: {len(payment_data):,} records")
    
    # Load customer data
    customer_data = pd.read_csv('data/cleaned/cleaned_customers.csv')
    print(f"Customer data: {len(customer_data):,} records")
    
    # Merge customer location data
    payment_with_location = payment_data.merge(
        customer_data[['customer_id', 'customer_state', 'customer_city']], 
        on='customer_id', 
        how='left'
    )
    
    print(f"After merge: {len(payment_with_location):,} records")
    print(f"Records with customer_state: {payment_with_location['customer_state'].notna().sum():,}")
    print(f"Records missing customer_state: {payment_with_location['customer_state'].isna().sum():,}")
    
    # Save the corrected dataset
    payment_with_location.to_csv('data/feature_engineered/payment_operations_corrected.csv', index=False)
    print("✅ Saved corrected dataset to: data/feature_engineered/payment_operations_corrected.csv")
    
    return payment_with_location

def verify_corrected_analysis():
    """Verify the analysis with corrected data."""
    
    print("\n🔍 Verifying analysis with corrected data...")
    
    # Load corrected data
    payment_data = pd.read_csv('data/feature_engineered/payment_operations_corrected.csv')
    
    # Payment method distribution
    print("\n=== PAYMENT METHOD DISTRIBUTION ===")
    payment_dist = payment_data['payment_type'].value_counts(dropna=False)
    payment_pct = payment_data['payment_type'].value_counts(normalize=True, dropna=False) * 100
    
    for method, count in payment_dist.items():
        pct = payment_pct[method]
        print(f'{method}: {count:,} ({pct:.1f}%)')
    
    # Satisfaction by payment method
    print("\n=== SATISFACTION BY PAYMENT METHOD ===")
    satisfaction_data = payment_data[payment_data['review_score'].notna()]
    print(f'Records with review scores: {len(satisfaction_data):,} out of {len(payment_data):,}')
    
    if len(satisfaction_data) > 0:
        payment_satisfaction = satisfaction_data.groupby('payment_type').agg({
            'review_score': ['mean', 'count'],
            'on_time_delivery': lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0
        }).round(2)
        
        print('\nSatisfaction by payment method:')
        for payment_type in payment_satisfaction.index:
            if pd.notna(payment_type):
                avg_sat = payment_satisfaction.loc[payment_type, ('review_score', 'mean')]
                count = payment_satisfaction.loc[payment_type, ('review_score', 'count')]
                on_time = payment_satisfaction.loc[payment_type, ('on_time_delivery', '<lambda>')]
                print(f'  {payment_type}: {avg_sat:.2f}/5.0 satisfaction ({count:,} reviews), {on_time:.1f}% on-time')
    
    # Regional analysis (now with proper location data)
    print("\n=== REGIONAL ANALYSIS ===")
    regional_data = payment_data[payment_data['customer_state'].notna()]
    
    if len(regional_data) > 0:
        print(f"Records with state data: {len(regional_data):,}")
        print(f"States covered: {regional_data['customer_state'].nunique()}")
        
        # State performance
        state_performance = regional_data.groupby('customer_state').agg({
            'on_time_delivery': lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0,
            'review_score': 'mean',
            'payment_value': 'mean',
            'order_id': 'count'
        }).round(2)
        
        # Sort by on-time delivery
        state_performance = state_performance.sort_values('on_time_delivery', ascending=False)
        
        print('\nTop 5 performing states (by on-time delivery):')
        for state in state_performance.head().index:
            on_time = state_performance.loc[state, 'on_time_delivery']
            avg_payment = state_performance.loc[state, 'payment_value']
            orders = state_performance.loc[state, 'order_id']
            print(f'  {state}: {on_time:.1f}% on-time, R$ {avg_payment:.2f} avg payment ({orders:,} orders)')
        
        print('\nBottom 5 performing states (by on-time delivery):')
        for state in state_performance.tail().index:
            on_time = state_performance.loc[state, 'on_time_delivery']
            avg_payment = state_performance.loc[state, 'payment_value']
            orders = state_performance.loc[state, 'order_id']
            print(f'  {state}: {on_time:.1f}% on-time, R$ {avg_payment:.2f} avg payment ({orders:,} orders)')
        
        # Payment method by state
        print('\n=== PAYMENT PREFERENCES BY STATE ===')
        state_payment = pd.crosstab(
            regional_data['customer_state'], 
            regional_data['payment_type'], 
            normalize='index'
        ) * 100
        
        print(f"Credit card usage by state (top 5):")
        if 'credit_card' in state_payment.columns:
            top_cc_states = state_payment['credit_card'].nlargest(5)
            for state, pct in top_cc_states.items():
                print(f'  {state}: {pct:.1f}%')
    
    # Overall metrics verification
    print("\n=== OVERALL METRICS ===")
    total_orders = len(payment_data)
    delivered_orders = len(payment_data[payment_data['order_status'] == 'delivered'])
    
    print(f'Total orders: {total_orders:,}')
    print(f'Delivered orders: {delivered_orders:,}')
    print(f'Delivery rate: {(delivered_orders/total_orders)*100:.1f}%')
    
    # Delivery performance
    delivery_data = payment_data[payment_data['delivery_days'].notna()]
    if len(delivery_data) > 0:
        avg_delivery = delivery_data['delivery_days'].mean()
        median_delivery = delivery_data['delivery_days'].median()
        print(f'Average delivery time: {avg_delivery:.1f} days')
        print(f'Median delivery time: {median_delivery:.1f} days')
    
    # On-time delivery
    on_time_data = payment_data[payment_data['on_time_delivery'].notna()]
    if len(on_time_data) > 0:
        on_time_rate = (on_time_data['on_time_delivery'].sum() / len(on_time_data)) * 100
        print(f'On-time delivery rate: {on_time_rate:.1f}%')
    
    print("\n✅ Verification complete!")

if __name__ == "__main__":
    # Fix the dataset
    corrected_data = fix_payment_operations_data()
    
    # Verify the analysis
    verify_corrected_analysis()