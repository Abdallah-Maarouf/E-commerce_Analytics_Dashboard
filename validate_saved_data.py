"""
Validate Saved Cleaned Data

This script validates the cleaned data that was saved to CSV files
to ensure data integrity is maintained after file operations.
"""

from save_cleaned_data import load_cleaned_datasets
from data_validator import validate_cleaned_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to validate saved cleaned data."""
    print("🔍 Validating saved cleaned datasets...")
    
    try:
        # Load cleaned datasets from files
        print("\n📂 Loading cleaned datasets from files...")
        cleaned_datasets = load_cleaned_datasets()
        
        if not cleaned_datasets:
            print("❌ No cleaned datasets found. Run save_cleaned_data.py first.")
            return
        
        print(f"✅ Loaded {len(cleaned_datasets)} datasets from files")
        
        # Run validation
        print("\n🔬 Running comprehensive validation...")
        validation_passed, validation_report = validate_cleaned_data(cleaned_datasets)
        
        # Display validation report
        print("\n" + validation_report)
        
        # Save validation report for saved data
        import os
        os.makedirs('data/cleaned', exist_ok=True)
        
        with open('data/cleaned/validation_report_saved_data.txt', 'w', encoding='utf-8') as f:
            f.write(validation_report)
        
        if validation_passed:
            print(f"\n✅ VALIDATION PASSED! Saved cleaned data is ready for analysis.")
            print("🎯 Data integrity maintained after file save/load operations")
        else:
            print(f"\n❌ VALIDATION FAILED! Issues found in saved data.")
            print("⚠️  Check validation report for details")
        
        print(f"📄 Validation report saved to 'data/cleaned/validation_report_saved_data.txt'")
        
        # Quick data integrity check
        print("\n📊 QUICK DATA INTEGRITY CHECK:")
        for name, df in cleaned_datasets.items():
            missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            print(f"   • {name}: {len(df):,} rows, {len(df.columns)} cols, {missing_pct:.2f}% missing")
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()