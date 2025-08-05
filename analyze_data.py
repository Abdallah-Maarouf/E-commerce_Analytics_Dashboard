#!/usr/bin/env python3
"""
Data Analysis Script for Case Study
Analyzes the actual feature-engineered data to understand business insights
"""

import pandas as pd
import numpy as np

def main():
    print("=== BRAZILIAN E-COMMERCE DATA ANALYSIS ===\n")
    
    # Load key datasets
    try:
        market_data = pd.read_csv('data/feature_engineered/market_expansion.csv')
        customer_data = pd.read_csv('data/feature_engineered/customer_analytics.csv')
        seasonal_data = pd.read_csv('data/feature_engineered/seasonal_intelligence_monthly_trends.csv')
        payment_data = pd.read_csv('data/feature_engineered/payment_operations.csv')
        print("✅ All datasets loaded successfully\n")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # === KEY BUSINESS METRICS ===
    print("=== KEY BUSINESS METRICS ===")
    total_revenue = customer_data['total_revenue'].sum()
    total_customers = len(customer_data)
    avg_order_value = customer_data['avg_order_value'].mean()
    high_value_customers = len(customer_data[customer_data['clv_category'].isin(['VIP', 'High Value'])])
    high_value_rate = high_value_customers/total_customers*100
    avg_delivery_days = customer_data['avg_delivery_experience'].mean()
    delivery_reliability = customer_data['delivery_reliability'].mean()*100
    
    print(f"Total Revenue: R$ {total_revenue:,.2f}")
    print(f"Total Customers: {total_customers:,}")
    print(f"Average Order Value: R$ {avg_order_value:.2f}")
    print(f"High-Value Customers: {high_value_customers:,} ({high_value_rate:.1f}%)")
    print(f"Average Delivery Days: {avg_delivery_days:.1f}")
    print(f"Delivery Reliability: {delivery_reliability:.1f}%")
    print()
    
    # === MARKET EXPANSION INSIGHTS ===
    print("=== MARKET EXPANSION INSIGHTS ===")
    state_summary = market_data.groupby('state').agg({
        'customer_count': 'sum',
        'total_revenue': 'sum',
        'market_opportunity_score': 'mean'
    }).reset_index().sort_values('total_revenue', ascending=False)
    
    print("Top 10 States by Revenue:")
    for i, row in state_summary.head(10).iterrows():
        print(f"  {row['state']}: R$ {row['total_revenue']:,.0f} ({row['customer_count']:,} customers)")
    print()
    
    # === CUSTOMER SEGMENTS ===
    print("=== CUSTOMER SEGMENTS ===")
    segment_analysis = customer_data['customer_segment'].value_counts()
    for segment, count in segment_analysis.items():
        pct = count/len(customer_data)*100
        avg_revenue = customer_data[customer_data['customer_segment']==segment]['total_revenue'].mean()
        total_segment_revenue = customer_data[customer_data['customer_segment']==segment]['total_revenue'].sum()
        revenue_share = total_segment_revenue/total_revenue*100
        print(f"  {segment}: {count:,} customers ({pct:.1f}%) - Avg Revenue: R$ {avg_revenue:.2f} - Revenue Share: {revenue_share:.1f}%")
    print()
    
    # === SEASONAL PATTERNS ===
    print("=== SEASONAL PATTERNS ===")
    peak_revenue_idx = seasonal_data['monthly_revenue'].idxmax()
    peak_orders_idx = seasonal_data['monthly_orders'].idxmax()
    
    peak_revenue_month = seasonal_data.loc[peak_revenue_idx]
    peak_orders_month = seasonal_data.loc[peak_orders_idx]
    
    print(f"Peak Revenue Month: {peak_revenue_month['year']}-{peak_revenue_month['month']:02d} with R$ {peak_revenue_month['monthly_revenue']:,.0f}")
    print(f"Peak Orders Month: {peak_orders_month['year']}-{peak_orders_month['month']:02d} with {peak_orders_month['monthly_orders']:,} orders")
    
    # Calculate seasonal variance
    revenue_cv = seasonal_data['monthly_revenue'].std() / seasonal_data['monthly_revenue'].mean()
    print(f"Revenue Seasonality (CV): {revenue_cv:.3f}")
    print()
    
    # === PAYMENT BEHAVIOR ===
    print("=== PAYMENT BEHAVIOR ===")
    payment_methods = payment_data['payment_type'].value_counts()
    for method, count in payment_methods.items():
        pct = count/len(payment_data)*100
        print(f"  {method}: {count:,} transactions ({pct:.1f}%)")
    print()
    
    # === DELIVERY PERFORMANCE ===
    print("=== DELIVERY PERFORMANCE ===")
    delivery_stats = payment_data.groupby('delivery_speed_category')['delivery_days'].agg(['count', 'mean']).reset_index()
    delivery_stats['percentage'] = delivery_stats['count'] / delivery_stats['count'].sum() * 100
    
    print("Delivery Speed Distribution:")
    for _, row in delivery_stats.iterrows():
        if pd.notna(row['delivery_speed_category']):
            print(f"  {row['delivery_speed_category']}: {row['count']:,} orders ({row['percentage']:.1f}%) - Avg: {row['mean']:.1f} days")
    print()
    
    # === GEOGRAPHIC ANALYSIS ===
    print("=== GEOGRAPHIC ANALYSIS ===")
    states_with_data = market_data[market_data['customer_count'] > 0]['state'].nunique()
    total_states = market_data['state'].nunique()
    print(f"States with customers: {states_with_data} out of {total_states} total states")
    
    # Top expansion opportunities
    expansion_opps = state_summary[state_summary['market_opportunity_score'] > 0.4]
    print(f"High opportunity states (score > 0.4): {len(expansion_opps)}")
    if len(expansion_opps) > 0:
        print("Top expansion opportunities:")
        for _, row in expansion_opps.head(5).iterrows():
            print(f"  {row['state']}: Score {row['market_opportunity_score']:.3f} - {row['customer_count']:,} customers")
    print()
    
    print("=== ANALYSIS COMPLETE ===")

if __name__ == "__main__":
    main()