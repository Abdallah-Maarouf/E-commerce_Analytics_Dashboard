"""
Data Quality Check Script for Brazilian E-commerce Dataset

This script performs comprehensive data quality checks and generates
detailed reports about the dataset's condition.
"""

import pandas as pd
import numpy as np
from data_loader import DataLoader, load_brazilian_ecommerce_data
import os
from datetime import datetime

class DataQualityChecker:
    """
    Comprehensive data quality checker for the Brazilian E-commerce dataset.
    """
    
    def __init__(self, datasets):
        """
        Initialize with loaded datasets.
        
        Args:
            datasets (dict): Dictionary of loaded DataFrames
        """
        self.datasets = datasets
        self.quality_issues = {}
        
    def check_missing_values(self):
        """Check for missing values across all datasets."""
        missing_analysis = []
        
        for name, df in self.datasets.items():
            missing_counts = df.isnull().sum()
            missing_percentages = (missing_counts / len(df)) * 100
            
            for column in df.columns:
                if missing_counts[column] > 0:
                    missing_analysis.append({
                        'Dataset': name,
                        'Column': column,
                        'Missing_Count': missing_counts[column],
                        'Missing_Percentage': round(missing_percentages[column], 2),
                        'Total_Rows': len(df),
                        'Severity': self._classify_missing_severity(missing_percentages[column])
                    })
        
        return pd.DataFrame(missing_analysis).sort_values('Missing_Percentage', ascending=False)
    
    def check_duplicates(self):
        """Check for duplicate records in all datasets."""
        duplicate_analysis = []
        
        for name, df in self.datasets.items():
            total_rows = len(df)
            duplicate_rows = df.duplicated().sum()
            duplicate_percentage = (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0
            
            duplicate_analysis.append({
                'Dataset': name,
                'Total_Rows': total_rows,
                'Duplicate_Rows': duplicate_rows,
                'Duplicate_Percentage': round(duplicate_percentage, 2),
                'Unique_Rows': total_rows - duplicate_rows,
                'Severity': self._classify_duplicate_severity(duplicate_percentage)
            })
        
        return pd.DataFrame(duplicate_analysis).sort_values('Duplicate_Percentage', ascending=False)
    
    def check_data_types(self):
        """Analyze data types and identify potential issues."""
        type_analysis = []
        
        for name, df in self.datasets.items():
            for column in df.columns:
                dtype = str(df[column].dtype)
                unique_count = df[column].nunique()
                sample_values = df[column].dropna().head(5).tolist()
                
                # Check if column might need type conversion
                needs_conversion = self._check_type_conversion_needed(df[column], column)
                
                type_analysis.append({
                    'Dataset': name,
                    'Column': column,
                    'Current_Type': dtype,
                    'Unique_Values': unique_count,
                    'Sample_Values': str(sample_values)[:100] + '...' if len(str(sample_values)) > 100 else str(sample_values),
                    'Needs_Conversion': needs_conversion,
                    'Suggested_Type': self._suggest_type_conversion(df[column], column)
                })
        
        return pd.DataFrame(type_analysis)
    
    def check_value_ranges(self):
        """Check for outliers and unusual value ranges in numerical columns."""
        range_analysis = []
        
        for name, df in self.datasets.items():
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numerical_cols:
                if df[col].notna().sum() > 0:  # Only analyze if there are non-null values
                    stats = df[col].describe()
                    q1 = stats['25%']
                    q3 = stats['75%']
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col].count()
                    outlier_percentage = (outliers / df[col].notna().sum()) * 100
                    
                    range_analysis.append({
                        'Dataset': name,
                        'Column': col,
                        'Min': stats['min'],
                        'Max': stats['max'],
                        'Mean': round(stats['mean'], 2),
                        'Std': round(stats['std'], 2),
                        'Outliers': outliers,
                        'Outlier_Percentage': round(outlier_percentage, 2),
                        'Severity': self._classify_outlier_severity(outlier_percentage)
                    })
        
        return pd.DataFrame(range_analysis)
    
    def check_foreign_key_integrity(self):
        """Check foreign key relationships between datasets."""
        integrity_issues = []
        
        # Define key relationships to check
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
                
                orphaned_records = len(child_keys - parent_keys)
                orphaned_percentage = (orphaned_records / len(child_keys)) * 100 if len(child_keys) > 0 else 0
                
                integrity_issues.append({
                    'Parent_Table': parent_table,
                    'Parent_Key': parent_key,
                    'Child_Table': child_table,
                    'Child_Key': child_key,
                    'Parent_Unique_Keys': len(parent_keys),
                    'Child_Unique_Keys': len(child_keys),
                    'Orphaned_Records': orphaned_records,
                    'Orphaned_Percentage': round(orphaned_percentage, 2),
                    'Integrity_Status': 'GOOD' if orphaned_records == 0 else 'ISSUES'
                })
        
        return pd.DataFrame(integrity_issues)
    
    def _classify_missing_severity(self, percentage):
        """Classify missing value severity."""
        if percentage == 0:
            return 'NONE'
        elif percentage < 5:
            return 'LOW'
        elif percentage < 20:
            return 'MEDIUM'
        elif percentage < 50:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _classify_duplicate_severity(self, percentage):
        """Classify duplicate severity."""
        if percentage == 0:
            return 'NONE'
        elif percentage < 1:
            return 'LOW'
        elif percentage < 5:
            return 'MEDIUM'
        elif percentage < 20:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _classify_outlier_severity(self, percentage):
        """Classify outlier severity."""
        if percentage == 0:
            return 'NONE'
        elif percentage < 5:
            return 'LOW'
        elif percentage < 10:
            return 'MEDIUM'
        elif percentage < 20:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _check_type_conversion_needed(self, series, column_name):
        """Check if a column needs type conversion."""
        # Check for date columns
        if any(keyword in column_name.lower() for keyword in ['date', 'time', 'timestamp']):
            return True
        
        # Check for categorical columns that might be stored as objects
        if series.dtype == 'object' and series.nunique() < len(series) * 0.1:
            return True
        
        return False
    
    def _suggest_type_conversion(self, series, column_name):
        """Suggest appropriate type conversion."""
        if any(keyword in column_name.lower() for keyword in ['date', 'time', 'timestamp']):
            return 'datetime64'
        
        if series.dtype == 'object' and series.nunique() < len(series) * 0.1:
            return 'category'
        
        return str(series.dtype)
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive data quality report."""
        print("Generating comprehensive data quality report...")
        
        # Run all checks
        missing_df = self.check_missing_values()
        duplicates_df = self.check_duplicates()
        types_df = self.check_data_types()
        ranges_df = self.check_value_ranges()
        integrity_df = self.check_foreign_key_integrity()
        
        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("COMPREHENSIVE DATA QUALITY REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Dataset overview
        report_lines.append("📊 DATASET OVERVIEW:")
        total_rows = sum(df.shape[0] for df in self.datasets.values())
        total_cols = sum(df.shape[1] for df in self.datasets.values())
        report_lines.append(f"   • Total datasets: {len(self.datasets)}")
        report_lines.append(f"   • Total rows: {total_rows:,}")
        report_lines.append(f"   • Total columns: {total_cols}")
        report_lines.append("")
        
        # Missing values summary
        report_lines.append("🔍 MISSING VALUES ANALYSIS:")
        if not missing_df.empty:
            critical_missing = missing_df[missing_df['Severity'] == 'CRITICAL']
            high_missing = missing_df[missing_df['Severity'] == 'HIGH']
            report_lines.append(f"   • Critical issues (>50% missing): {len(critical_missing)}")
            report_lines.append(f"   • High issues (20-50% missing): {len(high_missing)}")
            
            if len(critical_missing) > 0:
                report_lines.append("   • Critical columns:")
                for _, row in critical_missing.head(5).iterrows():
                    report_lines.append(f"     - {row['Dataset']}.{row['Column']}: {row['Missing_Percentage']:.1f}%")
        else:
            report_lines.append("   • No missing values found!")
        report_lines.append("")
        
        # Duplicates summary
        report_lines.append("🔄 DUPLICATE ANALYSIS:")
        high_duplicates = duplicates_df[duplicates_df['Severity'].isin(['HIGH', 'CRITICAL'])]
        if len(high_duplicates) > 0:
            report_lines.append(f"   • Datasets with significant duplicates: {len(high_duplicates)}")
            for _, row in high_duplicates.iterrows():
                report_lines.append(f"     - {row['Dataset']}: {row['Duplicate_Percentage']:.1f}% ({row['Duplicate_Rows']:,} rows)")
        else:
            report_lines.append("   • No significant duplicate issues found")
        report_lines.append("")
        
        # Foreign key integrity
        report_lines.append("🔗 FOREIGN KEY INTEGRITY:")
        integrity_issues = integrity_df[integrity_df['Integrity_Status'] == 'ISSUES']
        if len(integrity_issues) > 0:
            report_lines.append(f"   • Relationships with issues: {len(integrity_issues)}")
            for _, row in integrity_issues.iterrows():
                report_lines.append(f"     - {row['Parent_Table']}.{row['Parent_Key']} → {row['Child_Table']}.{row['Child_Key']}: {row['Orphaned_Records']:,} orphaned records")
        else:
            report_lines.append("   • All foreign key relationships are intact")
        report_lines.append("")
        
        # Recommendations
        report_lines.append("💡 RECOMMENDATIONS:")
        recommendations = self._generate_recommendations(missing_df, duplicates_df, integrity_df)
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"   {i}. {rec}")
        
        return "\n".join(report_lines), {
            'missing': missing_df,
            'duplicates': duplicates_df,
            'types': types_df,
            'ranges': ranges_df,
            'integrity': integrity_df
        }
    
    def _generate_recommendations(self, missing_df, duplicates_df, integrity_df):
        """Generate actionable recommendations based on findings."""
        recommendations = []
        
        # Missing value recommendations
        if not missing_df.empty:
            critical_missing = missing_df[missing_df['Severity'] == 'CRITICAL']
            if len(critical_missing) > 0:
                recommendations.append("Address critical missing value issues (>50% missing) - consider if these columns are necessary")
            
            high_missing = missing_df[missing_df['Severity'] == 'HIGH']
            if len(high_missing) > 0:
                recommendations.append("Implement imputation strategies for high missing value columns (20-50% missing)")
        
        # Duplicate recommendations
        high_duplicates = duplicates_df[duplicates_df['Severity'].isin(['HIGH', 'CRITICAL'])]
        if len(high_duplicates) > 0:
            recommendations.append("Remove duplicate records, especially from geolocation dataset")
        
        # Foreign key recommendations
        integrity_issues = integrity_df[integrity_df['Integrity_Status'] == 'ISSUES']
        if len(integrity_issues) > 0:
            recommendations.append("Investigate and resolve foreign key integrity issues")
        
        # General recommendations
        recommendations.extend([
            "Convert date columns to proper datetime format",
            "Consider converting categorical columns to category dtype for memory efficiency",
            "Create data validation rules for future data ingestion",
            "Implement data quality monitoring for ongoing data updates"
        ])
        
        return recommendations


def main():
    """Main function to run data quality checks."""
    print("Starting comprehensive data quality check...")
    
    # Load datasets
    datasets, summary = load_brazilian_ecommerce_data()
    
    if not datasets:
        print("❌ No datasets loaded. Please check data directory and files.")
        return
    
    print(f"✅ Loaded {len(datasets)} datasets successfully")
    
    # Initialize quality checker
    checker = DataQualityChecker(datasets)
    
    # Generate comprehensive report
    report, detailed_results = checker.generate_comprehensive_report()
    
    # Display report
    print("\n" + report)
    
    # Save report to file
    os.makedirs('reports', exist_ok=True)
    
    with open('reports/comprehensive_data_quality_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save detailed results to CSV files
    for check_name, df in detailed_results.items():
        if not df.empty:
            df.to_csv(f'reports/quality_check_{check_name}.csv', index=False)
    
    print(f"\n📄 Reports saved to 'reports/' directory")
    print("   • comprehensive_data_quality_report.txt")
    for check_name, df in detailed_results.items():
        if not df.empty:
            print(f"   • quality_check_{check_name}.csv")


if __name__ == "__main__":
    main()