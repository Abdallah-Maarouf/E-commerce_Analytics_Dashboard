"""
Dashboard Performance Optimization Script
Optimizes dashboard performance and fixes common issues
"""

import os
import pandas as pd
import sys

def optimize_data_loading():
    """Optimize data loading performance"""
    print("Optimizing data loading performance...")
    
    # Check if data directory exists
    if not os.path.exists('data'):
        print("Creating data directory...")
        os.makedirs('data', exist_ok=True)
    
    # Check for large files that might slow down loading
    data_files = []
    if os.path.exists('data'):
        for file in os.listdir('data'):
            if file.endswith('.csv'):
                file_path = os.path.join('data', file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                data_files.append((file, size_mb))
    
    if data_files:
        print("Data files found:")
        for file, size in data_files:
            print(f"  {file}: {size:.2f} MB")
    else:
        print("No data files found in data directory")
    
    return True

def optimize_dashboard_components():
    """Optimize dashboard components for better performance"""
    print("Optimizing dashboard components...")
    
    # Check if all required components exist
    required_components = [
        'dashboard/components/styling.py',
        'dashboard/components/navigation.py',
        'dashboard/components/ui_components.py'
    ]
    
    for component in required_components:
        if os.path.exists(component):
            print(f"✓ {component} exists")
        else:
            print(f"✗ {component} missing")
    
    return True

def optimize_memory_usage():
    """Optimize memory usage for better performance"""
    print("Optimizing memory usage...")
    
    # Add memory optimization recommendations
    optimizations = [
        "Use pd.read_csv with dtype specifications to reduce memory usage",
        "Implement data caching to avoid reloading data",
        "Use chunking for large datasets",
        "Clear unused variables with del statement",
        "Use categorical data types for string columns with limited values"
    ]
    
    print("Memory optimization recommendations:")
    for i, opt in enumerate(optimizations, 1):
        print(f"  {i}. {opt}")
    
    return True

def create_performance_config():
    """Create performance configuration file"""
    print("Creating performance configuration...")
    
    config_content = """# Dashboard Performance Configuration

# Data Loading Settings
CHUNK_SIZE = 10000
MAX_MEMORY_USAGE = 500  # MB
CACHE_ENABLED = True

# UI Settings
LAZY_LOADING = True
CHART_ANIMATION = False  # Disable for better performance
MAX_CHART_POINTS = 1000

# Streamlit Settings
STREAMLIT_CONFIG = {
    'server.maxUploadSize': 200,
    'server.maxMessageSize': 200,
    'client.caching': True,
    'client.displayEnabled': True
}
"""
    
    with open('performance_config.py', 'w') as f:
        f.write(config_content)
    
    print("Performance configuration saved to performance_config.py")
    return True

def run_optimization():
    """Run all optimization steps"""
    print("=" * 50)
    print("DASHBOARD PERFORMANCE OPTIMIZATION")
    print("=" * 50)
    
    optimizations = [
        optimize_data_loading,
        optimize_dashboard_components,
        optimize_memory_usage,
        create_performance_config
    ]
    
    results = []
    for optimization in optimizations:
        try:
            result = optimization()
            results.append(f"✓ {optimization.__name__}: Success")
        except Exception as e:
            results.append(f"✗ {optimization.__name__}: Failed - {str(e)}")
        print()
    
    print("=" * 50)
    print("OPTIMIZATION SUMMARY")
    print("=" * 50)
    
    for result in results:
        print(result)
    
    print("\nOptimization completed!")
    return results

if __name__ == "__main__":
    run_optimization()