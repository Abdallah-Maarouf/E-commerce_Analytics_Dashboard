import pandas as pd
import numpy as np

# Load datasets
dfs = {
    'orders': pd.read_csv('data/olist_orders_dataset.csv'),
    'customers': pd.read_csv('data/olist_customers_dataset.csv'), 
    'products': pd.read_csv('data/olist_products_dataset.csv'),
    'order_items': pd.read_csv('data/olist_order_items_dataset.csv'),
    'payments': pd.read_csv('data/olist_order_payments_dataset.csv'),
    'reviews': pd.read_csv('data/olist_order_reviews_dataset.csv'),
    'sellers': pd.read_csv('data/olist_sellers_dataset.csv'),
    'geolocation': pd.read_csv('data/olist_geolocation_dataset.csv'),
    'category_translation': pd.read_csv('data/product_category_name_translation.csv')
}

print("2. DATA QUALITY ASSESSMENT")
print("-" * 30)

for name, df in dfs.items():
    print(f"\n{name.upper()}:")
    print(f"  Missing values:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    for col in missing[missing > 0].index:
        print(f"    {col}: {missing[col]} ({missing_pct[col]:.1f}%)")
    
    if missing.sum() == 0:
        print("    No missing values!")
    
    duplicates = df.duplicated().sum()
    print(f"  Duplicates: {duplicates}")
    
    print(f"  Data types:")
    for col, dtype in df.dtypes.items():
        print(f"    {col}: {dtype}")

print("\n3. KEY RELATIONSHIPS")
print("-" * 30)

# Check relationships between datasets
print(f"Orders: {dfs['orders']['order_id'].nunique()} unique orders")
print(f"Customers: {dfs['customers']['customer_id'].nunique()} unique customers")
print(f"Products: {dfs['products']['product_id'].nunique()} unique products")
print(f"Sellers: {dfs['sellers']['seller_id'].nunique()} unique sellers")

# Check foreign key relationships
print(f"\nForeign key checks:")
orders_in_items = dfs['order_items']['order_id'].nunique()
orders_total = dfs['orders']['order_id'].nunique()
print(f"Orders in order_items vs orders table: {orders_in_items}/{orders_total}")

customers_in_orders = dfs['orders']['customer_id'].nunique()
customers_total = dfs['customers']['customer_id'].nunique()
print(f"Customers in orders vs customers table: {customers_in_orders}/{customers_total}")