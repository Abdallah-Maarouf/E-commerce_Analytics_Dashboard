import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("=== BRAZILIAN E-COMMERCE DATASET EXPLORATION ===")

# Load all datasets
datasets = {
    'orders': 'data/olist_orders_dataset.csv',
    'customers': 'data/olist_customers_dataset.csv', 
    'products': 'data/olist_products_dataset.csv',
    'order_items': 'data/olist_order_items_dataset.csv',
    'payments': 'data/olist_order_payments_dataset.csv',
    'reviews': 'data/olist_order_reviews_dataset.csv',
    'sellers': 'data/olist_sellers_dataset.csv',
    'geolocation': 'data/olist_geolocation_dataset.csv',
    'category_translation': 'data/product_category_name_translation.csv'
}

# Load all dataframes
dfs = {}
for name, path in datasets.items():
    try:
        dfs[name] = pd.read_csv(path)
        print(f"✓ Loaded {name}: {dfs[name].shape}")
    except Exception as e:
        print(f"✗ Error loading {name}: {e}")

print("\n" + "="*60)

# 1. DATASET OVERVIEW
print("\n1. DATASET OVERVIEW")
print("-" * 30)

for name, df in dfs.items():
    print(f"\n{name.upper()}:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")