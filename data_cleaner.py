"""
Data Cleaning Module for Brazilian E-commerce Dataset

This module provides comprehensive data cleaning functions to address
identified quality issues and prepare data for analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional
import warnings
from data_loader import load_brazilian_ecommerce_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Comprehensive data cleaner for the Brazilian E-commerce dataset.
    Addresses missing values, duplicates, data type conversions, and foreign key issues.
    """
    
    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        """
        Initialize the DataCleaner with loaded datasets.
        
        Args:
            datasets (Dict[str, pd.DataFrame]): Dictionary of loaded DataFrames
        """
        self.datasets = datasets.copy()  # Work with a copy to preserve original
        self.cleaning_log = []
        self.validation_results = {}
        
    def log_cleaning_action(self, action: str, dataset: str, details: str):
        """Log cleaning actions for audit trail."""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'dataset': dataset,
            'details': details
        }
        self.cleaning_log.append(log_entry)
        logger.info(f"{action} - {dataset}: {details}")
    
    def clean_missing_values(self) -> Dict[str, pd.DataFrame]:
        """
        Handle missing values using business logic and appropriate imputation strategies.
        
        Returns:
            Dict[str, pd.DataFrame]: Datasets with missing values handled
        """
        logger.info("Starting missing values cleaning...")
        
        # Handle orders dataset missing values
        if 'orders' in self.datasets:
            orders_df = self.datasets['orders'].copy()
            original_shape = orders_df.shape
            
            # Handle missing delivery dates using business logic
            # If order is delivered but missing delivery date, use estimated date
            delivered_mask = (orders_df['order_status'] == 'delivered') & \
                           (orders_df['order_delivered_customer_date'].isna()) & \
                           (orders_df['order_estimated_delivery_date'].notna())
            
            if delivered_mask.sum() > 0:
                orders_df.loc[delivered_mask, 'order_delivered_customer_date'] = \
                    orders_df.loc[delivered_mask, 'order_estimated_delivery_date']
                
                self.log_cleaning_action(
                    'IMPUTE_MISSING_DELIVERY_DATE',
                    'orders',
                    f"Filled {delivered_mask.sum()} missing delivery dates with estimated dates for delivered orders"
                )
            
            # Handle missing carrier delivery dates
            # Use business logic: if customer delivery date exists, carrier date should be before it
            carrier_missing = orders_df['order_delivered_carrier_date'].isna() & \
                            orders_df['order_delivered_customer_date'].notna()
            
            if carrier_missing.sum() > 0:
                # Estimate carrier date as 1-2 days before customer delivery
                orders_df.loc[carrier_missing, 'order_delivered_carrier_date'] = \
                    pd.to_datetime(orders_df.loc[carrier_missing, 'order_delivered_customer_date']) - \
                    pd.Timedelta(days=1)
                
                self.log_cleaning_action(
                    'IMPUTE_MISSING_CARRIER_DATE',
                    'orders',
                    f"Estimated {carrier_missing.sum()} missing carrier delivery dates"
                )
            
            self.datasets['orders'] = orders_df
        
        # Handle products dataset missing values
        if 'products' in self.datasets:
            products_df = self.datasets['products'].copy()
            
            # Products with missing category information - these are likely data entry errors
            # We'll keep them but mark them as 'unknown' category
            missing_category = products_df['product_category_name'].isna()
            if missing_category.sum() > 0:
                products_df.loc[missing_category, 'product_category_name'] = 'unknown'
                
                self.log_cleaning_action(
                    'FILL_MISSING_CATEGORY',
                    'products',
                    f"Filled {missing_category.sum()} missing product categories with 'unknown'"
                )
            
            # Handle missing product dimensions and weights
            # Use median values within the same category for imputation
            numeric_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
            
            for col in numeric_cols:
                missing_mask = products_df[col].isna()
                if missing_mask.sum() > 0:
                    # Impute with median by category
                    median_by_category = products_df.groupby('product_category_name')[col].median()
                    
                    for category in products_df.loc[missing_mask, 'product_category_name'].unique():
                        category_mask = missing_mask & (products_df['product_category_name'] == category)
                        if category_mask.sum() > 0 and category in median_by_category:
                            products_df.loc[category_mask, col] = median_by_category[category]
                    
                    # For any remaining missing values, use overall median
                    still_missing = products_df[col].isna()
                    if still_missing.sum() > 0:
                        overall_median = products_df[col].median()
                        products_df.loc[still_missing, col] = overall_median
                    
                    self.log_cleaning_action(
                        'IMPUTE_MISSING_DIMENSIONS',
                        'products',
                        f"Imputed {missing_mask.sum()} missing values in {col} using category medians"
                    )
                
                # Fix any zero or negative values that might exist
                invalid_values = products_df[col] <= 0
                if invalid_values.sum() > 0:
                    # Replace with category median or overall median if category median is also invalid
                    median_by_category = products_df[products_df[col] > 0].groupby('product_category_name')[col].median()
                    
                    for category in products_df.loc[invalid_values, 'product_category_name'].unique():
                        category_mask = invalid_values & (products_df['product_category_name'] == category)
                        if category_mask.sum() > 0 and category in median_by_category and median_by_category[category] > 0:
                            products_df.loc[category_mask, col] = median_by_category[category]
                    
                    # For any remaining invalid values, use overall median of positive values
                    still_invalid = products_df[col] <= 0
                    if still_invalid.sum() > 0:
                        overall_median = products_df[products_df[col] > 0][col].median()
                        if pd.notna(overall_median) and overall_median > 0:
                            products_df.loc[still_invalid, col] = overall_median
                    
                    self.log_cleaning_action(
                        'FIX_INVALID_DIMENSIONS',
                        'products',
                        f"Fixed {invalid_values.sum()} invalid (<=0) values in {col}"
                    )
            
            self.datasets['products'] = products_df
        
        # Handle order_reviews dataset - keep missing comments as they represent valid business case
        # (customers who didn't leave detailed reviews)
        if 'order_reviews' in self.datasets:
            reviews_df = self.datasets['order_reviews'].copy()
            
            # Don't impute missing review comments as they represent legitimate missing data
            # Just log the situation
            missing_titles = reviews_df['review_comment_title'].isna().sum()
            missing_messages = reviews_df['review_comment_message'].isna().sum()
            
            self.log_cleaning_action(
                'PRESERVE_MISSING_REVIEWS',
                'order_reviews',
                f"Preserved {missing_titles} missing review titles and {missing_messages} missing review messages as valid business case"
            )
        
        # Handle order_payments dataset - fix invalid payment values
        if 'order_payments' in self.datasets:
            payments_df = self.datasets['order_payments'].copy()
            
            # Fix zero or negative payment values
            invalid_payments = payments_df['payment_value'] <= 0
            if invalid_payments.sum() > 0:
                # Replace with median payment value by payment type
                median_by_type = payments_df[payments_df['payment_value'] > 0].groupby('payment_type')['payment_value'].median()
                
                for payment_type in payments_df.loc[invalid_payments, 'payment_type'].unique():
                    type_mask = invalid_payments & (payments_df['payment_type'] == payment_type)
                    if type_mask.sum() > 0 and payment_type in median_by_type:
                        payments_df.loc[type_mask, 'payment_value'] = median_by_type[payment_type]
                
                # For any remaining invalid values, use overall median
                still_invalid = payments_df['payment_value'] <= 0
                if still_invalid.sum() > 0:
                    overall_median = payments_df[payments_df['payment_value'] > 0]['payment_value'].median()
                    payments_df.loc[still_invalid, 'payment_value'] = overall_median
                
                self.log_cleaning_action(
                    'FIX_INVALID_PAYMENTS',
                    'order_payments',
                    f"Fixed {invalid_payments.sum()} invalid (<=0) payment values"
                )
            
            self.datasets['order_payments'] = payments_df
        
        logger.info("Missing values cleaning completed")
        return self.datasets
    
    def remove_duplicates(self) -> Dict[str, pd.DataFrame]:
        """
        Remove duplicate records, especially from geolocation dataset.
        
        Returns:
            Dict[str, pd.DataFrame]: Datasets with duplicates removed
        """
        logger.info("Starting duplicate removal...")
        
        # Handle geolocation duplicates (major issue - 26% duplicates)
        if 'geolocation' in self.datasets:
            geo_df = self.datasets['geolocation'].copy()
            original_count = len(geo_df)
            
            # Remove exact duplicates
            geo_df = geo_df.drop_duplicates()
            duplicates_removed = original_count - len(geo_df)
            
            # For remaining near-duplicates (same zip code but slightly different coordinates),
            # keep the first occurrence for each zip code to maintain consistency
            geo_df = geo_df.drop_duplicates(subset=['geolocation_zip_code_prefix'], keep='first')
            
            final_count = len(geo_df)
            total_removed = original_count - final_count
            
            self.log_cleaning_action(
                'REMOVE_DUPLICATES',
                'geolocation',
                f"Removed {total_removed:,} duplicate records ({(total_removed/original_count)*100:.1f}%)"
            )
            
            self.datasets['geolocation'] = geo_df
        
        # Check other datasets for duplicates (should be minimal based on quality report)
        for dataset_name, df in self.datasets.items():
            if dataset_name != 'geolocation':  # Already handled
                original_count = len(df)
                df_clean = df.drop_duplicates()
                duplicates_removed = original_count - len(df_clean)
                
                if duplicates_removed > 0:
                    self.datasets[dataset_name] = df_clean
                    self.log_cleaning_action(
                        'REMOVE_DUPLICATES',
                        dataset_name,
                        f"Removed {duplicates_removed} duplicate records"
                    )
        
        logger.info("Duplicate removal completed")
        return self.datasets
    
    def convert_data_types(self) -> Dict[str, pd.DataFrame]:
        """
        Convert columns to appropriate data types for better performance and analysis.
        
        Returns:
            Dict[str, pd.DataFrame]: Datasets with proper data types
        """
        logger.info("Starting data type conversions...")
        
        # Define date columns that need conversion
        date_columns = {
            'orders': [
                'order_purchase_timestamp',
                'order_approved_at',
                'order_delivered_carrier_date',
                'order_delivered_customer_date',
                'order_estimated_delivery_date'
            ],
            'order_items': ['shipping_limit_date'],
            'order_reviews': ['review_creation_date', 'review_answer_timestamp']
        }
        
        # Define categorical columns for memory efficiency
        categorical_columns = {
            'customers': ['customer_city', 'customer_state'],
            'geolocation': ['geolocation_city', 'geolocation_state'],
            'order_items': ['seller_id'],
            'order_payments': ['payment_type'],
            'order_reviews': ['review_comment_title'],
            'orders': ['order_status'],
            'products': ['product_category_name'],
            'sellers': ['seller_state']
        }
        
        # Convert date columns
        for dataset_name, columns in date_columns.items():
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name].copy()
                
                for col in columns:
                    if col in df.columns:
                        try:
                            original_type = str(df[col].dtype)
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                            
                            self.log_cleaning_action(
                                'CONVERT_DATETIME',
                                dataset_name,
                                f"Converted {col} from {original_type} to datetime64"
                            )
                        except Exception as e:
                            logger.warning(f"Failed to convert {col} in {dataset_name}: {str(e)}")
                
                self.datasets[dataset_name] = df
        
        # Convert categorical columns (do this after merge to ensure product categories are properly handled)
        for dataset_name, columns in categorical_columns.items():
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name].copy()
                
                for col in columns:
                    if col in df.columns:
                        try:
                            original_type = str(df[col].dtype)
                            # Ensure we handle the merged product category properly
                            if dataset_name == 'products' and col == 'product_category_name':
                                # This will be converted after merge
                                continue
                            df[col] = df[col].astype('category')
                            
                            self.log_cleaning_action(
                                'CONVERT_CATEGORY',
                                dataset_name,
                                f"Converted {col} from {original_type} to category"
                            )
                        except Exception as e:
                            logger.warning(f"Failed to convert {col} in {dataset_name}: {str(e)}")
                
                self.datasets[dataset_name] = df
        
        logger.info("Data type conversions completed")
        return self.datasets
    
    def merge_product_categories(self) -> Dict[str, pd.DataFrame]:
        """
        Merge product category translations with products dataset.
        
        Returns:
            Dict[str, pd.DataFrame]: Datasets with merged category information
        """
        logger.info("Starting product category merge...")
        
        if 'products' in self.datasets and 'product_categories' in self.datasets:
            products_df = self.datasets['products'].copy()
            categories_df = self.datasets['product_categories'].copy()
            
            original_count = len(products_df)
            
            # Merge category translations
            products_merged = products_df.merge(
                categories_df,
                on='product_category_name',
                how='left'
            )
            
            # Handle products without category translations
            missing_translations = products_merged['product_category_name_english'].isna()
            if missing_translations.sum() > 0:
                # For unknown categories, use the Portuguese name as English name
                products_merged.loc[missing_translations, 'product_category_name_english'] = \
                    products_merged.loc[missing_translations, 'product_category_name']
                
                self.log_cleaning_action(
                    'HANDLE_MISSING_TRANSLATIONS',
                    'products',
                    f"Used Portuguese names as English translations for {missing_translations.sum()} products"
                )
            
            self.log_cleaning_action(
                'MERGE_CATEGORIES',
                'products',
                f"Successfully merged category translations for {len(products_merged)} products"
            )
            
            # Now convert product_category_name to category after merge
            try:
                original_type = str(products_merged['product_category_name'].dtype)
                products_merged['product_category_name'] = products_merged['product_category_name'].astype('category')
                
                self.log_cleaning_action(
                    'CONVERT_CATEGORY',
                    'products',
                    f"Converted product_category_name from {original_type} to category after merge"
                )
            except Exception as e:
                logger.warning(f"Failed to convert product_category_name to category: {str(e)}")
            
            self.datasets['products'] = products_merged
        
        logger.info("Product category merge completed")
        return self.datasets
    
    def validate_foreign_keys(self) -> Dict[str, any]:
        """
        Validate and report on foreign key relationships.
        
        Returns:
            Dict: Validation results for foreign key relationships
        """
        logger.info("Starting foreign key validation...")
        
        validation_results = {}
        
        # Define key relationships to validate
        relationships = [
            ('customers', 'customer_id', 'orders', 'customer_id'),
            ('orders', 'order_id', 'order_items', 'order_id'),
            ('orders', 'order_id', 'order_payments', 'order_id'),
            ('orders', 'order_id', 'order_reviews', 'order_id'),
            ('products', 'product_id', 'order_items', 'product_id'),
            ('sellers', 'seller_id', 'order_items', 'seller_id')
        ]
        
        for parent_table, parent_key, child_table, child_key in relationships:
            if (parent_table in self.datasets and child_table in self.datasets and
                parent_key in self.datasets[parent_table].columns and
                child_key in self.datasets[child_table].columns):
                
                parent_keys = set(self.datasets[parent_table][parent_key].dropna())
                child_keys = set(self.datasets[child_table][child_key].dropna())
                
                orphaned_records = child_keys - parent_keys
                orphaned_count = len(orphaned_records)
                
                validation_results[f"{parent_table}_{child_table}"] = {
                    'parent_table': parent_table,
                    'parent_key': parent_key,
                    'child_table': child_table,
                    'child_key': child_key,
                    'parent_unique_keys': len(parent_keys),
                    'child_unique_keys': len(child_keys),
                    'orphaned_records': orphaned_count,
                    'orphaned_percentage': (orphaned_count / len(child_keys)) * 100 if len(child_keys) > 0 else 0,
                    'integrity_status': 'GOOD' if orphaned_count == 0 else 'ISSUES'
                }
                
                self.log_cleaning_action(
                    'VALIDATE_FOREIGN_KEYS',
                    f"{parent_table}->{child_table}",
                    f"Orphaned records: {orphaned_count} ({(orphaned_count / len(child_keys)) * 100:.2f}%)" if len(child_keys) > 0 else "No child records"
                )
        
        self.validation_results = validation_results
        logger.info("Foreign key validation completed")
        return validation_results
    
    def create_derived_features(self) -> Dict[str, pd.DataFrame]:
        """
        Create useful derived features for analysis.
        
        Returns:
            Dict[str, pd.DataFrame]: Datasets with derived features
        """
        logger.info("Starting derived feature creation...")
        
        # Add delivery performance metrics to orders
        if 'orders' in self.datasets:
            orders_df = self.datasets['orders'].copy()
            
            # Calculate delivery days
            delivered_mask = (orders_df['order_delivered_customer_date'].notna() & 
                            orders_df['order_purchase_timestamp'].notna())
            
            if delivered_mask.sum() > 0:
                orders_df.loc[delivered_mask, 'delivery_days'] = (
                    orders_df.loc[delivered_mask, 'order_delivered_customer_date'] - 
                    orders_df.loc[delivered_mask, 'order_purchase_timestamp']
                ).dt.days
                
                # Calculate delivery performance vs estimate
                estimate_mask = delivered_mask & orders_df['order_estimated_delivery_date'].notna()
                if estimate_mask.sum() > 0:
                    orders_df.loc[estimate_mask, 'delivery_vs_estimate_days'] = (
                        orders_df.loc[estimate_mask, 'order_delivered_customer_date'] - 
                        orders_df.loc[estimate_mask, 'order_estimated_delivery_date']
                    ).dt.days
                    
                    # On-time delivery flag (delivered on or before estimate)
                    orders_df.loc[estimate_mask, 'on_time_delivery'] = \
                        orders_df.loc[estimate_mask, 'delivery_vs_estimate_days'] <= 0
                
                self.log_cleaning_action(
                    'CREATE_DELIVERY_METRICS',
                    'orders',
                    f"Created delivery performance metrics for {delivered_mask.sum()} orders"
                )
            
            # Add order timing features
            orders_df['order_year'] = orders_df['order_purchase_timestamp'].dt.year
            orders_df['order_month'] = orders_df['order_purchase_timestamp'].dt.month
            orders_df['order_day_of_week'] = orders_df['order_purchase_timestamp'].dt.dayofweek
            orders_df['order_hour'] = orders_df['order_purchase_timestamp'].dt.hour
            
            self.log_cleaning_action(
                'CREATE_TIME_FEATURES',
                'orders',
                "Created temporal features (year, month, day_of_week, hour)"
            )
            
            self.datasets['orders'] = orders_df
        
        # Add product dimension features
        if 'products' in self.datasets:
            products_df = self.datasets['products'].copy()
            
            # Calculate product volume
            dimension_cols = ['product_length_cm', 'product_height_cm', 'product_width_cm']
            if all(col in products_df.columns for col in dimension_cols):
                products_df['product_volume_cm3'] = (
                    products_df['product_length_cm'] * 
                    products_df['product_height_cm'] * 
                    products_df['product_width_cm']
                )
                
                # Calculate weight-to-volume ratio (density indicator)
                volume_mask = products_df['product_volume_cm3'] > 0
                weight_mask = products_df['product_weight_g'] > 0
                valid_mask = volume_mask & weight_mask
                
                if valid_mask.sum() > 0:
                    products_df.loc[valid_mask, 'weight_volume_ratio'] = (
                        products_df.loc[valid_mask, 'product_weight_g'] / 
                        products_df.loc[valid_mask, 'product_volume_cm3']
                    )
                
                self.log_cleaning_action(
                    'CREATE_PRODUCT_METRICS',
                    'products',
                    f"Created volume and density metrics for {valid_mask.sum()} products"
                )
            
            self.datasets['products'] = products_df
        
        logger.info("Derived feature creation completed")
        return self.datasets
    
    def generate_cleaning_report(self) -> str:
        """
        Generate a comprehensive cleaning report.
        
        Returns:
            str: Detailed cleaning report
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("DATA CLEANING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary of actions
        report_lines.append("📋 CLEANING ACTIONS SUMMARY:")
        action_counts = {}
        for log_entry in self.cleaning_log:
            action = log_entry['action']
            action_counts[action] = action_counts.get(action, 0) + 1
        
        for action, count in action_counts.items():
            report_lines.append(f"   • {action}: {count} operations")
        report_lines.append("")
        
        # Dataset size changes
        report_lines.append("📊 DATASET SIZE CHANGES:")
        for dataset_name, df in self.datasets.items():
            report_lines.append(f"   • {dataset_name}: {len(df):,} rows, {len(df.columns)} columns")
        report_lines.append("")
        
        # Foreign key validation results
        if self.validation_results:
            report_lines.append("🔗 FOREIGN KEY VALIDATION:")
            for relationship, results in self.validation_results.items():
                status = results['integrity_status']
                orphaned = results['orphaned_records']
                report_lines.append(f"   • {relationship}: {status} ({orphaned} orphaned records)")
        report_lines.append("")
        
        # Detailed action log
        report_lines.append("📝 DETAILED ACTION LOG:")
        for log_entry in self.cleaning_log:
            report_lines.append(f"   [{log_entry['timestamp']}] {log_entry['action']} - {log_entry['dataset']}")
            report_lines.append(f"      {log_entry['details']}")
        
        return "\n".join(report_lines)
    
    def clean_all_data(self) -> Tuple[Dict[str, pd.DataFrame], str]:
        """
        Perform comprehensive data cleaning pipeline.
        
        Returns:
            Tuple[Dict[str, pd.DataFrame], str]: Cleaned datasets and cleaning report
        """
        logger.info("Starting comprehensive data cleaning pipeline...")
        
        # Execute cleaning steps in order
        self.clean_missing_values()
        self.remove_duplicates()
        self.convert_data_types()
        self.merge_product_categories()
        self.create_derived_features()
        self.validate_foreign_keys()
        
        # Generate final report
        cleaning_report = self.generate_cleaning_report()
        
        logger.info("Data cleaning pipeline completed successfully")
        return self.datasets, cleaning_report


def clean_brazilian_ecommerce_data(data_dir: str = "data") -> Tuple[Dict[str, pd.DataFrame], str]:
    """
    Convenience function to load and clean all Brazilian e-commerce datasets.
    
    Args:
        data_dir (str): Path to data directory
        
    Returns:
        Tuple[Dict[str, pd.DataFrame], str]: Cleaned datasets and cleaning report
    """
    # Load raw data
    logger.info("Loading raw datasets...")
    datasets, _ = load_brazilian_ecommerce_data(data_dir)
    
    if not datasets:
        raise ValueError("No datasets loaded. Please check data directory and files.")
    
    # Initialize cleaner and clean data
    cleaner = DataCleaner(datasets)
    cleaned_datasets, cleaning_report = cleaner.clean_all_data()
    
    return cleaned_datasets, cleaning_report


if __name__ == "__main__":
    # Example usage
    print("Starting comprehensive data cleaning...")
    
    try:
        # Clean all datasets
        cleaned_datasets, report = clean_brazilian_ecommerce_data()
        
        # Display report
        print("\n" + report)
        
        # Save report
        import os
        os.makedirs('reports', exist_ok=True)
        
        with open('reports/data_cleaning_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Data cleaning completed successfully!")
        print(f"📄 Cleaning report saved to 'reports/data_cleaning_report.txt'")
        print(f"🗂️  Cleaned datasets available in memory with {len(cleaned_datasets)} datasets")
        
        # Display final dataset summary
        print("\n📊 FINAL DATASET SUMMARY:")
        for name, df in cleaned_datasets.items():
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            print(f"   • {name}: {len(df):,} rows, {len(df.columns)} columns, {memory_mb:.1f} MB")
        
    except Exception as e:
        logger.error(f"Data cleaning failed: {str(e)}")
        raise