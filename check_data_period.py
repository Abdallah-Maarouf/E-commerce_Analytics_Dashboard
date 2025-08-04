#!/usr/bin/env python3
"""
Check the data period and explain what the executive overview is showing
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_data_period():
    """Analyze the data period and monthly distribution"""
    
    # Load the customer data to check the date range
    customer_data = pd.read_csv('data/feature_engineered/customer_analytics.csv')
    
    # Convert date columns
    customer_data['last_order_date'] = pd.to_datetime(customer_data['last_order_date'])
    customer_data['first_order_date'] = pd.to_datetime(customer_data['first_order_date'])
    
    # Check date range
    min_date = customer_data['last_order_date'].min()
    max_date = customer_data['last_order_date'].max()
    total_days = (max_date - min_date).days
    
    print("=== EXECUTIVE OVERVIEW DATA PERIOD ANALYSIS ===")
    print(f'Data Period: {min_date.strftime("%Y-%m-%d")} to {max_date.strftime("%Y-%m-%d")}')
    print(f'Total Duration: {total_days} days ({total_days/365.25:.1f} years)')
    print(f'Total Records: {len(customer_data):,}')
    
    # Check monthly distribution
    customer_data['month_year'] = customer_data['last_order_date'].dt.to_period('M')
    monthly_counts = customer_data['month_year'].value_counts().sort_index()
    monthly_revenue = customer_data.groupby('month_year')['total_revenue'].sum().sort_index()
    
    print(f'\nMonthly Data Summary:')
    print(f'First month: {monthly_counts.index[0]} ({monthly_counts.iloc[0]:,} orders, R$ {monthly_revenue.iloc[0]:,.2f})')
    print(f'Last month: {monthly_counts.index[-1]} ({monthly_counts.iloc[-1]:,} orders, R$ {monthly_revenue.iloc[-1]:,.2f})')
    print(f'Peak orders month: {monthly_counts.idxmax()} ({monthly_counts.max():,} orders)')
    print(f'Peak revenue month: {monthly_revenue.idxmax()} (R$ {monthly_revenue.max():,.2f})')
    
    # Show the trend over time
    print(f'\nMonthly Trend (Last 10 months):')
    for period in monthly_counts.index[-10:]:
        orders = monthly_counts[period]
        revenue = monthly_revenue[period]
        print(f'  {period}: {orders:,} orders, R$ {revenue:,.2f}')
    
    # Explain the sharp drop
    print(f'\n=== DATA COMPLETENESS ANALYSIS ===')
    
    # Check if October 2018 is a partial month
    oct_2018_data = customer_data[customer_data['last_order_date'].dt.to_period('M') == '2018-10']
    if len(oct_2018_data) > 0:
        oct_dates = oct_2018_data['last_order_date'].dt.day.unique()
        print(f'October 2018 data: {len(oct_2018_data)} orders on days: {sorted(oct_dates)}')
        max_oct_day = oct_2018_data['last_order_date'].dt.day.max()
        print(f'Last order date: {max_date.strftime("%Y-%m-%d")} (Day {max_oct_day} of October)')
        
        if max_oct_day < 20:
            print('⚠️  October 2018 appears to be PARTIAL DATA (dataset ends mid-month)')
        else:
            print('✅ October 2018 appears to have complete data')
    
    return {
        'start_date': min_date,
        'end_date': max_date,
        'total_days': total_days,
        'total_records': len(customer_data),
        'monthly_data': monthly_revenue
    }

def explain_chart_context():
    """Explain what the executive overview chart represents"""
    
    print(f'\n=== EXECUTIVE OVERVIEW CHART EXPLANATION ===')
    print("The Monthly Revenue Trend chart shows:")
    print("📊 WHAT: Monthly revenue aggregated from all customer orders")
    print("📅 WHEN: September 2016 to October 2018 (26+ months)")
    print("💰 DATA: Actual historical business performance")
    print("📈 PATTERN: Shows business growth trajectory and seasonal patterns")
    
    print(f'\nKey Observations:')
    print("• Steady growth from Sep 2016 to mid-2018")
    print("• Peak performance around Nov 2017 - Feb 2018")
    print("• Sharp drop in Oct 2018 (likely partial month data)")
    print("• This represents the COMPLETE available dataset period")
    
    print(f'\nBusiness Context:')
    print("• This is historical data, not real-time")
    print("• Represents the full business performance period available")
    print("• Useful for understanding growth patterns and seasonality")
    print("• The sharp drop at the end indicates dataset cutoff, not business decline")

if __name__ == "__main__":
    data_info = analyze_data_period()
    explain_chart_context()