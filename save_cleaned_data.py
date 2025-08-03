"""
Save Cleaned Data Script

This script saves the cleaned datasets to CSV files for easy access
in subsequent analysis tasks.
"""

import os
import pandas as pd
from data_cleaner import clean_brazilian_ecommerce_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_cleaned_datasets(output_dir: str = "data/cleaned"):
    """
    Save cleaned datasets to CSV files.
    
    Args:
        output_dir (str): Directory to save cleaned datasets
    """
    logger.info("Loading and cleaning datasets...")
    
    # Load and clean data
    cleaned_datasets, cleaning_report = clean_brazilian_ecommerce_data()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each cleaned dataset
    logger.info(f"Saving cleaned datasets to {output_dir}/...")
    
    for dataset_name, df in cleaned_datasets.items():
        output_file = os.path.join(output_dir, f"cleaned_{dataset_name}.csv")
        df.to_csv(output_file, index=False)
        
        logger.info(f"Saved {dataset_name}: {len(df):,} rows, {len(df.columns)} columns -> {output_file}")
    
    # Save cleaning report
    report_file = os.path.join(output_dir, "cleaning_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(cleaning_report)
    
    logger.info(f"Saved cleaning report -> {report_file}")
    
    # Create a summary file
    summary_lines = []
    summary_lines.append("CLEANED DATASETS SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append("")
    
    total_size_mb = 0
    for dataset_name, df in cleaned_datasets.items():
        size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        total_size_mb += size_mb
        summary_lines.append(f"{dataset_name}:")
        summary_lines.append(f"  - Rows: {len(df):,}")
        summary_lines.append(f"  - Columns: {len(df.columns)}")
        summary_lines.append(f"  - Memory: {size_mb:.1f} MB")
        summary_lines.append(f"  - File: cleaned_{dataset_name}.csv")
        summary_lines.append("")
    
    summary_lines.append(f"Total Memory Usage: {total_size_mb:.1f} MB")
    summary_lines.append(f"Total Datasets: {len(cleaned_datasets)}")
    
    summary_file = os.path.join(output_dir, "datasets_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    logger.info(f"Saved datasets summary -> {summary_file}")
    
    return cleaned_datasets

def load_cleaned_datasets(input_dir: str = "data/cleaned"):
    """
    Load cleaned datasets from CSV files with proper data type restoration.
    
    Args:
        input_dir (str): Directory containing cleaned datasets
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary of cleaned datasets with proper types
    """
    if not os.path.exists(input_dir):
        logger.error(f"Cleaned data directory not found: {input_dir}")
        logger.info("Run save_cleaned_datasets() first to create cleaned data files")
        return {}
    
    logger.info(f"Loading cleaned datasets from {input_dir}/...")
    
    datasets = {}
    
    # Define data type conversions needed after CSV load
    type_conversions = {
        'orders': {
            'order_purchase_timestamp': 'datetime64[ns]',
            'order_approved_at': 'datetime64[ns]',
            'order_delivered_carrier_date': 'datetime64[ns]',
            'order_delivered_customer_date': 'datetime64[ns]',
            'order_estimated_delivery_date': 'datetime64[ns]',
            'order_status': 'category'
        },
        'customers': {
            'customer_city': 'category',
            'customer_state': 'category'
        },
        'products': {
            'product_category_name': 'category'
        },
        'order_payments': {
            'payment_type': 'category'
        },
        'order_items': {
            'seller_id': 'category',
            'shipping_limit_date': 'datetime64[ns]'
        },
        'order_reviews': {
            'review_comment_title': 'category',
            'review_creation_date': 'datetime64[ns]',
            'review_answer_timestamp': 'datetime64[ns]'
        },
        'geolocation': {
            'geolocation_city': 'category',
            'geolocation_state': 'category'
        },
        'sellers': {
            'seller_state': 'category'
        }
    }
    
    # Find all cleaned CSV files
    for filename in os.listdir(input_dir):
        if filename.startswith("cleaned_") and filename.endswith(".csv"):
            dataset_name = filename.replace("cleaned_", "").replace(".csv", "")
            file_path = os.path.join(input_dir, filename)
            
            try:
                df = pd.read_csv(file_path)
                
                # Apply data type conversions
                if dataset_name in type_conversions:
                    for col, dtype in type_conversions[dataset_name].items():
                        if col in df.columns:
                            try:
                                if 'datetime' in dtype:
                                    df[col] = pd.to_datetime(df[col], errors='coerce')
                                elif dtype == 'category':
                                    df[col] = df[col].astype('category')
                                else:
                                    df[col] = df[col].astype(dtype)
                            except Exception as e:
                                logger.warning(f"Failed to convert {col} to {dtype} in {dataset_name}: {str(e)}")
                
                datasets[dataset_name] = df
                logger.info(f"Loaded {dataset_name}: {len(df):,} rows, {len(df.columns)} columns")
            except Exception as e:
                logger.error(f"Failed to load {filename}: {str(e)}")
    
    logger.info(f"Successfully loaded {len(datasets)} cleaned datasets with proper data types")
    return datasets

if __name__ == "__main__":
    print("Saving cleaned datasets to files...")
    
    # Save cleaned data
    cleaned_datasets = save_cleaned_datasets()
    
    print(f"\n✅ Successfully saved {len(cleaned_datasets)} cleaned datasets!")
    print("📁 Location: data/cleaned/")
    print("📄 Files created:")
    
    for dataset_name in cleaned_datasets.keys():
        print(f"   • cleaned_{dataset_name}.csv")
    
    print("   • cleaning_report.txt")
    print("   • datasets_summary.txt")
    
    print("\n🔄 Testing reload...")
    
    # Test loading
    reloaded_datasets = load_cleaned_datasets()
    
    if len(reloaded_datasets) == len(cleaned_datasets):
        print("✅ Reload test successful!")
    else:
        print("❌ Reload test failed!")
    
    print("\n📊 Ready for feature engineering!")