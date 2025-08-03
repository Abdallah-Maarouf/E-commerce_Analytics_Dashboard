"""
Data Loading Module for Brazilian E-commerce Dataset

This module provides functionality to load and validate all 9 CSV files
from the Brazilian E-commerce dataset with comprehensive error handling.
"""

import pandas as pd
import os
import logging
from typing import Dict, Optional, Tuple
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    """
    A comprehensive data loader for the Brazilian E-commerce dataset.
    Handles loading, validation, and basic error checking for all CSV files.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the DataLoader with the data directory path.
        
        Args:
            data_dir (str): Path to the directory containing CSV files
        """
        self.data_dir = data_dir
        self.datasets = {}
        
        # Define expected files and their descriptions
        self.file_mapping = {
            'customers': 'olist_customers_dataset.csv',
            'geolocation': 'olist_geolocation_dataset.csv',
            'order_items': 'olist_order_items_dataset.csv',
            'order_payments': 'olist_order_payments_dataset.csv',
            'order_reviews': 'olist_order_reviews_dataset.csv',
            'orders': 'olist_orders_dataset.csv',
            'products': 'olist_products_dataset.csv',
            'sellers': 'olist_sellers_dataset.csv',
            'product_categories': 'product_category_name_translation.csv'
        }
        
    def validate_file_exists(self, filename: str) -> bool:
        """
        Check if a file exists in the data directory.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        file_path = os.path.join(self.data_dir, filename)
        return os.path.exists(file_path)
    
    def load_single_file(self, key: str, filename: str) -> Optional[pd.DataFrame]:
        """
        Load a single CSV file with error handling.
        
        Args:
            key (str): Dataset key for identification
            filename (str): Name of the CSV file
            
        Returns:
            Optional[pd.DataFrame]: Loaded DataFrame or None if failed
        """
        file_path = os.path.join(self.data_dir, filename)
        
        try:
            # Check if file exists
            if not self.validate_file_exists(filename):
                logger.error(f"File not found: {filename}")
                return None
            
            # Load the CSV file
            logger.info(f"Loading {filename}...")
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Basic validation
            if df.empty:
                logger.warning(f"File {filename} is empty")
                return None
            
            logger.info(f"Successfully loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except pd.errors.EmptyDataError:
            logger.error(f"File {filename} is empty or corrupted")
            return None
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing {filename}: {str(e)}")
            return None
        except UnicodeDecodeError:
            # Try alternative encoding
            try:
                logger.warning(f"UTF-8 encoding failed for {filename}, trying latin-1")
                df = pd.read_csv(file_path, encoding='latin-1')
                logger.info(f"Successfully loaded {filename} with latin-1 encoding: {df.shape[0]} rows, {df.shape[1]} columns")
                return df
            except Exception as e:
                logger.error(f"Failed to load {filename} with alternative encoding: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error loading {filename}: {str(e)}")
            return None
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all datasets from the Brazilian E-commerce dataset.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all loaded datasets
        """
        logger.info("Starting to load all datasets...")
        
        loaded_datasets = {}
        failed_loads = []
        
        for key, filename in self.file_mapping.items():
            df = self.load_single_file(key, filename)
            if df is not None:
                loaded_datasets[key] = df
            else:
                failed_loads.append(filename)
        
        # Report results
        logger.info(f"Successfully loaded {len(loaded_datasets)}/{len(self.file_mapping)} datasets")
        
        if failed_loads:
            logger.warning(f"Failed to load: {', '.join(failed_loads)}")
        
        self.datasets = loaded_datasets
        return loaded_datasets
    
    def get_dataset_summary(self) -> pd.DataFrame:
        """
        Generate a summary of all loaded datasets.
        
        Returns:
            pd.DataFrame: Summary information about each dataset
        """
        if not self.datasets:
            logger.warning("No datasets loaded. Call load_all_datasets() first.")
            return pd.DataFrame()
        
        summary_data = []
        
        for key, df in self.datasets.items():
            summary_data.append({
                'Dataset': key,
                'Filename': self.file_mapping[key],
                'Rows': df.shape[0],
                'Columns': df.shape[1],
                'Memory_Usage_MB': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                'Missing_Values': df.isnull().sum().sum(),
                'Missing_Percentage': round((df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100, 2)
            })
        
        return pd.DataFrame(summary_data)
    
    def validate_data_relationships(self) -> Dict[str, any]:
        """
        Validate relationships between datasets (foreign keys).
        
        Returns:
            Dict: Validation results for key relationships
        """
        if not self.datasets:
            logger.warning("No datasets loaded. Call load_all_datasets() first.")
            return {}
        
        validation_results = {}
        
        try:
            # Check customer_id relationships
            if 'customers' in self.datasets and 'orders' in self.datasets:
                customers_ids = set(self.datasets['customers']['customer_id'])
                orders_customer_ids = set(self.datasets['orders']['customer_id'])
                
                validation_results['customer_orders_match'] = {
                    'customers_in_orders': len(orders_customer_ids.intersection(customers_ids)),
                    'customers_not_in_orders': len(customers_ids - orders_customer_ids),
                    'orders_without_customers': len(orders_customer_ids - customers_ids)
                }
            
            # Check order_id relationships
            if 'orders' in self.datasets and 'order_items' in self.datasets:
                orders_ids = set(self.datasets['orders']['order_id'])
                items_order_ids = set(self.datasets['order_items']['order_id'])
                
                validation_results['order_items_match'] = {
                    'orders_with_items': len(orders_ids.intersection(items_order_ids)),
                    'orders_without_items': len(orders_ids - items_order_ids),
                    'items_without_orders': len(items_order_ids - orders_ids)
                }
            
            # Check product_id relationships
            if 'products' in self.datasets and 'order_items' in self.datasets:
                products_ids = set(self.datasets['products']['product_id'])
                items_product_ids = set(self.datasets['order_items']['product_id'])
                
                validation_results['product_items_match'] = {
                    'products_with_sales': len(products_ids.intersection(items_product_ids)),
                    'products_without_sales': len(products_ids - items_product_ids),
                    'sales_without_products': len(items_product_ids - products_ids)
                }
                
        except KeyError as e:
            logger.error(f"Missing expected column in relationship validation: {str(e)}")
        except Exception as e:
            logger.error(f"Error in relationship validation: {str(e)}")
        
        return validation_results


def load_brazilian_ecommerce_data(data_dir: str = "data") -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """
    Convenience function to load all Brazilian e-commerce datasets.
    
    Args:
        data_dir (str): Path to data directory
        
    Returns:
        Tuple[Dict[str, pd.DataFrame], pd.DataFrame]: Datasets and summary
    """
    loader = DataLoader(data_dir)
    datasets = loader.load_all_datasets()
    summary = loader.get_dataset_summary()
    
    return datasets, summary


if __name__ == "__main__":
    # Example usage
    print("Loading Brazilian E-commerce Dataset...")
    
    # Load all datasets
    datasets, summary = load_brazilian_ecommerce_data()
    
    # Display summary
    print("\nDataset Summary:")
    print(summary.to_string(index=False))
    
    # Display first few rows of each dataset
    for name, df in datasets.items():
        print(f"\n{name.upper()} - First 3 rows:")
        print(df.head(3).to_string())