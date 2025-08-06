"""
Sample Data Generator for Deployment
Creates sample datasets when original data files are not available
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def create_sample_market_expansion_data():
    """Create sample market expansion data"""
    brazilian_states = [
        'SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE',
        'PA', 'DF', 'ES', 'PB', 'RN', 'MT', 'MS', 'PI', 'AL', 'MA',
        'TO', 'SE', 'RO', 'AC', 'AM', 'RR', 'AP'
    ]
    
    data = []
    for state in brazilian_states:
        # Generate realistic sample data
        customers = np.random.randint(100, 15000)
        revenue = customers * np.random.uniform(120, 400)
        sellers = np.random.randint(10, 500)
        
        data.append({
            'state': state,
            'state_customers': customers,
            'state_revenue': revenue,
            'state_sellers': sellers,
            'market_opportunity_score': np.random.uniform(0.2, 0.9),
            'avg_delivery_days': np.random.uniform(8, 25),
            'delivery_reliability': np.random.uniform(0.7, 0.95)
        })
    
    return pd.DataFrame(data)

def create_sample_customer_analytics_data():
    """Create sample customer analytics data"""
    n_customers = 10000
    
    # Customer segments
    segments = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'New Customers', 
               'Promising', 'Need Attention', 'About to Sleep', 'At Risk', 'Cannot Lose Them']
    
    clv_categories = ['VIP', 'High Value', 'Medium Value', 'Low Value']
    
    data = []
    for i in range(n_customers):
        # Generate sample customer data
        total_revenue = np.random.lognormal(5, 1)  # Log-normal distribution for revenue
        avg_order_value = total_revenue * np.random.uniform(0.8, 1.2)
        
        data.append({
            'customer_unique_id': f'customer_{i:06d}',
            'customer_segment': np.random.choice(segments),
            'clv_category': np.random.choice(clv_categories, p=[0.1, 0.4, 0.35, 0.15]),
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'recency_score': np.random.randint(1, 6),
            'frequency_score': np.random.randint(1, 6),
            'monetary_score': np.random.randint(1, 6),
            'avg_delivery_experience': np.random.uniform(5, 30),
            'delivery_reliability': np.random.uniform(0.6, 1.0),
            'last_order_date': (datetime.now() - timedelta(days=np.random.randint(1, 800))).strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(data)

def create_sample_seasonal_data():
    """Create sample seasonal intelligence data"""
    # Generate monthly data for 2 years
    dates = pd.date_range('2017-01-01', '2018-12-31', freq='M')
    
    data = []
    for date in dates:
        # Simulate seasonal patterns
        month = date.month
        seasonal_multiplier = 1.0
        
        # Higher sales in November (Black Friday) and December (Christmas)
        if month == 11:
            seasonal_multiplier = 1.5
        elif month == 12:
            seasonal_multiplier = 1.3
        elif month in [6, 7]:  # Winter sales in Brazil
            seasonal_multiplier = 1.2
        
        base_revenue = 800000
        revenue = base_revenue * seasonal_multiplier * np.random.uniform(0.8, 1.2)
        orders = int(revenue / 160)  # Avg order value ~160
        
        data.append({
            'month_year': date.strftime('%Y-%m'),
            'total_revenue': revenue,
            'total_orders': orders,
            'avg_order_value': revenue / orders,
            'seasonal_index': seasonal_multiplier,
            'growth_rate': np.random.uniform(-0.1, 0.3)
        })
    
    return pd.DataFrame(data)

def create_sample_payment_operations_data():
    """Create sample payment operations data"""
    n_orders = 15000
    
    payment_methods = ['credit_card', 'boleto', 'voucher', 'debit_card']
    payment_weights = [0.765, 0.199, 0.02, 0.015]
    
    brazilian_states = [
        'SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE',
        'PA', 'DF', 'ES', 'PB', 'RN', 'MT', 'MS', 'PI', 'AL', 'MA'
    ]
    
    data = []
    for i in range(n_orders):
        payment_method = np.random.choice(payment_methods, p=payment_weights)
        installments = 1 if payment_method != 'credit_card' else np.random.choice([1, 2, 3, 4, 5, 6], p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05])
        
        data.append({
            'order_id': f'order_{i:08d}',
            'payment_type': payment_method,
            'payment_installments': installments,
            'payment_value': np.random.lognormal(4.5, 0.8),
            'customer_state': np.random.choice(brazilian_states),
            'delivery_days': np.random.gamma(2, 6),  # Gamma distribution for delivery days
            'review_score': np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.05, 0.15, 0.25, 0.5]),
            'order_status': 'delivered'
        })
    
    return pd.DataFrame(data)

def generate_all_sample_data():
    """Generate all required sample datasets"""
    print("🔄 Generating sample data for deployment...")
    
    # Create directories
    os.makedirs('data/feature_engineered', exist_ok=True)
    
    # Generate and save datasets
    datasets = {
        'market_expansion.csv': create_sample_market_expansion_data(),
        'customer_analytics.csv': create_sample_customer_analytics_data(),
        'seasonal_intelligence_monthly_trends.csv': create_sample_seasonal_data(),
        'payment_operations.csv': create_sample_payment_operations_data()
    }
    
    for filename, df in datasets.items():
        filepath = f'data/feature_engineered/{filename}'
        df.to_csv(filepath, index=False)
        print(f"✅ Created {filepath} with {len(df):,} records")
    
    print("🎉 Sample data generation complete!")
    return True

if __name__ == "__main__":
    generate_all_sample_data()