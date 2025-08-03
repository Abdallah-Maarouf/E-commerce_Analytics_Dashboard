"""
Initial Business Analysis of Brazilian E-commerce Dataset

This script provides initial business insights and characteristics
of the dataset to understand the business context.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import load_brazilian_ecommerce_data
import warnings
warnings.filterwarnings('ignore')

def analyze_business_characteristics(datasets):
    """
    Analyze key business characteristics of the e-commerce dataset.
    
    Args:
        datasets (dict): Dictionary of loaded DataFrames
    """
    print("=" * 80)
    print("BRAZILIAN E-COMMERCE DATASET - BUSINESS CHARACTERISTICS")
    print("=" * 80)
    
    # Basic business metrics
    if 'orders' in datasets and 'order_items' in datasets:
        orders_df = datasets['orders']
        items_df = datasets['order_items']
        
        print("\n📈 BUSINESS SCALE:")
        print(f"   • Total orders: {len(orders_df):,}")
        print(f"   • Total order items: {len(items_df):,}")
        print(f"   • Average items per order: {len(items_df) / len(orders_df):.2f}")
        
        # Time period analysis
        if 'order_purchase_timestamp' in orders_df.columns:
            orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
            min_date = orders_df['order_purchase_timestamp'].min()
            max_date = orders_df['order_purchase_timestamp'].max()
            
            print(f"\n📅 TIME PERIOD:")
            print(f"   • Data period: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            print(f"   • Duration: {(max_date - min_date).days} days")
            
            # Monthly order distribution
            orders_df['year_month'] = orders_df['order_purchase_timestamp'].dt.to_period('M')
            monthly_orders = orders_df['year_month'].value_counts().sort_index()
            print(f"   • Average orders per month: {monthly_orders.mean():.0f}")
            print(f"   • Peak month: {monthly_orders.idxmax()} ({monthly_orders.max():,} orders)")
    
    # Geographic analysis
    if 'customers' in datasets:
        customers_df = datasets['customers']
        
        print(f"\n🌎 GEOGRAPHIC COVERAGE:")
        print(f"   • Total customers: {len(customers_df):,}")
        print(f"   • States covered: {customers_df['customer_state'].nunique()}")
        print(f"   • Cities covered: {customers_df['customer_city'].nunique():,}")
        
        # Top states by customers
        top_states = customers_df['customer_state'].value_counts().head(5)
        print(f"   • Top 5 states by customers:")
        for state, count in top_states.items():
            percentage = (count / len(customers_df)) * 100
            print(f"     - {state}: {count:,} ({percentage:.1f}%)")
    
    # Product analysis
    if 'products' in datasets:
        products_df = datasets['products']
        
        print(f"\n🛍️ PRODUCT CATALOG:")
        print(f"   • Total products: {len(products_df):,}")
        print(f"   • Product categories: {products_df['product_category_name'].nunique()}")
        
        # Top categories
        if 'order_items' in datasets:
            # Merge to get sales data
            items_with_products = datasets['order_items'].merge(
                products_df[['product_id', 'product_category_name']], 
                on='product_id', 
                how='left'
            )
            
            top_categories = items_with_products['product_category_name'].value_counts().head(5)
            print(f"   • Top 5 categories by sales volume:")
            for category, count in top_categories.items():
                if pd.notna(category):
                    print(f"     - {category}: {count:,} items sold")
    
    # Revenue analysis
    if 'order_items' in datasets:
        items_df = datasets['order_items']
        
        print(f"\n💰 REVENUE INSIGHTS:")
        total_revenue = items_df['price'].sum()
        print(f"   • Total revenue: R$ {total_revenue:,.2f}")
        print(f"   • Average item price: R$ {items_df['price'].mean():.2f}")
        print(f"   • Price range: R$ {items_df['price'].min():.2f} - R$ {items_df['price'].max():.2f}")
        
        # Freight analysis
        total_freight = items_df['freight_value'].sum()
        print(f"   • Total freight: R$ {total_freight:,.2f}")
        print(f"   • Freight as % of revenue: {(total_freight / total_revenue) * 100:.1f}%")
    
    # Payment analysis
    if 'order_payments' in datasets:
        payments_df = datasets['order_payments']
        
        print(f"\n💳 PAYMENT BEHAVIOR:")
        payment_methods = payments_df['payment_type'].value_counts()
        print(f"   • Payment methods used: {len(payment_methods)}")
        print(f"   • Most popular payment methods:")
        for method, count in payment_methods.head(3).items():
            percentage = (count / len(payments_df)) * 100
            print(f"     - {method}: {count:,} ({percentage:.1f}%)")
        
        # Installment analysis
        avg_installments = payments_df['payment_installments'].mean()
        max_installments = payments_df['payment_installments'].max()
        print(f"   • Average installments: {avg_installments:.1f}")
        print(f"   • Maximum installments: {max_installments}")
    
    # Review analysis
    if 'order_reviews' in datasets:
        reviews_df = datasets['order_reviews']
        
        print(f"\n⭐ CUSTOMER SATISFACTION:")
        print(f"   • Total reviews: {len(reviews_df):,}")
        avg_score = reviews_df['review_score'].mean()
        print(f"   • Average review score: {avg_score:.2f}/5")
        
        score_distribution = reviews_df['review_score'].value_counts().sort_index()
        print(f"   • Score distribution:")
        for score, count in score_distribution.items():
            percentage = (count / len(reviews_df)) * 100
            print(f"     - {score} stars: {count:,} ({percentage:.1f}%)")
    
    # Seller analysis
    if 'sellers' in datasets:
        sellers_df = datasets['sellers']
        
        print(f"\n🏪 SELLER ECOSYSTEM:")
        print(f"   • Total sellers: {len(sellers_df):,}")
        print(f"   • Seller states: {sellers_df['seller_state'].nunique()}")
        
        top_seller_states = sellers_df['seller_state'].value_counts().head(3)
        print(f"   • Top seller states:")
        for state, count in top_seller_states.items():
            percentage = (count / len(sellers_df)) * 100
            print(f"     - {state}: {count:,} ({percentage:.1f}%)")


def identify_business_opportunities(datasets):
    """
    Identify potential business opportunities based on initial analysis.
    
    Args:
        datasets (dict): Dictionary of loaded DataFrames
    """
    print(f"\n🎯 BUSINESS OPPORTUNITIES IDENTIFIED:")
    
    opportunities = []
    
    # Geographic expansion opportunities
    if 'customers' in datasets:
        customers_df = datasets['customers']
        state_distribution = customers_df['customer_state'].value_counts()
        
        # States with low customer count might be expansion opportunities
        low_customer_states = state_distribution[state_distribution < state_distribution.quantile(0.25)]
        if len(low_customer_states) > 0:
            opportunities.append(f"Geographic expansion: {len(low_customer_states)} states have below-average customer presence")
    
    # Product category opportunities
    if 'products' in datasets and 'order_items' in datasets:
        items_with_products = datasets['order_items'].merge(
            datasets['products'][['product_id', 'product_category_name']], 
            on='product_id', 
            how='left'
        )
        
        category_revenue = items_with_products.groupby('product_category_name')['price'].sum().sort_values(ascending=False)
        if len(category_revenue) > 10:
            opportunities.append(f"Product diversification: Focus on top {min(5, len(category_revenue))} categories that generate most revenue")
    
    # Customer satisfaction opportunities
    if 'order_reviews' in datasets:
        reviews_df = datasets['order_reviews']
        low_scores = reviews_df[reviews_df['review_score'] <= 3]
        if len(low_scores) > 0:
            low_score_percentage = (len(low_scores) / len(reviews_df)) * 100
            opportunities.append(f"Customer satisfaction: {low_score_percentage:.1f}% of reviews are 3 stars or below")
    
    # Payment optimization opportunities
    if 'order_payments' in datasets:
        payments_df = datasets['order_payments']
        high_installments = payments_df[payments_df['payment_installments'] > 6]
        if len(high_installments) > 0:
            high_installment_percentage = (len(high_installments) / len(payments_df)) * 100
            opportunities.append(f"Payment optimization: {high_installment_percentage:.1f}% of payments use >6 installments")
    
    # Display opportunities
    for i, opportunity in enumerate(opportunities, 1):
        print(f"   {i}. {opportunity}")
    
    if not opportunities:
        print("   • Further analysis needed to identify specific opportunities")


def main():
    """Main function to run business analysis."""
    print("Loading datasets for business analysis...")
    
    # Load datasets
    datasets, summary = load_brazilian_ecommerce_data()
    
    if not datasets:
        print("❌ No datasets loaded. Please check data directory and files.")
        return
    
    # Run business analysis
    analyze_business_characteristics(datasets)
    identify_business_opportunities(datasets)
    
    print(f"\n✅ Business analysis complete!")
    print(f"📋 Key findings documented for next phase: data cleaning and feature engineering")


if __name__ == "__main__":
    main()