"""
Data Validation Module for Cleaned Brazilian E-commerce Dataset

This module provides validation functions to ensure data quality
after the cleaning process and before analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional
from data_cleaner import clean_brazilian_ecommerce_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    """
    Comprehensive data validator for cleaned Brazilian E-commerce dataset.
    Ensures data quality meets requirements for analysis.
    """
    
    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        """
        Initialize the DataValidator with cleaned datasets.
        
        Args:
            datasets (Dict[str, pd.DataFrame]): Dictionary of cleaned DataFrames
        """
        self.datasets = datasets
        self.validation_results = {}
        self.validation_passed = True
        
    def validate_data_completeness(self) -> Dict[str, any]:
        """
        Validate that critical data is complete after cleaning.
        
        Returns:
            Dict: Validation results for data completeness
        """
        logger.info("Validating data completeness...")
        
        completeness_results = {}
        
        # Critical columns that should have minimal missing values after cleaning
        critical_columns = {
            'orders': ['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp'],
            'customers': ['customer_id', 'customer_state'],
            'products': ['product_id', 'product_category_name'],
            'order_items': ['order_id', 'product_id', 'seller_id', 'price'],
            'order_payments': ['order_id', 'payment_type', 'payment_value']
        }
        
        for dataset_name, columns in critical_columns.items():
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name]
                dataset_results = {}
                
                for col in columns:
                    if col in df.columns:
                        missing_count = df[col].isnull().sum()
                        missing_percentage = (missing_count / len(df)) * 100
                        
                        dataset_results[col] = {
                            'missing_count': missing_count,
                            'missing_percentage': round(missing_percentage, 2),
                            'status': 'PASS' if missing_percentage < 1.0 else 'FAIL'
                        }
                        
                        if missing_percentage >= 1.0:
                            self.validation_passed = False
                            logger.warning(f"Critical column {dataset_name}.{col} has {missing_percentage:.2f}% missing values")
                
                completeness_results[dataset_name] = dataset_results
        
        self.validation_results['completeness'] = completeness_results
        return completeness_results
    
    def validate_data_types(self) -> Dict[str, any]:
        """
        Validate that data types are correct after conversion.
        
        Returns:
            Dict: Validation results for data types
        """
        logger.info("Validating data types...")
        
        type_results = {}
        
        # Expected data types after cleaning
        expected_types = {
            'orders': {
                'order_purchase_timestamp': 'datetime64[ns]',
                'order_approved_at': 'datetime64[ns]',
                'order_delivered_carrier_date': 'datetime64[ns]',
                'order_delivered_customer_date': 'datetime64[ns]',
                'order_estimated_delivery_date': 'datetime64[ns]',
                'order_status': 'category',
                'delivery_days': ['int64', 'float64'],  # Can be either due to NaN handling
                'order_year': ['int64', 'int32'],
                'order_month': ['int64', 'int32']
            },
            'products': {
                'product_category_name': 'category',
                'product_weight_g': 'float64',
                'product_length_cm': 'float64',
                'product_height_cm': 'float64',
                'product_width_cm': 'float64',
                'product_volume_cm3': 'float64'
            },
            'customers': {
                'customer_city': 'category',
                'customer_state': 'category'
            },
            'order_payments': {
                'payment_type': 'category'
            }
        }
        
        for dataset_name, type_expectations in expected_types.items():
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name]
                dataset_results = {}
                
                for col, expected_type in type_expectations.items():
                    if col in df.columns:
                        actual_type = str(df[col].dtype)
                        
                        # Handle multiple acceptable types
                        if isinstance(expected_type, list):
                            type_match = actual_type in expected_type
                        else:
                            type_match = actual_type == expected_type
                        
                        dataset_results[col] = {
                            'expected_type': expected_type,
                            'actual_type': actual_type,
                            'status': 'PASS' if type_match else 'FAIL'
                        }
                        
                        if not type_match:
                            self.validation_passed = False
                            logger.warning(f"Type mismatch in {dataset_name}.{col}: expected {expected_type}, got {actual_type}")
                
                type_results[dataset_name] = dataset_results
        
        self.validation_results['data_types'] = type_results
        return type_results
    
    def validate_business_rules(self) -> Dict[str, any]:
        """
        Validate business logic rules in the cleaned data.
        
        Returns:
            Dict: Validation results for business rules
        """
        logger.info("Validating business rules...")
        
        business_results = {}
        
        # Validate orders dataset business rules
        if 'orders' in self.datasets:
            orders_df = self.datasets['orders']
            orders_validation = {}
            
            # Rule 1: Delivery date should be after purchase date
            if 'order_delivered_customer_date' in orders_df.columns and 'order_purchase_timestamp' in orders_df.columns:
                valid_delivery_mask = (
                    orders_df['order_delivered_customer_date'].notna() & 
                    orders_df['order_purchase_timestamp'].notna()
                )
                
                if valid_delivery_mask.sum() > 0:
                    invalid_delivery_dates = (
                        orders_df.loc[valid_delivery_mask, 'order_delivered_customer_date'] < 
                        orders_df.loc[valid_delivery_mask, 'order_purchase_timestamp']
                    ).sum()
                    
                    orders_validation['delivery_after_purchase'] = {
                        'invalid_count': invalid_delivery_dates,
                        'total_checked': valid_delivery_mask.sum(),
                        'status': 'PASS' if invalid_delivery_dates == 0 else 'FAIL'
                    }
                    
                    if invalid_delivery_dates > 0:
                        self.validation_passed = False
                        logger.warning(f"Found {invalid_delivery_dates} orders with delivery date before purchase date")
            
            # Rule 2: Delivery days should be positive
            if 'delivery_days' in orders_df.columns:
                negative_delivery_days = (orders_df['delivery_days'] < 0).sum()
                
                orders_validation['positive_delivery_days'] = {
                    'invalid_count': negative_delivery_days,
                    'total_rows': len(orders_df),
                    'status': 'PASS' if negative_delivery_days == 0 else 'FAIL'
                }
                
                if negative_delivery_days > 0:
                    self.validation_passed = False
                    logger.warning(f"Found {negative_delivery_days} orders with negative delivery days")
            
            business_results['orders'] = orders_validation
        
        # Validate products dataset business rules
        if 'products' in self.datasets:
            products_df = self.datasets['products']
            products_validation = {}
            
            # Rule 1: Product dimensions should be positive
            dimension_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
            for col in dimension_cols:
                if col in products_df.columns:
                    negative_values = (products_df[col] <= 0).sum()
                    
                    products_validation[f'positive_{col}'] = {
                        'invalid_count': negative_values,
                        'total_rows': len(products_df),
                        'status': 'PASS' if negative_values == 0 else 'FAIL'
                    }
                    
                    if negative_values > 0:
                        self.validation_passed = False
                        logger.warning(f"Found {negative_values} products with non-positive {col}")
            
            business_results['products'] = products_validation
        
        # Validate order_payments dataset business rules
        if 'order_payments' in self.datasets:
            payments_df = self.datasets['order_payments']
            payments_validation = {}
            
            # Rule 1: Payment values should be positive
            if 'payment_value' in payments_df.columns:
                negative_payments = (payments_df['payment_value'] <= 0).sum()
                
                payments_validation['positive_payment_value'] = {
                    'invalid_count': negative_payments,
                    'total_rows': len(payments_df),
                    'status': 'PASS' if negative_payments == 0 else 'FAIL'
                }
                
                if negative_payments > 0:
                    self.validation_passed = False
                    logger.warning(f"Found {negative_payments} payments with non-positive values")
            
            business_results['order_payments'] = payments_validation
        
        self.validation_results['business_rules'] = business_results
        return business_results
    
    def validate_referential_integrity(self) -> Dict[str, any]:
        """
        Validate referential integrity between datasets.
        
        Returns:
            Dict: Validation results for referential integrity
        """
        logger.info("Validating referential integrity...")
        
        integrity_results = {}
        
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
                
                relationship_key = f"{parent_table}_{child_table}"
                integrity_results[relationship_key] = {
                    'parent_table': parent_table,
                    'parent_key': parent_key,
                    'child_table': child_table,
                    'child_key': child_key,
                    'orphaned_count': orphaned_count,
                    'child_unique_keys': len(child_keys),
                    'status': 'PASS' if orphaned_count == 0 else 'FAIL'
                }
                
                if orphaned_count > 0:
                    self.validation_passed = False
                    logger.warning(f"Referential integrity violation: {orphaned_count} orphaned records in {child_table}")
        
        self.validation_results['referential_integrity'] = integrity_results
        return integrity_results
    
    def validate_data_ranges(self) -> Dict[str, any]:
        """
        Validate that numerical data falls within reasonable ranges.
        
        Returns:
            Dict: Validation results for data ranges
        """
        logger.info("Validating data ranges...")
        
        range_results = {}
        
        # Define reasonable ranges for key metrics
        range_expectations = {
            'orders': {
                'delivery_days': {'min': 0, 'max': 365},  # Delivery should be within a year
                'order_year': {'min': 2016, 'max': 2019},  # Dataset time range
                'order_month': {'min': 1, 'max': 12}
            },
            'products': {
                'product_weight_g': {'min': 0, 'max': 50000},  # Up to 50kg seems reasonable
                'product_length_cm': {'min': 0, 'max': 200},   # Up to 2m
                'product_height_cm': {'min': 0, 'max': 200},
                'product_width_cm': {'min': 0, 'max': 200}
            },
            'order_payments': {
                'payment_value': {'min': 0, 'max': 10000},  # Up to R$10,000
                'payment_installments': {'min': 1, 'max': 24}  # Reasonable installment range
            },
            'order_reviews': {
                'review_score': {'min': 1, 'max': 5}  # Standard 1-5 rating scale
            }
        }
        
        for dataset_name, column_ranges in range_expectations.items():
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name]
                dataset_results = {}
                
                for col, range_def in column_ranges.items():
                    if col in df.columns:
                        valid_data = df[col].dropna()
                        
                        if len(valid_data) > 0:
                            out_of_range_count = (
                                (valid_data < range_def['min']) | 
                                (valid_data > range_def['max'])
                            ).sum()
                            
                            dataset_results[col] = {
                                'expected_min': range_def['min'],
                                'expected_max': range_def['max'],
                                'actual_min': valid_data.min(),
                                'actual_max': valid_data.max(),
                                'out_of_range_count': out_of_range_count,
                                'total_values': len(valid_data),
                                'status': 'PASS' if out_of_range_count == 0 else 'WARN'  # Warning, not failure
                            }
                            
                            if out_of_range_count > 0:
                                logger.warning(f"Found {out_of_range_count} values outside expected range in {dataset_name}.{col}")
                
                range_results[dataset_name] = dataset_results
        
        self.validation_results['data_ranges'] = range_results
        return range_results
    
    def generate_validation_report(self) -> str:
        """
        Generate a comprehensive validation report.
        
        Returns:
            str: Detailed validation report
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("DATA VALIDATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overall validation status
        overall_status = "✅ PASSED" if self.validation_passed else "❌ FAILED"
        report_lines.append(f"🎯 OVERALL VALIDATION STATUS: {overall_status}")
        report_lines.append("")
        
        # Dataset overview
        report_lines.append("📊 DATASET OVERVIEW:")
        for name, df in self.datasets.items():
            report_lines.append(f"   • {name}: {len(df):,} rows, {len(df.columns)} columns")
        report_lines.append("")
        
        # Validation results summary
        validation_categories = [
            ('completeness', '🔍 DATA COMPLETENESS'),
            ('data_types', '🏷️  DATA TYPES'),
            ('business_rules', '📋 BUSINESS RULES'),
            ('referential_integrity', '🔗 REFERENTIAL INTEGRITY'),
            ('data_ranges', '📏 DATA RANGES')
        ]
        
        for category_key, category_title in validation_categories:
            if category_key in self.validation_results:
                report_lines.append(f"{category_title}:")
                
                category_results = self.validation_results[category_key]
                
                if category_key == 'completeness':
                    for dataset, columns in category_results.items():
                        failed_columns = [col for col, result in columns.items() if result['status'] == 'FAIL']
                        if failed_columns:
                            report_lines.append(f"   ❌ {dataset}: {len(failed_columns)} critical columns with high missing values")
                        else:
                            report_lines.append(f"   ✅ {dataset}: All critical columns complete")
                
                elif category_key == 'data_types':
                    for dataset, columns in category_results.items():
                        failed_columns = [col for col, result in columns.items() if result['status'] == 'FAIL']
                        if failed_columns:
                            report_lines.append(f"   ❌ {dataset}: {len(failed_columns)} columns with incorrect types")
                        else:
                            report_lines.append(f"   ✅ {dataset}: All data types correct")
                
                elif category_key == 'business_rules':
                    for dataset, rules in category_results.items():
                        failed_rules = [rule for rule, result in rules.items() if result['status'] == 'FAIL']
                        if failed_rules:
                            report_lines.append(f"   ❌ {dataset}: {len(failed_rules)} business rule violations")
                        else:
                            report_lines.append(f"   ✅ {dataset}: All business rules satisfied")
                
                elif category_key == 'referential_integrity':
                    failed_relationships = [rel for rel, result in category_results.items() if result['status'] == 'FAIL']
                    if failed_relationships:
                        report_lines.append(f"   ❌ {len(failed_relationships)} relationships with integrity issues")
                    else:
                        report_lines.append(f"   ✅ All {len(category_results)} relationships maintain integrity")
                
                elif category_key == 'data_ranges':
                    for dataset, columns in category_results.items():
                        warned_columns = [col for col, result in columns.items() if result['status'] == 'WARN']
                        if warned_columns:
                            report_lines.append(f"   ⚠️  {dataset}: {len(warned_columns)} columns with values outside expected ranges")
                        else:
                            report_lines.append(f"   ✅ {dataset}: All values within expected ranges")
                
                report_lines.append("")
        
        # Recommendations
        report_lines.append("💡 RECOMMENDATIONS:")
        if self.validation_passed:
            report_lines.append("   • Data quality is excellent and ready for analysis")
            report_lines.append("   • Proceed with confidence to the feature engineering phase")
        else:
            report_lines.append("   • Review and address validation failures before proceeding")
            report_lines.append("   • Check data cleaning logic for failed validations")
            report_lines.append("   • Consider additional data quality measures")
        
        return "\n".join(report_lines)
    
    def validate_all_data(self) -> Tuple[bool, str]:
        """
        Perform comprehensive data validation.
        
        Returns:
            Tuple[bool, str]: Validation passed status and detailed report
        """
        logger.info("Starting comprehensive data validation...")
        
        # Execute all validation checks
        self.validate_data_completeness()
        self.validate_data_types()
        self.validate_business_rules()
        self.validate_referential_integrity()
        self.validate_data_ranges()
        
        # Generate final report
        validation_report = self.generate_validation_report()
        
        logger.info(f"Data validation completed. Status: {'PASSED' if self.validation_passed else 'FAILED'}")
        return self.validation_passed, validation_report


def validate_cleaned_data(datasets: Dict[str, pd.DataFrame]) -> Tuple[bool, str]:
    """
    Convenience function to validate cleaned datasets.
    
    Args:
        datasets (Dict[str, pd.DataFrame]): Cleaned datasets
        
    Returns:
        Tuple[bool, str]: Validation passed status and report
    """
    validator = DataValidator(datasets)
    return validator.validate_all_data()


if __name__ == "__main__":
    # Example usage
    print("Starting data validation on cleaned datasets...")
    
    try:
        # Load cleaned data from saved files
        from save_cleaned_data import load_cleaned_datasets
        print("📂 Loading cleaned datasets from files...")
        cleaned_datasets = load_cleaned_datasets()
        
        if not cleaned_datasets:
            print("❌ No cleaned datasets found. Loading and cleaning fresh data...")
            # Fallback to fresh cleaning if files don't exist
            cleaned_datasets, cleaning_report = clean_brazilian_ecommerce_data()
        else:
            print(f"✅ Loaded {len(cleaned_datasets)} datasets from saved files")
        
        # Validate cleaned data
        validation_passed, validation_report = validate_cleaned_data(cleaned_datasets)
        
        # Display validation report
        print("\n" + validation_report)
        
        # Save validation report
        import os
        os.makedirs('reports', exist_ok=True)
        
        # Save to both reports and cleaned data directory
        with open('reports/data_validation_report.txt', 'w', encoding='utf-8') as f:
            f.write(validation_report)
        
        # Also save in cleaned data directory
        with open('data/cleaned/validation_report_saved_data.txt', 'w', encoding='utf-8') as f:
            f.write(validation_report)
        
        if validation_passed:
            print(f"\n✅ Data validation PASSED! Data is ready for analysis.")
        else:
            print(f"\n❌ Data validation FAILED! Please review issues before proceeding.")
        
        print(f"📄 Validation report saved to 'reports/data_validation_report.txt'")
        
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        raise