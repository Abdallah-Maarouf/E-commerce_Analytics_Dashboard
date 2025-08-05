"""
Simple Dashboard Testing Suite
Tests core functionality without unicode issues
"""

import sys
import os
import pandas as pd
import traceback
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_core_functionality():
    """Test core dashboard functionality"""
    print("Testing Core Dashboard Functionality...")
    results = []
    
    # Test 1: Data Loading
    try:
        from data_loader import load_all_data
        data = load_all_data()
        if data and len(data) > 0:
            results.append("PASS: Data loading successful")
        else:
            results.append("FAIL: Data loading failed - no data returned")
    except Exception as e:
        results.append(f"FAIL: Data loading error - {str(e)}")
    
    # Test 2: Dashboard Components
    try:
        from dashboard.components.styling import get_theme_colors
        from dashboard.components.navigation import setup_sidebar_navigation
        from dashboard.components.ui_components import show_loading_state
        results.append("PASS: Dashboard components imported successfully")
    except Exception as e:
        results.append(f"FAIL: Dashboard components error - {str(e)}")
    
    # Test 3: Dashboard Pages
    page_tests = []
    pages = [
        'dashboard.pages.executive_overview',
        'dashboard.pages.market_expansion', 
        'dashboard.pages.customer_analytics',
        'dashboard.pages.seasonal_intelligence',
        'dashboard.pages.payment_operations'
    ]
    
    for page in pages:
        try:
            module = __import__(page, fromlist=[page.split('.')[-1]])
            if hasattr(module, 'render'):
                page_tests.append(f"PASS: {page.split('.')[-1]} page OK")
            else:
                page_tests.append(f"FAIL: {page.split('.')[-1]} missing render function")
        except Exception as e:
            page_tests.append(f"FAIL: {page.split('.')[-1]} import error - {str(e)}")
    
    results.extend(page_tests)
    
    # Test 4: Analysis Modules
    analysis_modules = ['market_expansion', 'customer_analytics', 'seasonal_analysis', 'payment_operations']
    for module_name in analysis_modules:
        try:
            module = __import__(module_name)
            results.append(f"PASS: {module_name} analysis module imported")
        except Exception as e:
            results.append(f"FAIL: {module_name} analysis module error - {str(e)}")
    
    return results

def test_data_integrity():
    """Test data integrity and calculations"""
    print("Testing Data Integrity...")
    results = []
    
    try:
        from data_loader import load_all_data
        data = load_all_data()
        
        # Check if key datasets exist
        key_datasets = ['orders', 'customers', 'order_items', 'products']
        for dataset in key_datasets:
            if dataset in data and not data[dataset].empty:
                results.append(f"PASS: {dataset} dataset loaded and not empty")
            else:
                results.append(f"FAIL: {dataset} dataset missing or empty")
        
        # Basic data validation
        if 'orders' in data:
            orders = data['orders']
            if len(orders) > 0:
                results.append("PASS: Orders data contains records")
            else:
                results.append("FAIL: Orders data is empty")
        
    except Exception as e:
        results.append(f"FAIL: Data integrity test error - {str(e)}")
    
    return results

def test_app_structure():
    """Test main app structure"""
    print("Testing App Structure...")
    results = []
    
    try:
        # Test main app file
        if os.path.exists('app.py'):
            results.append("PASS: Main app.py file exists")
        else:
            results.append("FAIL: Main app.py file missing")
        
        # Test dashboard directory structure
        required_dirs = ['dashboard', 'dashboard/components', 'dashboard/pages']
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                results.append(f"PASS: {dir_path} directory exists")
            else:
                results.append(f"FAIL: {dir_path} directory missing")
        
        # Test required files
        required_files = [
            'dashboard/components/styling.py',
            'dashboard/components/navigation.py',
            'dashboard/components/ui_components.py'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                results.append(f"PASS: {file_path} exists")
            else:
                results.append(f"FAIL: {file_path} missing")
                
    except Exception as e:
        results.append(f"FAIL: App structure test error - {str(e)}")
    
    return results

def run_all_tests():
    """Run all tests and generate report"""
    print("=" * 50)
    print("Dashboard Quality Assurance Testing")
    print("=" * 50)
    
    all_results = []
    
    # Run test suites
    test_suites = [
        test_core_functionality,
        test_data_integrity,
        test_app_structure
    ]
    
    for test_suite in test_suites:
        try:
            results = test_suite()
            all_results.extend(results)
            print()
        except Exception as e:
            all_results.append(f"FAIL: Test suite {test_suite.__name__} crashed - {str(e)}")
    
    # Generate summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = len([r for r in all_results if r.startswith("PASS")])
    failed = len([r for r in all_results if r.startswith("FAIL")])
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {len(all_results)}")
    
    # Print all results
    print("\nDetailed Results:")
    print("-" * 30)
    for result in all_results:
        print(result)
    
    # Save results to file
    try:
        with open('test_results.txt', 'w', encoding='utf-8') as f:
            f.write("Dashboard Quality Assurance Test Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for result in all_results:
                f.write(result + "\n")
            
            f.write(f"\nSummary:\n")
            f.write(f"Passed: {passed}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Total: {len(all_results)}\n")
        
        print(f"\nResults saved to test_results.txt")
    except Exception as e:
        print(f"Could not sa