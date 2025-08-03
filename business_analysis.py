import pandas as pd
import numpy as np

# Load key datasets
orders_df = pd.read_csv('data/olist_orders_dataset.csv')
customers_df = pd.read_csv('data/olist_customers_dataset.csv')
products_df = pd.read_csv('data/olist_products_dataset.csv')
order_items_df = pd.read_csv('data/olist_order_items_dataset.csv')
payments_df = pd.read_csv('data/olist_order_payments_dataset.csv')
reviews_df = pd.read_csv('data/olist_order_reviews_dataset.csv')
translation_df = pd.read_csv('data/product_category_name_translation.csv')

print("4. TEMPORAL ANALYSIS")
print("-" * 30)

# Convert date columns
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])

print(f"Date range: {orders_df['order_purchase_timestamp'].min()} to {orders_df['order_purchase_timestamp'].max()}")
print(f"Total time span: {(orders_df['order_purchase_timestamp'].max() - orders_df['order_purchase_timestamp'].min()).days} days")

print(f"\nOrder status distribution:")
status_counts = orders_df['order_status'].value_counts()
for status, count in status_counts.items():
    pct = (count / len(orders_df)) * 100
    print(f"  {status}: {count} ({pct:.1f}%)")

print("\n5. GEOGRAPHIC ANALYSIS")
print("-" * 30)

print(f"Customer states (top 10):")
state_counts = customers_df['customer_state'].value_counts().head(10)
for state, count in state_counts.items():
    pct = (count / len(customers_df)) * 100
    print(f"  {state}: {count} ({pct:.1f}%)")

print("\n6. PRODUCT ANALYSIS")
print("-" * 30)

print(f"Product categories (top 10):")
category_counts = products_df['product_category_name'].value_counts().head(10)
for category, count in category_counts.items():
    if pd.notna(category):
        # Get English translation
        english_name = translation_df[translation_df['product_category_name'] == category]['product_category_name_english'].values
        english_name = english_name[0] if len(english_name) > 0 else category
        pct = (count / len(products_df)) * 100
        print(f"  {english_name}: {count} ({pct:.1f}%)")

print("\n7. FINANCIAL ANALYSIS")
print("-" * 30)

print(f"Order items financial summary:")
print(f"  Price range: R${order_items_df['price'].min():.2f} - R${order_items_df['price'].max():.2f}")
print(f"  Average price: R${order_items_df['price'].mean():.2f}")
print(f"  Total revenue: R${order_items_df['price'].sum():,.2f}")

print(f"\nPayment methods:")
payment_counts = payments_df['payment_type'].value_counts()
for method, count in payment_counts.items():
    pct = (count / len(payments_df)) * 100
    print(f"  {method}: {count} ({pct:.1f}%)")

print("\n8. REVIEW ANALYSIS")
print("-" * 30)

print(f"Review scores distribution:")
score_counts = reviews_df['review_score'].value_counts().sort_index()
for score, count in score_counts.items():
    pct = (count / len(reviews_df)) * 100
    print(f"  {score} stars: {count} ({pct:.1f}%)")

print(f"\nAverage review score: {reviews_df['review_score'].mean():.2f}")

print("\n9. DATA CLEANING REQUIREMENTS")
print("-" * 30)

print("Issues to address:")
print("• Orders: Missing delivery dates (1.8% carrier, 3.0% customer)")
print("• Products: Missing category info for 610 products (1.9%)")
print("• Reviews: High missing values in comments (88% titles, 59% messages)")
print("• Geolocation: 261k duplicate records need deduplication")
print("• Date columns need proper datetime conversion")
print("• Foreign key mismatches: 775 orders in items table not in orders table")

print("\n10. BUSINESS QUESTIONS WE CAN ANSWER")
print("-" * 30)

print("Customer Analytics:")
print("• Customer segmentation by purchase behavior")
print("• Customer lifetime value analysis")
print("• Geographic distribution and regional preferences")

print("\nSales & Revenue:")
print("• Monthly/seasonal sales trends")
print("• Product category performance")
print("• Revenue forecasting")

print("\nOperational:")
print("• Delivery performance analysis")
print("• Payment method preferences")
print("• Review sentiment and satisfaction")

print("\nMarketing:")
print("• Customer acquisition patterns")
print("• Product recommendation opportunities")
print("• Regional market penetration")