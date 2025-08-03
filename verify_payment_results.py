"""
Verification script to check if payment analysis results are accurate
"""

import pandas as pd
import numpy as np

def verify_payment_analysis():
    """Verify the payment analysis results against actual data."""
    
    # Load the payment operations data
    payment_data = pd.read_csv('data/feature_engineered/payment_operations.csv')
    
    print('=== DATASET VERIFICATION ===')
    print(f'Total records: {len(payment_data):,}')
    print(f'Columns available: {list(payment_data.columns)}')
    
    # Check for missing customer state data
    print(f'\nRecords with customer_state: {payment_data["customer_state"].notna().sum():,}')
    print(f'Records missing customer_state: {payment_data["customer_state"].isna().sum():,}')
    
    # Check payment method distribution
    print('\n=== PAYMENT METHOD DISTRIBUTION ===')
    payment_dist = payment_data['payment_type'].value_counts(dropna=False)
    payment_pct = payment_data['payment_type'].value_counts(normalize=True, dropna=False) * 100
    
    for method, count in payment_dist.items():
        pct = payment_pct[method]
        print(f'{method}: {count:,} ({pct:.1f}%)')
    
    # Check satisfaction by payment method (only for records with reviews)
    print('\n=== SATISFACTION BY PAYMENT METHOD ===')
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
    
    # Check regional performance
    print('\n=== REGIONAL PERFORMANCE VERIFICATION ===')
    if 'customer_state' in payment_data.columns:
        regional_data = payment_data[payment_data['customer_state'].notna()]
        
        if len(regional_data) > 0:
            state_performance = regional_data.groupby('customer_state').agg({
                'on_time_delivery': lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0,
                'review_score': 'mean',
                'payment_value': 'mean',
                'order_id': 'count'
            }).round(2)
            
            # Sort by on-time delivery
            state_performance = state_performance.sort_values('on_time_delivery', ascending=False)
            
            print(f'States analyzed: {len(state_performance)}')
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
        else:
            print('No regional data available for analysis')
    
    # Check installment patterns
    print('\n=== INSTALLMENT ANALYSIS VERIFICATION ===')
    installment_data = payment_data[payment_data['payment_installments'].notna()]
    
    if len(installment_data) > 0:
        print(f'Records with installment data: {len(installment_data):,}')
        
        # Create installment categories
        installment_data = installment_data.copy()
        installment_data['installment_category'] = pd.cut(
            installment_data['payment_installments'],
            bins=[0, 1, 3, 6, 12, float('inf')],
            labels=['Single Payment', '2-3 Installments', '4-6 Installments', 
                   '7-12 Installments', '12+ Installments'],
            include_lowest=True
        )
        
        # Analyze satisfaction by installment category
        installment_satisfaction = installment_data[installment_data['review_score'].notna()]
        
        if len(installment_satisfaction) > 0:
            installment_analysis = installment_satisfaction.groupby('installment_category').agg({
                'review_score': ['mean', 'count'],
                'payment_value': 'mean'
            }).round(2)
            
            print('\nSatisfaction by installment category:')
            for category in installment_analysis.index:
                if pd.notna(category):
                    avg_sat = installment_analysis.loc[category, ('review_score', 'mean')]
                    count = installment_analysis.loc[category, ('review_score', 'count')]
                    avg_value = installment_analysis.loc[category, ('payment_value', 'mean')]
                    print(f'  {category}: {avg_sat:.2f}/5.0 satisfaction ({count:,} reviews), R$ {avg_value:.2f} avg')
    
    # Check overall operational metrics
    print('\n=== OPERATIONAL METRICS VERIFICATION ===')
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
    
    print('\n=== VERIFICATION COMPLETE ===')
    return True

if __name__ == "__main__":
    verify_payment_analysis()