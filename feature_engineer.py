"""
Feature Engineering Module for Brazilian E-commerce Dataset

This module creates derived features and master analytical datasets
for business analysis across all 5 key business question areas.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import warnings
from save_cleaned_data import load_cleaned_datasets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Comprehensive feature engineering for Brazilian E-commerce analytics.
    Creates derived features and master datasets for business analysis.
    """
    
    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        """
        Initialize the FeatureEngineer with cleaned datasets.
        
        Args:
            datasets (Dict[str, pd.DataFrame]): Dictionary of cleaned DataFrames
        """
        self.datasets = datasets.copy()
        self.feature_log = []
        self.master_datasets = {}
        self.feature_dictionary = {}
        
    def log_feature_action(self, action: str, dataset: str, details: str):
        """Log feature engineering actions for audit trail."""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'dataset': dataset,
            'details': details
        }
        self.feature_log.append(log_entry)
        logger.info(f"{action} - {dataset}: {details}")
    
    def create_delivery_performance_features(self) -> pd.DataFrame:
        """
        Create comprehensive delivery performance metrics.
        
        Returns:
            pd.DataFrame: Enhanced orders dataset with delivery features
        """
        logger.info("Creating delivery performance features...")
        
        if 'orders' not in self.datasets:
            logger.error("Orders dataset not found")
            return pd.DataFrame()
        
        orders_df = self.datasets['orders'].copy()
        
        # Basic delivery metrics (some may already exist from cleaning)
        delivered_mask = (orders_df['order_delivered_customer_date'].notna() & 
                         orders_df['order_purchase_timestamp'].notna())
        
        if delivered_mask.sum() > 0:
            # Delivery days (if not already calculated)
            if 'delivery_days' not in orders_df.columns:
                orders_df.loc[delivered_mask, 'delivery_days'] = (
                    orders_df.loc[delivered_mask, 'order_delivered_customer_date'] - 
                    orders_df.loc[delivered_mask, 'order_purchase_timestamp']
                ).dt.days
            
            # Advanced delivery performance metrics
            # Delivery speed categories
            orders_df.loc[delivered_mask, 'delivery_speed_category'] = pd.cut(
                orders_df.loc[delivered_mask, 'delivery_days'],
                bins=[-np.inf, 7, 14, 21, 30, np.inf],
                labels=['Very Fast (≤7d)', 'Fast (8-14d)', 'Normal (15-21d)', 'Slow (22-30d)', 'Very Slow (>30d)']
            )
            
            # Delivery performance vs estimate
            estimate_mask = delivered_mask & orders_df['order_estimated_delivery_date'].notna()
            if estimate_mask.sum() > 0:
                if 'delivery_vs_estimate_days' not in orders_df.columns:
                    orders_df.loc[estimate_mask, 'delivery_vs_estimate_days'] = (
                        orders_df.loc[estimate_mask, 'order_delivered_customer_date'] - 
                        orders_df.loc[estimate_mask, 'order_estimated_delivery_date']
                    ).dt.days
                
                if 'on_time_delivery' not in orders_df.columns:
                    orders_df.loc[estimate_mask, 'on_time_delivery'] = \
                        orders_df.loc[estimate_mask, 'delivery_vs_estimate_days'] <= 0
                
                # Delivery accuracy categories
                orders_df.loc[estimate_mask, 'delivery_accuracy'] = pd.cut(
                    orders_df.loc[estimate_mask, 'delivery_vs_estimate_days'],
                    bins=[-np.inf, -7, 0, 7, 14, np.inf],
                    labels=['Much Earlier', 'Earlier', 'On Time', 'Late', 'Very Late']
                )
            
            # Processing time (purchase to carrier)
            carrier_mask = (orders_df['order_delivered_carrier_date'].notna() & 
                           orders_df['order_purchase_timestamp'].notna())
            if carrier_mask.sum() > 0:
                orders_df.loc[carrier_mask, 'processing_days'] = (
                    orders_df.loc[carrier_mask, 'order_delivered_carrier_date'] - 
                    orders_df.loc[carrier_mask, 'order_purchase_timestamp']
                ).dt.days
            
            # Shipping time (carrier to customer)
            shipping_mask = (orders_df['order_delivered_customer_date'].notna() & 
                            orders_df['order_delivered_carrier_date'].notna())
            if shipping_mask.sum() > 0:
                orders_df.loc[shipping_mask, 'shipping_days'] = (
                    orders_df.loc[shipping_mask, 'order_delivered_customer_date'] - 
                    orders_df.loc[shipping_mask, 'order_delivered_carrier_date']
                ).dt.days
        
        # Temporal features for seasonality analysis
        orders_df['order_year'] = orders_df['order_purchase_timestamp'].dt.year
        orders_df['order_month'] = orders_df['order_purchase_timestamp'].dt.month
        orders_df['order_quarter'] = orders_df['order_purchase_timestamp'].dt.quarter
        orders_df['order_day_of_week'] = orders_df['order_purchase_timestamp'].dt.dayofweek
        orders_df['order_day_name'] = orders_df['order_purchase_timestamp'].dt.day_name()
        orders_df['order_hour'] = orders_df['order_purchase_timestamp'].dt.hour
        orders_df['order_week_of_year'] = orders_df['order_purchase_timestamp'].dt.isocalendar().week
        
        # Brazilian holiday and seasonal indicators
        orders_df['is_weekend'] = orders_df['order_day_of_week'].isin([5, 6])
        orders_df['is_holiday_season'] = orders_df['order_month'].isin([11, 12])  # Black Friday, Christmas
        orders_df['is_carnival_season'] = orders_df['order_month'].isin([2, 3])   # Carnival period
        orders_df['is_mothers_day_season'] = orders_df['order_month'] == 5        # Mother's Day (May)
        orders_df['is_valentines_season'] = orders_df['order_month'] == 6         # Valentine's Day (June in Brazil)
        
        self.log_feature_action(
            'CREATE_DELIVERY_FEATURES',
            'orders',
            f"Created delivery performance and temporal features for {len(orders_df)} orders"
        )
        
        # Update feature dictionary
        self.feature_dictionary.update({
            'delivery_days': 'Number of days from purchase to delivery',
            'delivery_speed_category': 'Categorical delivery speed classification',
            'delivery_vs_estimate_days': 'Days difference between actual and estimated delivery',
            'on_time_delivery': 'Boolean flag for on-time delivery performance',
            'delivery_accuracy': 'Categorical delivery accuracy vs estimate',
            'processing_days': 'Days from purchase to carrier pickup',
            'shipping_days': 'Days from carrier pickup to customer delivery',
            'order_quarter': 'Quarter of the year when order was placed',
            'order_day_name': 'Day of the week name when order was placed',
            'order_week_of_year': 'Week number of the year when order was placed',
            'is_weekend': 'Boolean flag for weekend orders',
            'is_holiday_season': 'Boolean flag for holiday season orders (Nov-Dec)',
            'is_carnival_season': 'Boolean flag for carnival season orders (Feb-Mar)',
            'is_mothers_day_season': 'Boolean flag for Mother\'s Day season orders (May)',
            'is_valentines_season': 'Boolean flag for Valentine\'s Day season orders (June)'
        })
        
        return orders_df
    
    def create_customer_behavior_features(self) -> pd.DataFrame:
        """
        Create customer behavior features including RFM analysis components.
        
        Returns:
            pd.DataFrame: Customer metrics dataset with behavior features
        """
        logger.info("Creating customer behavior features...")
        
        if 'orders' not in self.datasets or 'order_items' not in self.datasets:
            logger.error("Required datasets (orders, order_items) not found")
            return pd.DataFrame()
        
        orders_df = self.datasets['orders'].copy()
        items_df = self.datasets['order_items'].copy()
        
        # Get order values by joining with order items
        order_values = items_df.groupby('order_id').agg({
            'price': 'sum',
            'freight_value': 'sum'
        }).reset_index()
        order_values['total_order_value'] = order_values['price'] + order_values['freight_value']
        
        # Merge with orders to get customer information
        orders_with_values = orders_df.merge(order_values, on='order_id', how='left')
        
        # Calculate customer metrics for RFM analysis
        analysis_date = orders_df['order_purchase_timestamp'].max()
        
        customer_metrics = orders_with_values.groupby('customer_id').agg({
            'order_id': 'count',  # Frequency
            'total_order_value': ['sum', 'mean'],  # Monetary
            'order_purchase_timestamp': ['max', 'min']  # Recency calculation
        }).reset_index()
        
        # Flatten column names
        customer_metrics.columns = [
            'customer_id', 'total_orders', 'total_revenue', 'avg_order_value',
            'last_order_date', 'first_order_date'
        ]
        
        # Calculate recency (days since last order)
        customer_metrics['days_since_last_order'] = (
            analysis_date - customer_metrics['last_order_date']
        ).dt.days
        
        # Calculate customer lifetime (days between first and last order)
        customer_metrics['customer_lifetime_days'] = (
            customer_metrics['last_order_date'] - customer_metrics['first_order_date']
        ).dt.days
        
        # Calculate order frequency (orders per month for active customers)
        customer_metrics['order_frequency_per_month'] = np.where(
            customer_metrics['customer_lifetime_days'] > 0,
            customer_metrics['total_orders'] / (customer_metrics['customer_lifetime_days'] / 30.44),
            customer_metrics['total_orders']  # For single-order customers
        )
        
        # RFM Score Components (1-5 scale, 5 being best)
        customer_metrics['recency_score'] = pd.qcut(
            customer_metrics['days_since_last_order'], 
            q=5, labels=[5, 4, 3, 2, 1]  # Lower days = higher score
        ).astype(int)
        
        customer_metrics['frequency_score'] = pd.qcut(
            customer_metrics['total_orders'].rank(method='first'), 
            q=5, labels=[1, 2, 3, 4, 5]
        ).astype(int)
        
        customer_metrics['monetary_score'] = pd.qcut(
            customer_metrics['total_revenue'].rank(method='first'), 
            q=5, labels=[1, 2, 3, 4, 5]
        ).astype(int)
        
        # Combined RFM Score
        customer_metrics['rfm_score'] = (
            customer_metrics['recency_score'] * 100 + 
            customer_metrics['frequency_score'] * 10 + 
            customer_metrics['monetary_score']
        )
        
        # Customer Segmentation based on RFM
        def categorize_customer(row):
            r, f, m = row['recency_score'], row['frequency_score'], row['monetary_score']
            
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            elif r >= 3 and f >= 3 and m >= 3:
                return 'Loyal Customers'
            elif r >= 4 and f <= 2:
                return 'New Customers'
            elif r >= 3 and f >= 3 and m <= 2:
                return 'Potential Loyalists'
            elif r <= 2 and f >= 3 and m >= 3:
                return 'At Risk'
            elif r <= 2 and f <= 2 and m >= 3:
                return 'Cannot Lose Them'
            elif r >= 3 and f <= 2 and m <= 2:
                return 'Promising'
            elif r <= 2 and f <= 2 and m <= 2:
                return 'Lost'
            else:
                return 'Others'
        
        customer_metrics['customer_segment'] = customer_metrics.apply(categorize_customer, axis=1)
        
        # Customer Lifetime Value (CLV) estimation
        # Simple CLV = Average Order Value × Purchase Frequency × Customer Lifetime
        customer_metrics['estimated_clv'] = (
            customer_metrics['avg_order_value'] * 
            customer_metrics['order_frequency_per_month'] * 
            np.maximum(customer_metrics['customer_lifetime_days'] / 30.44, 1)  # Convert to months
        )
        
        # Customer value categories
        customer_metrics['clv_category'] = pd.qcut(
            customer_metrics['estimated_clv'].rank(method='first'),
            q=4, labels=['Low Value', 'Medium Value', 'High Value', 'VIP']
        )
        
        # Customer activity status
        customer_metrics['customer_status'] = np.where(
            customer_metrics['days_since_last_order'] <= 90, 'Active',
            np.where(customer_metrics['days_since_last_order'] <= 180, 'Inactive', 'Churned')
        )
        
        # Repeat customer flag
        customer_metrics['is_repeat_customer'] = customer_metrics['total_orders'] > 1
        
        self.log_feature_action(
            'CREATE_CUSTOMER_FEATURES',
            'customer_metrics',
            f"Created customer behavior features for {len(customer_metrics)} customers"
        )
        
        # Update feature dictionary
        self.feature_dictionary.update({
            'total_orders': 'Total number of orders placed by customer',
            'total_revenue': 'Total monetary value of all customer orders',
            'avg_order_value': 'Average monetary value per order',
            'days_since_last_order': 'Number of days since customer\'s last order (Recency)',
            'customer_lifetime_days': 'Number of days between first and last order',
            'order_frequency_per_month': 'Average number of orders per month',
            'recency_score': 'RFM Recency score (1-5, 5 being most recent)',
            'frequency_score': 'RFM Frequency score (1-5, 5 being most frequent)',
            'monetary_score': 'RFM Monetary score (1-5, 5 being highest value)',
            'rfm_score': 'Combined RFM score (111-555)',
            'customer_segment': 'Customer segment based on RFM analysis',
            'estimated_clv': 'Estimated Customer Lifetime Value',
            'clv_category': 'Customer value category (Low/Medium/High/VIP)',
            'customer_status': 'Customer activity status (Active/Inactive/Churned)',
            'is_repeat_customer': 'Boolean flag for customers with multiple orders'
        })
        
        return customer_metrics
    
    def create_product_performance_features(self) -> pd.DataFrame:
        """
        Create product performance metrics including sales volume and review scores.
        
        Returns:
            pd.DataFrame: Product metrics dataset with performance features
        """
        logger.info("Creating product performance features...")
        
        if ('products' not in self.datasets or 'order_items' not in self.datasets or 
            'order_reviews' not in self.datasets):
            logger.error("Required datasets (products, order_items, order_reviews) not found")
            return pd.DataFrame()
        
        products_df = self.datasets['products'].copy()
        items_df = self.datasets['order_items'].copy()
        reviews_df = self.datasets['order_reviews'].copy()
        
        # Product sales metrics
        product_sales = items_df.groupby('product_id').agg({
            'order_id': 'nunique',  # Number of unique orders
            'product_id': 'count',  # Total quantity sold
            'price': ['sum', 'mean', 'std'],
            'freight_value': ['sum', 'mean']
        }).reset_index()
        
        # Flatten column names
        product_sales.columns = [
            'product_id', 'unique_orders', 'total_quantity_sold', 
            'total_revenue', 'avg_price', 'price_std',
            'total_freight', 'avg_freight'
        ]
        
        # Calculate additional sales metrics
        product_sales['revenue_per_order'] = product_sales['total_revenue'] / product_sales['unique_orders']
        product_sales['avg_quantity_per_order'] = product_sales['total_quantity_sold'] / product_sales['unique_orders']
        
        # Price variability indicator
        product_sales['price_coefficient_variation'] = (
            product_sales['price_std'] / product_sales['avg_price']
        ).fillna(0)
        
        # Product review metrics
        # First, get order_id to product_id mapping
        order_product_map = items_df[['order_id', 'product_id']].drop_duplicates()
        
        # Merge reviews with product information
        product_reviews = reviews_df.merge(order_product_map, on='order_id', how='left')
        
        # Calculate review metrics by product
        review_metrics = product_reviews.groupby('product_id').agg({
            'review_score': ['count', 'mean', 'std'],
            'review_comment_message': lambda x: x.notna().sum()  # Count of reviews with comments
        }).reset_index()
        
        # Flatten column names
        review_metrics.columns = [
            'product_id', 'total_reviews', 'avg_review_score', 'review_score_std',
            'reviews_with_comments'
        ]
        
        # Calculate review engagement rate
        review_metrics['review_comment_rate'] = (
            review_metrics['reviews_with_comments'] / review_metrics['total_reviews']
        ).fillna(0)
        
        # Review score categories
        review_metrics['review_category'] = pd.cut(
            review_metrics['avg_review_score'],
            bins=[0, 2, 3, 4, 5],
            labels=['Poor (1-2)', 'Fair (2-3)', 'Good (3-4)', 'Excellent (4-5)']
        )
        
        # Merge all product metrics
        product_metrics = products_df.merge(product_sales, on='product_id', how='left')
        product_metrics = product_metrics.merge(review_metrics, on='product_id', how='left')
        
        # Fill missing values for products without sales/reviews
        numeric_cols = [
            'unique_orders', 'total_quantity_sold', 'total_revenue', 'avg_price',
            'total_freight', 'avg_freight', 'revenue_per_order', 'avg_quantity_per_order',
            'total_reviews', 'avg_review_score', 'reviews_with_comments', 'review_comment_rate'
        ]
        product_metrics[numeric_cols] = product_metrics[numeric_cols].fillna(0)
        
        # Product performance categories
        # Sales performance
        product_metrics['sales_performance'] = pd.qcut(
            product_metrics['total_quantity_sold'].rank(method='first'),
            q=4, labels=['Low Sales', 'Medium Sales', 'High Sales', 'Top Seller']
        )
        
        # Revenue performance
        product_metrics['revenue_performance'] = pd.qcut(
            product_metrics['total_revenue'].rank(method='first'),
            q=4, labels=['Low Revenue', 'Medium Revenue', 'High Revenue', 'Top Revenue']
        )
        
        # Product popularity score (combination of sales and reviews)
        # Normalize metrics to 0-1 scale for combination
        max_sales = product_metrics['total_quantity_sold'].max()
        max_reviews = product_metrics['total_reviews'].max()
        
        if max_sales > 0 and max_reviews > 0:
            product_metrics['popularity_score'] = (
                (product_metrics['total_quantity_sold'] / max_sales) * 0.6 +
                (product_metrics['total_reviews'] / max_reviews) * 0.2 +
                (product_metrics['avg_review_score'] / 5) * 0.2
            )
        else:
            product_metrics['popularity_score'] = 0
        
        # Product lifecycle stage
        def categorize_product_lifecycle(row):
            if row['total_quantity_sold'] == 0:
                return 'No Sales'
            elif row['unique_orders'] <= 5:
                return 'Introduction'
            elif row['popularity_score'] >= 0.7:
                return 'Growth'
            elif row['popularity_score'] >= 0.3:
                return 'Maturity'
            else:
                return 'Decline'
        
        product_metrics['product_lifecycle'] = product_metrics.apply(categorize_product_lifecycle, axis=1)
        
        # Category performance metrics
        category_metrics = product_metrics.groupby('product_category_name_english').agg({
            'total_quantity_sold': 'sum',
            'total_revenue': 'sum',
            'avg_review_score': 'mean',
            'product_id': 'count'
        }).reset_index()
        
        category_metrics.columns = [
            'product_category_name_english', 'category_total_sales', 'category_total_revenue',
            'category_avg_review', 'category_product_count'
        ]
        
        # Merge category metrics back to product metrics
        product_metrics = product_metrics.merge(category_metrics, on='product_category_name_english', how='left')
        
        # Product's share within category
        product_metrics['category_sales_share'] = (
            product_metrics['total_quantity_sold'] / product_metrics['category_total_sales']
        ).fillna(0)
        
        product_metrics['category_revenue_share'] = (
            product_metrics['total_revenue'] / product_metrics['category_total_revenue']
        ).fillna(0)
        
        self.log_feature_action(
            'CREATE_PRODUCT_FEATURES',
            'product_metrics',
            f"Created product performance features for {len(product_metrics)} products"
        )
        
        # Update feature dictionary
        self.feature_dictionary.update({
            'unique_orders': 'Number of unique orders containing this product',
            'total_quantity_sold': 'Total quantity of product sold',
            'total_revenue': 'Total revenue generated by product',
            'avg_price': 'Average selling price of product',
            'revenue_per_order': 'Average revenue per order containing this product',
            'avg_quantity_per_order': 'Average quantity sold per order',
            'price_coefficient_variation': 'Price variability indicator (std/mean)',
            'total_reviews': 'Total number of reviews for product',
            'avg_review_score': 'Average review score (1-5)',
            'review_comment_rate': 'Percentage of reviews with written comments',
            'review_category': 'Review quality category',
            'sales_performance': 'Sales performance quartile',
            'revenue_performance': 'Revenue performance quartile',
            'popularity_score': 'Combined popularity score (0-1)',
            'product_lifecycle': 'Product lifecycle stage',
            'category_sales_share': 'Product\'s share of category sales',
            'category_revenue_share': 'Product\'s share of category revenue'
        })
        
        return product_metrics
    
    def create_geographic_features(self) -> pd.DataFrame:
        """
        Create geographic features for market expansion analysis.
        
        Returns:
            pd.DataFrame: Geographic metrics dataset
        """
        logger.info("Creating geographic features...")
        
        if ('customers' not in self.datasets or 'sellers' not in self.datasets or 
            'orders' not in self.datasets or 'order_items' not in self.datasets):
            logger.error("Required datasets for geographic analysis not found")
            return pd.DataFrame()
        
        customers_df = self.datasets['customers'].copy()
        sellers_df = self.datasets['sellers'].copy()
        orders_df = self.datasets['orders'].copy()
        items_df = self.datasets['order_items'].copy()
        
        # Customer geographic metrics
        customer_geo = customers_df.groupby(['customer_state', 'customer_city']).agg({
            'customer_id': 'count'
        }).reset_index()
        customer_geo.columns = ['state', 'city', 'customer_count']
        customer_geo['location_type'] = 'customer'
        
        # Seller geographic metrics
        seller_geo = sellers_df.groupby(['seller_state', 'seller_city']).agg({
            'seller_id': 'count'
        }).reset_index()
        seller_geo.columns = ['state', 'city', 'seller_count']
        seller_geo['location_type'] = 'seller'
        
        # Order volume by customer location
        orders_with_customers = orders_df.merge(customers_df, on='customer_id', how='left')
        order_geo = orders_with_customers.groupby(['customer_state', 'customer_city']).agg({
            'order_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        order_geo.columns = ['state', 'city', 'total_orders', 'unique_customers']
        order_geo['orders_per_customer'] = order_geo['total_orders'] / order_geo['unique_customers']
        
        # Revenue by geographic location
        # Get order values
        order_values = items_df.groupby('order_id').agg({
            'price': 'sum',
            'freight_value': 'sum'
        }).reset_index()
        order_values['total_order_value'] = order_values['price'] + order_values['freight_value']
        
        # Merge with geographic information
        orders_with_geo = orders_with_customers.merge(order_values, on='order_id', how='left')
        
        revenue_geo = orders_with_geo.groupby(['customer_state', 'customer_city']).agg({
            'total_order_value': ['sum', 'mean'],
            'order_id': 'count'
        }).reset_index()
        
        revenue_geo.columns = ['state', 'city', 'total_revenue', 'avg_order_value', 'order_count']
        
        # Combine all geographic metrics
        geo_metrics = customer_geo.merge(
            seller_geo[['state', 'city', 'seller_count']], 
            on=['state', 'city'], how='outer'
        )
        geo_metrics = geo_metrics.merge(
            order_geo[['state', 'city', 'total_orders', 'orders_per_customer']], 
            on=['state', 'city'], how='outer'
        )
        geo_metrics = geo_metrics.merge(
            revenue_geo[['state', 'city', 'total_revenue', 'avg_order_value']], 
            on=['state', 'city'], how='outer'
        )
        
        # Fill missing values
        numeric_cols = ['customer_count', 'seller_count', 'total_orders', 'orders_per_customer', 
                       'total_revenue', 'avg_order_value']
        geo_metrics[numeric_cols] = geo_metrics[numeric_cols].fillna(0)
        
        # Calculate market metrics
        geo_metrics['customer_to_seller_ratio'] = np.where(
            geo_metrics['seller_count'] > 0,
            geo_metrics['customer_count'] / geo_metrics['seller_count'],
            geo_metrics['customer_count']
        )
        
        # Market penetration indicators
        geo_metrics['revenue_per_customer'] = np.where(
            geo_metrics['customer_count'] > 0,
            geo_metrics['total_revenue'] / geo_metrics['customer_count'],
            0
        )
        
        # State-level aggregations for expansion analysis
        state_metrics = geo_metrics.groupby('state').agg({
            'customer_count': 'sum',
            'seller_count': 'sum',
            'total_orders': 'sum',
            'total_revenue': 'sum',
            'city': 'count'  # Number of cities per state
        }).reset_index()
        
        state_metrics.columns = [
            'state', 'state_customers', 'state_sellers', 'state_orders', 
            'state_revenue', 'cities_count'
        ]
        
        # Calculate state-level metrics
        state_metrics['state_revenue_per_customer'] = (
            state_metrics['state_revenue'] / state_metrics['state_customers']
        ).fillna(0)
        
        state_metrics['state_orders_per_customer'] = (
            state_metrics['state_orders'] / state_metrics['state_customers']
        ).fillna(0)
        
        state_metrics['state_customer_to_seller_ratio'] = np.where(
            state_metrics['state_sellers'] > 0,
            state_metrics['state_customers'] / state_metrics['state_sellers'],
            state_metrics['state_customers']
        )
        
        # Market opportunity score (higher = better expansion opportunity)
        # Normalize metrics for scoring
        max_customers = state_metrics['state_customers'].max()
        max_revenue_per_customer = state_metrics['state_revenue_per_customer'].max()
        
        if max_customers > 0 and max_revenue_per_customer > 0:
            # Opportunity = High revenue per customer potential + Low current penetration
            state_metrics['market_opportunity_score'] = (
                (1 - state_metrics['state_customers'] / max_customers) * 0.6 +  # Low penetration = opportunity
                (state_metrics['state_revenue_per_customer'] / max_revenue_per_customer) * 0.4  # High value potential
            )
        else:
            state_metrics['market_opportunity_score'] = 0
        
        # Merge state metrics back to city-level data
        geo_metrics = geo_metrics.merge(state_metrics, on='state', how='left')
        
        self.log_feature_action(
            'CREATE_GEOGRAPHIC_FEATURES',
            'geographic_metrics',
            f"Created geographic features for {len(geo_metrics)} locations"
        )
        
        # Update feature dictionary
        self.feature_dictionary.update({
            'customer_count': 'Number of customers in location',
            'seller_count': 'Number of sellers in location',
            'total_orders': 'Total orders from location',
            'orders_per_customer': 'Average orders per customer in location',
            'total_revenue': 'Total revenue from location',
            'avg_order_value': 'Average order value in location',
            'customer_to_seller_ratio': 'Ratio of customers to sellers',
            'revenue_per_customer': 'Average revenue per customer',
            'market_opportunity_score': 'Market expansion opportunity score (0-1)',
            'state_customers': 'Total customers in state',
            'state_revenue_per_customer': 'Average revenue per customer in state'
        })
        
        return geo_metrics 
   
    def create_seasonal_features(self, enhanced_orders: pd.DataFrame = None) -> pd.DataFrame:
        """
        Create seasonal and temporal features for demand analysis.
        
        Returns:
            pd.DataFrame: Seasonal metrics dataset
        """
        logger.info("Creating seasonal features...")
        
        if ('orders' not in self.datasets or 'order_items' not in self.datasets or 
            'products' not in self.datasets):
            logger.error("Required datasets for seasonal analysis not found")
            return pd.DataFrame()
        
        orders_df = enhanced_orders.copy() if enhanced_orders is not None else self.datasets['orders'].copy()
        items_df = self.datasets['order_items'].copy()
        products_df = self.datasets['products'].copy()
        
        # Get order values and merge with temporal data
        order_values = items_df.groupby('order_id').agg({
            'price': 'sum',
            'freight_value': 'sum',
            'product_id': 'count'
        }).reset_index()
        order_values['total_order_value'] = order_values['price'] + order_values['freight_value']
        order_values.columns = ['order_id', 'order_price', 'order_freight', 'items_count', 'total_order_value']
        
        # Merge orders with values and product information
        orders_with_values = orders_df.merge(order_values, on='order_id', how='left')
        
        # Get product category information for seasonal analysis
        items_with_products = items_df.merge(products_df[['product_id', 'product_category_name_english']], 
                                           on='product_id', how='left')
        
        # Monthly seasonal metrics by category
        orders_monthly = orders_with_values.groupby(['order_year', 'order_month']).agg({
            'order_id': 'count',
            'total_order_value': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        
        orders_monthly.columns = ['year', 'month', 'monthly_orders', 'monthly_revenue', 'monthly_customers']
        orders_monthly['year_month'] = orders_monthly['year'].astype(str) + '-' + orders_monthly['month'].astype(str).str.zfill(2)
        
        # Category seasonal patterns
        category_seasonal = items_with_products.merge(orders_df[['order_id', 'order_month', 'order_year']], 
                                                    on='order_id', how='left')
        
        category_monthly = category_seasonal.groupby(['product_category_name_english', 'order_year', 'order_month']).agg({
            'order_id': 'nunique',
            'price': 'sum',
            'product_id': 'count'
        }).reset_index()
        
        category_monthly.columns = ['category', 'year', 'month', 'category_orders', 'category_revenue', 'category_items']
        
        # Calculate seasonal variance for each category
        category_variance = category_monthly.groupby('category').agg({
            'category_revenue': ['mean', 'std']
        }).reset_index()
        
        category_variance.columns = ['category', 'avg_monthly_revenue', 'revenue_std']
        category_variance['seasonal_variance'] = (
            category_variance['revenue_std'] / category_variance['avg_monthly_revenue']
        ).fillna(0)
        
        # Holiday impact analysis - merge with enhanced orders to get holiday flags
        orders_enhanced = orders_df.copy()  # This should have the holiday flags from delivery features
        orders_with_holidays = orders_enhanced.merge(order_values, on='order_id', how='left')
        
        holiday_impact = orders_with_holidays.groupby(['is_holiday_season', 'order_month']).agg({
            'total_order_value': 'mean',
            'order_id': 'count'
        }).reset_index()
        
        # Brazilian cultural events impact
        cultural_events = orders_with_values.groupby(['order_month']).agg({
            'total_order_value': ['sum', 'mean', 'count'],
            'customer_id': 'nunique'
        }).reset_index()
        
        cultural_events.columns = ['month', 'monthly_total_revenue', 'avg_order_value', 'order_count', 'unique_customers']
        
        # Add cultural event indicators
        cultural_events['event_type'] = cultural_events['month'].map({
            2: 'Carnival', 3: 'Carnival', 5: 'Mothers Day', 6: 'Valentines Day',
            11: 'Black Friday', 12: 'Christmas'
        }).fillna('Regular')
        
        self.log_feature_action(
            'CREATE_SEASONAL_FEATURES',
            'seasonal_metrics',
            f"Created seasonal features for {len(orders_monthly)} months and {len(category_variance)} categories"
        )
        
        # Update feature dictionary
        self.feature_dictionary.update({
            'monthly_orders': 'Number of orders per month',
            'monthly_revenue': 'Total revenue per month',
            'monthly_customers': 'Unique customers per month',
            'seasonal_variance': 'Revenue variability coefficient for category',
            'category_orders': 'Orders per category per month',
            'category_revenue': 'Revenue per category per month',
            'event_type': 'Brazilian cultural event type for month'
        })
        
        # Store seasonal datasets
        self.seasonal_data = {
            'monthly_metrics': orders_monthly,
            'category_seasonal': category_monthly,
            'category_variance': category_variance,
            'cultural_events': cultural_events
        }
        
        return orders_monthly
    
    def create_master_analytical_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Create master analytical datasets for each business question area.
        
        Returns:
            Dict[str, pd.DataFrame]: Master datasets for business analysis
        """
        logger.info("Creating master analytical datasets...")
        
        # Create all feature sets
        enhanced_orders = self.create_delivery_performance_features()
        customer_metrics = self.create_customer_behavior_features()
        product_metrics = self.create_product_performance_features()
        geographic_metrics = self.create_geographic_features()
        seasonal_metrics = self.create_seasonal_features(enhanced_orders)
        
        # Master Dataset 1: Market Expansion Analysis
        market_expansion_data = geographic_metrics.copy()
        
        # Add delivery performance by location
        if not enhanced_orders.empty and not customer_metrics.empty:
            # Get customer location delivery performance
            customers_df = self.datasets['customers'].copy()
            delivery_by_location = enhanced_orders.merge(customers_df, on='customer_id', how='left')
            
            location_delivery = delivery_by_location.groupby(['customer_state', 'customer_city']).agg({
                'delivery_days': 'mean',
                'on_time_delivery': 'mean',
                'delivery_speed_category': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
            }).reset_index()
            
            location_delivery.columns = ['state', 'city', 'avg_delivery_days', 'on_time_rate', 'typical_delivery_speed']
            
            market_expansion_data = market_expansion_data.merge(
                location_delivery, on=['state', 'city'], how='left'
            )
        
        # Master Dataset 2: Customer Analytics
        customer_analytics_data = customer_metrics.copy()
        
        # Add delivery experience impact
        if not enhanced_orders.empty:
            customer_delivery = enhanced_orders.groupby('customer_id').agg({
                'delivery_days': 'mean',
                'on_time_delivery': 'mean',
                'order_id': 'count'
            }).reset_index()
            
            customer_delivery.columns = ['customer_id', 'avg_delivery_experience', 'delivery_reliability', 'total_orders_check']
            
            customer_analytics_data = customer_analytics_data.merge(
                customer_delivery, on='customer_id', how='left'
            )
        
        # Master Dataset 3: Seasonal Intelligence
        seasonal_intelligence_data = seasonal_metrics.copy()
        
        # Add product category seasonal patterns
        if hasattr(self, 'seasonal_data'):
            seasonal_intelligence_data = {
                'monthly_trends': self.seasonal_data['monthly_metrics'],
                'category_patterns': self.seasonal_data['category_seasonal'],
                'seasonal_variance': self.seasonal_data['category_variance'],
                'cultural_events': self.seasonal_data['cultural_events']
            }
        
        # Master Dataset 4: Payment & Operations Analysis
        if 'order_payments' in self.datasets:
            payments_df = self.datasets['order_payments'].copy()
            
            # Payment behavior by customer
            payment_behavior = payments_df.groupby('order_id').agg({
                'payment_type': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown',
                'payment_installments': 'max',
                'payment_value': 'sum'
            }).reset_index()
            
            # Merge with orders and customer data
            payment_operations_data = enhanced_orders.merge(payment_behavior, on='order_id', how='left')
            
            if 'order_reviews' in self.datasets:
                reviews_df = self.datasets['order_reviews'].copy()
                payment_operations_data = payment_operations_data.merge(
                    reviews_df[['order_id', 'review_score']], on='order_id', how='left'
                )
        else:
            payment_operations_data = enhanced_orders.copy()
        
        # Master Dataset 5: Product Performance Analysis
        product_performance_data = product_metrics.copy()
        
        # Store master datasets
        self.master_datasets = {
            'market_expansion': market_expansion_data,
            'customer_analytics': customer_analytics_data,
            'seasonal_intelligence': seasonal_intelligence_data,
            'payment_operations': payment_operations_data,
            'product_performance': product_performance_data
        }
        
        self.log_feature_action(
            'CREATE_MASTER_DATASETS',
            'all_datasets',
            f"Created {len(self.master_datasets)} master analytical datasets"
        )
        
        return self.master_datasets
    
    def save_feature_dictionary(self, output_path: str = 'reports/feature_dictionary.txt'):
        """
        Save the feature dictionary documentation.
        
        Args:
            output_path (str): Path to save the feature dictionary
        """
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("# Feature Dictionary\n")
            f.write("# Generated on: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            
            for feature, description in self.feature_dictionary.items():
                f.write(f"{feature}: {description}\n")
        
        logger.info(f"Feature dictionary saved to {output_path}")
    
    def save_master_datasets(self, output_dir: str = 'data/feature_engineered'):
        """
        Save master analytical datasets to CSV files for use in subsequent analysis.
        
        Args:
            output_dir (str): Directory to save the feature-engineered datasets
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Saving master analytical datasets to {output_dir}/...")
        
        saved_files = []
        
        for dataset_name, dataset in self.master_datasets.items():
            if isinstance(dataset, dict):
                # Handle nested datasets (like seasonal_intelligence)
                for sub_name, sub_dataset in dataset.items():
                    if isinstance(sub_dataset, pd.DataFrame) and not sub_dataset.empty:
                        filename = f"{dataset_name}_{sub_name}.csv"
                        filepath = os.path.join(output_dir, filename)
                        sub_dataset.to_csv(filepath, index=False)
                        saved_files.append(filename)
                        logger.info(f"Saved {filename} with {len(sub_dataset)} records")
            elif isinstance(dataset, pd.DataFrame) and not dataset.empty:
                filename = f"{dataset_name}.csv"
                filepath = os.path.join(output_dir, filename)
                dataset.to_csv(filepath, index=False)
                saved_files.append(filename)
                logger.info(f"Saved {filename} with {len(dataset)} records")
        
        # Save dataset inventory
        inventory_path = os.path.join(output_dir, 'dataset_inventory.txt')
        with open(inventory_path, 'w') as f:
            f.write("# Feature-Engineered Datasets Inventory\n")
            f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Available Datasets:\n\n")
            
            for filename in sorted(saved_files):
                f.write(f"- {filename}\n")
            
            f.write(f"\n## Dataset Descriptions:\n\n")
            f.write("- market_expansion.csv: Geographic analysis data for market expansion decisions\n")
            f.write("- customer_analytics.csv: Customer behavior and RFM analysis data\n")
            f.write("- seasonal_intelligence_*.csv: Seasonal patterns and demand forecasting data\n")
            f.write("- payment_operations.csv: Payment behavior and operational metrics\n")
            f.write("- product_performance.csv: Product sales and performance analytics\n")
        
        logger.info(f"Saved {len(saved_files)} feature-engineered datasets")
        logger.info(f"Dataset inventory saved to {inventory_path}")
        
        return saved_files
    
    def get_feature_engineering_summary(self) -> Dict:
        """
        Get a summary of all feature engineering activities.
        
        Returns:
            Dict: Summary of feature engineering process
        """
        return {
            'total_features_created': len(self.feature_dictionary),
            'master_datasets_created': len(self.master_datasets),
            'feature_engineering_log': self.feature_log,
            'datasets_processed': list(self.datasets.keys())
        }


def load_feature_engineered_datasets(input_dir: str = "data/feature_engineered") -> Dict[str, pd.DataFrame]:
    """
    Load feature-engineered datasets from CSV files.
    
    Args:
        input_dir (str): Directory containing feature-engineered datasets
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary of feature-engineered datasets
    """
    import os
    
    if not os.path.exists(input_dir):
        logger.error(f"Feature-engineered data directory not found: {input_dir}")
        logger.info("Run create_enhanced_datasets_from_cleaned_data() first to create feature-engineered data files")
        return {}
    
    logger.info(f"Loading feature-engineered datasets from {input_dir}/...")
    
    datasets = {}
    
    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    for filename in csv_files:
        if filename == 'dataset_inventory.txt':
            continue
            
        filepath = os.path.join(input_dir, filename)
        dataset_name = filename.replace('.csv', '')
        
        try:
            df = pd.read_csv(filepath)
            datasets[dataset_name] = df
            logger.info(f"Loaded {dataset_name}: {len(df)} records")
        except Exception as e:
            logger.error(f"Failed to load {filename}: {str(e)}")
    
    logger.info(f"Successfully loaded {len(datasets)} feature-engineered datasets")
    return datasets


def create_enhanced_datasets_from_cleaned_data():
    """
    Main function to create enhanced datasets with engineered features from cleaned data.
    
    Returns:
        Tuple[FeatureEngineer, Dict[str, pd.DataFrame]]: Feature engineer instance and master datasets
    """
    logger.info("Starting feature engineering from cleaned datasets...")
    
    # Load cleaned datasets
    cleaned_datasets = load_cleaned_datasets("data/cleaned")
    
    if not cleaned_datasets:
        logger.error("Failed to load cleaned datasets")
        return None, {}
    
    logger.info(f"Loaded {len(cleaned_datasets)} cleaned datasets")
    
    # Initialize feature engineer
    feature_engineer = FeatureEngineer(cleaned_datasets)
    
    # Create master analytical datasets
    master_datasets = feature_engineer.create_master_analytical_datasets()
    
    # Save feature dictionary
    feature_engineer.save_feature_dictionary()
    
    # Save master datasets to files
    saved_files = feature_engineer.save_master_datasets()
    
    # Generate summary report
    summary = feature_engineer.get_feature_engineering_summary()
    
    # Save summary report
    import os
    os.makedirs('reports', exist_ok=True)
    
    with open('reports/feature_engineering_report.txt', 'w') as f:
        f.write("# Feature Engineering Summary Report\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total features created: {summary['total_features_created']}\n")
        f.write(f"Master datasets created: {summary['master_datasets_created']}\n")
        f.write(f"Datasets processed: {', '.join(summary['datasets_processed'])}\n")
        f.write(f"Files saved: {len(saved_files)}\n\n")
        
        f.write("## Saved Dataset Files:\n")
        for filename in saved_files:
            f.write(f"- {filename}\n")
        f.write("\n")
        
        f.write("## Feature Engineering Log:\n")
        for log_entry in summary['feature_engineering_log']:
            f.write(f"[{log_entry['timestamp']}] {log_entry['action']} - {log_entry['dataset']}: {log_entry['details']}\n")
    
    logger.info("Feature engineering completed successfully!")
    logger.info(f"Created {len(master_datasets)} master analytical datasets")
    logger.info(f"Generated {summary['total_features_created']} engineered features")
    
    return feature_engineer, master_datasets


if __name__ == "__main__":
    # Execute feature engineering
    print("🔧 Starting Feature Engineering and Data Preparation...")
    
    feature_engineer, master_datasets = create_enhanced_datasets_from_cleaned_data()
    
    if feature_engineer and master_datasets:
        print(f"✅ Feature engineering completed successfully!")
        print(f"📊 Created {len(master_datasets)} master analytical datasets:")
        for dataset_name in master_datasets.keys():
            if isinstance(master_datasets[dataset_name], dict):
                print(f"   - {dataset_name}: {len(master_datasets[dataset_name])} sub-datasets")
            else:
                print(f"   - {dataset_name}: {len(master_datasets[dataset_name])} records")
        
        print(f"📝 Feature dictionary and reports saved to 'reports/' directory")
    else:
        print("❌ Feature engineering failed!")