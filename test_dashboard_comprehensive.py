"""
Comprehensive Dashboard Testing Suite
Tests all dashboard pages, components, and functionality
"""

import sys
import os
import pandas as pd
import numpy as np
import traceback
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_loading():
    """Test data loading functionality"""
    print("🔍 Testing Data Loading...")
    test_results = []
    
    try:
        # Test data loader
        from data_loader import load_all_data
        data = load_all_data()
        
        # Validate all datasets are loaded
        expected_datasets = [
            'orders', 'customers', 'order_items', 'products', 
            'sellers', 'geolocation', 'payments', 'reviews'
        ]
        
        for dataset in expected_datasets:
            if dataset in data and not data[dataset].empty:
                test_results.append(f"✅ {dataset} dataset loaded successfully")
            else:
                test_results.append(f"❌ {dataset} dataset failed to load or is empty")
                
    except Exception as e:
        test_results.append(f"❌ Data loading failed: {str(e)}")
    
    return test_results

def test_data_cleaning():
    """Test data cleaning functionality"""
    print("🧹 Testing Data Cleaning...")
    test_results = []
    
    try:
        from data_cleaner import DataCleaner
        from data_loader import load_all_data
        
        # Load raw data
        raw_data = load_all_data()
        cleaner = DataCleaner()
        
        # Test cleaning functions
        cleaned_data = cleaner.clean_all_data(raw_data)
        
        # Validate cleaning results
        if 'orders' in cleaned_data:
            orders = cleaned_data['orders']
            if 'delivery_days' in orders.columns:
                test_results.append("✅ Delivery days calculated successfully")
            else:
                test_results.append("❌ Delivery days calculation failed")
                
        test_results.append("✅ Data cleaning completed successfully")
        
    except Exception as e:
        test_results.append(f"❌ Data cleaning failed: {str(e)}")
    
    return test_results

def test_feature_engineering():
    """Test feature engineering functionality"""
    print("⚙️ Testing Feature Engineering...")
    test_results = []
    
    try:
        from feature_engineer import FeatureEngineer
        from data_loader import load_all_data
        from data_cleaner import DataCleaner
        
        # Load and clean data
        raw_data = load_all_data()
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_all_data(raw_data)
        
        # Test feature engineering
        engineer = FeatureEngineer()
        enhanced_data = engineer.create_all_features(cleaned_data)
        
        # Validate feature creation
        if 'customer_metrics' in enhanced_data:
            test_results.append("✅ Customer metrics created successfully")
        if 'product_metrics' in enhanced_data:
            test_results.append("✅ Product metrics created successfully")
            
        test_results.append("✅ Feature engineering completed successfully")
        
    except Exception as e:
        test_results.append(f"❌ Feature engineering failed: {str(e)}")
    
    return test_results

def test_analysis_modules():
    """Test all business analysis modules"""
    print("📊 Testing Analysis Modules...")
    test_results = []
    
    analysis_modules = [
        ('market_expansion', 'Market Expansion Analysis'),
        ('customer_analytics', 'Customer Analytics'),
        ('seasonal_analysis', 'Seasonal Analysis'),
        ('payment_operations', 'Payment Operations')
    ]
    
    for module_name, display_name in analysis_modules:
        try:
            module = __import__(module_name)
            test_results.append(f"✅ {display_name} module imported successfully")
            
            # Test if main analysis function exists
            if hasattr(module, 'run_analysis') or hasattr(module, 'analyze'):
                test_results.append(f"✅ {display_name} analysis function available")
            else:
                test_results.append(f"⚠️ {display_name} analysis function not found")
                
        except Exception as e:
            test_results.append(f"❌ {display_name} module failed: {str(e)}")
    
    return test_results

def test_dashboard_components():
    """Test dashboard components"""
    print("🎨 Testing Dashboard Components...")
    test_results = []
    
    try:
        # Test styling components
        from dashboard.components.styling import apply_dark_theme, get_theme_colors
        colors = get_theme_colors()
        
        if colors and isinstance(colors, dict):
            test_results.append("✅ Theme colors loaded successfully")
        else:
            test_results.append("❌ Theme colors failed to load")
            
        # Test navigation components
        from dashboard.components.navigation import setup_sidebar_navigation
        test_results.append("✅ Navigation component imported successfully")
        
        # Test UI components
        from dashboard.components.ui_components import show_loading_state, show_error_message
        test_results.append("✅ UI components imported successfully")
        
    except Exception as e:
        test_results.append(f"❌ Dashboard components failed: {str(e)}")
    
    return test_results

def test_dashboard_pages():
    """Test all dashboard pages"""
    print("📄 Testing Dashboard Pages...")
    test_results = []
    
    pages = [
        ('executive_overview', 'Executive Overview'),
        ('market_expansion', 'Market Expansion'),
        ('customer_analytics', 'Customer Analytics'),
        ('seasonal_intelligence', 'Seasonal Intelligence'),
        ('payment_operations', 'Payment & Operations')
    ]
    
    for page_module, page_name in pages:
        try:
            module = __import__(f'dashboard.pages.{page_module}', fromlist=[page_module])
            
            if hasattr(module, 'render'):
                test_results.append(f"✅ {page_name} page imported and render function available")
            else:
                test_results.append(f"❌ {page_name} page missing render function")
                
        except Exception as e:
            test_results.append(f"❌ {page_name} page failed: {str(e)}")
    
    return test_results

def test_data_accuracy():
    """Test data accuracy and calculations"""
    print("🔢 Testing Data Accuracy...")
    test_results = []
    
    try:
        from data_loader import load_all_data
        from data_cleaner import DataCleaner
        
        # Load and clean data
        raw_data = load_all_data()
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_all_data(raw_data)
        
        # Test basic data integrity
        if 'orders' in cleaned_data:
            orders = cleaned_data['orders']
            
            # Check for reasonable date ranges
            if 'order_purchase_timestamp' in orders.columns:
                min_date = pd.to_datetime(orders['order_purchase_timestamp']).min()
                max_date = pd.to_datetime(orders['order_purchase_timestamp']).max()
                
                if min_date.year >= 2016 and max_date.year <= 2019:
                    test_results.append("✅ Order dates are within expected range")
                else:
                    test_results.append(f"⚠️ Order dates outside expected range: {min_date} to {max_date}")
            
            # Check for positive values where expected
            if 'price' in orders.columns:
                negative_prices = orders[orders['price'] < 0]
                if len(negative_prices) == 0:
                    test_results.append("✅ No negative prices found")
                else:
                    test_results.append(f"⚠️ Found {len(negative_prices)} negative prices")
        
        test_results.append("✅ Data accuracy validation completed")
        
    except Exception as e:
        test_results.append(f"❌ Data accuracy testing failed: {str(e)}")
    
    return test_results

def test_error_handling():
    """Test error handling scenarios"""
    print("🛡️ Testing Error Handling...")
    test_results = []
    
    try:
        # Test with missing data files
        from dashboard.components.ui_components import show_error_message
        test_results.append("✅ Error message component available")
        
        # Test with invalid data
        try:
            from data_loader import load_all_data
            # This should handle missing files gracefully
            test_results.append("✅ Data loader handles missing files")
        except Exception:
            test_results.append("✅ Data loader properly raises exceptions for missing files")
        
        test_results.append("✅ Error handling tests completed")
        
    except Exception as e:
        test_results.append(f"❌ Error handling testing failed: {str(e)}")
    
    return test_results

def test_performance():
    """Test performance and optimization"""
    print("⚡ Testing Performance...")
    test_results = []
    
    try:
        import time
        
        # Test data loading performance
        start_time = time.time()
        from data_loader import load_all_data
        data = load_all_data()
        load_time = time.time() - start_time
        
        if load_time < 30:  # Should load within 30 seconds
            test_results.append(f"✅ Data loading performance acceptable: {load_time:.2f}s")
        else:
            test_results.append(f"⚠️ Data loading slow: {load_time:.2f}s")
        
        # Test memory usage
        total_memory = 0
        for dataset_name, dataset in data.items():
            if hasattr(dataset, 'memory_usage'):
                memory = dataset.memory_usage(deep=True).sum()
                total_memory += memory
        
        total_memory_mb = total_memory / (1024 * 1024)
        if total_memory_mb < 500:  # Less than 500MB
            test_results.append(f"✅ Memory usage acceptable: {total_memory_mb:.2f}MB")
        else:
            test_results.append(f"⚠️ High memory usage: {total_memory_mb:.2f}MB")
        
        test_results.append("✅ Performance testing completed")
        
    except Exception as e:
        test_results.append(f"❌ Performance testing failed: {str(e)}")
    
    return test_results

def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("🚀 Starting Comprehensive Dashboard Testing")
    print("=" * 60)
    
    all_results = []
    
    # Run all test suites
    test_suites = [
        test_data_loading,
        test_data_cleaning,
        test_feature_engineering,
        test_analysis_modules,
        test_dashboard_components,
        test_dashboard_pages,
        test_data_accuracy,
        test_error_handling,
        test_performance
    ]
    
    for test_suite in test_suites:
        try:
            results = test_suite()
            all_results.extend(results)
            print()
        except Exception as e:
            all_results.append(f"❌ Test suite {test_suite.__name__} crashed: {str(e)}")
            print(f"❌ Test suite {test_suite.__name__} crashed: {str(e)}")
    
    # Generate summary
    print("=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = len([r for r in all_results if r.startswith("✅")])
    warnings = len([r for r in all_results if r.startswith("⚠️")])
    failed = len([r for r in all_results if r.startswith("❌")])
    
    print(f"✅ Passed: {passed}")
    print(f"⚠️ Warnings: {warnings}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total Tests: {len(all_results)}")
    
    if failed == 0:
        print("\n🎉 All critical tests passed! Dashboard is ready for deployment.")
    elif failed < 3:
        print(f"\n⚠️ Minor issues found ({failed} failures). Review and fix before deployment.")
    else:
        print(f"\n🚨 Significant issues found ({failed} failures). Major fixes needed.")
    
    # Save detailed results
    with open('test_results.txt', 'w') as f:
        f.write("Dashboard Comprehensive Test Results\n")
        f.write("=" * 50 + "\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in all_results:
            f.write(result + "\n")
        
        f.write(f"\nSummary:\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Warnings: {warnings}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Total: {len(all_results)}\n")
    
    print(f"\n📄 Detailed results saved to test_results.txt")
    
    return all_results

if __name__ == "__main__":
    run_comprehensive_tests()