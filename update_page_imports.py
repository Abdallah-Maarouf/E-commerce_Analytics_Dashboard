"""
Script to update all page files to use modern components
"""

import os
import re

# Define the old and new import patterns
old_imports = [
    "from dashboard.components.navigation import show_page_header",
    "from dashboard.components.ui_components import",
    "from dashboard.components.styling import get_theme_colors"
]

new_imports = """from dashboard.components.modern_styling import get_modern_theme_colors
from dashboard.components.modern_ui_components import create_modern_kpi_card, create_modern_chart_container, apply_modern_chart_theme, create_info_banner"""

# Page files to update
page_files = [
    "dashboard/pages/customer_analytics.py",
    "dashboard/pages/seasonal_intelligence.py", 
    "dashboard/pages/payment_operations.py"
]

def update_file_imports(file_path):
    """Update imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace old imports with new ones
        # Pattern to match the old import block
        old_pattern = r'from dashboard\.components\.navigation import.*?\nfrom dashboard\.components\.styling import get_theme_colors'
        
        if re.search(old_pattern, content, re.DOTALL):
            content = re.sub(old_pattern, new_imports, content, flags=re.DOTALL)
            
            # Also replace function calls
            content = content.replace('get_theme_colors()', 'get_modern_theme_colors()')
            content = content.replace('show_page_header(', '# show_page_header(')
            content = content.replace('create_section_divider(', '# create_section_divider(')
            content = content.replace('create_metric_card(', 'create_modern_kpi_card(')
            content = content.replace('create_info_card(', '# create_info_card(')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated {file_path}")
        else:
            print(f"⚠️ No matching pattern found in {file_path}")
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def main():
    """Update all page files"""
    print("🔄 Updating page files to use modern components...")
    
    for file_path in page_files:
        if os.path.exists(file_path):
            update_file_imports(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n✨ Update complete! Please review the files and make manual adjustments as needed.")
    print("\nNext steps:")
    print("1. Test the modern_ui_test.py file")
    print("2. Run your main app.py")
    print("3. Check each page for any remaining issues")

if __name__ == "__main__":
    main()