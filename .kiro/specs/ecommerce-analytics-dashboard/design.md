# Design Document

## Overview

This design outlines the technical architecture for a comprehensive e-commerce analytics dashboard that transforms raw Brazilian e-commerce data into actionable business insights. The project follows a collaborative development approach with continuous documentation, version control, and iterative feedback loops to ensure optimal results.

## Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Data      │───▶│  Data Pipeline  │───▶│   Dashboard     │
│   (CSV Files)   │    │   (Python/      │    │  (Streamlit)    │
│                 │    │   Pandas)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  GitHub Repo    │    │  Documentation  │    │   Deployment    │
│  (Version       │    │  & Case Study   │    │   (Streamlit    │
│   Control)      │    │   Reports       │    │    Cloud)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack
- **Data Processing:** Python, Pandas, NumPy
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Dashboard:** Streamlit
- **Version Control:** Git, GitHub
- **Deployment:** Streamlit Cloud
- **Documentation:** Markdown, Jupyter Notebooks

## Components and Interfaces

### 1. Data Processing Layer
**Purpose:** Clean, transform, and prepare data for analysis

**Components:**
- `data_loader.py`: Load and validate CSV files
- `data_cleaner.py`: Handle missing values, duplicates, data type conversions
- `feature_engineer.py`: Create derived features for analysis
- `data_validator.py`: Ensure data quality and consistency

**Interfaces:**
- Input: Raw CSV files from Brazilian e-commerce dataset
- Output: Clean, processed DataFrames ready for analysis

### 2. Analysis Layer
**Purpose:** Perform business-specific analytics to answer key questions

**Components:**
- `market_expansion.py`: Geographic and expansion analysis
- `customer_analytics.py`: CLV, segmentation, retention analysis
- `seasonal_analysis.py`: Time series and seasonal pattern analysis
- `payment_operations.py`: Payment behavior and operational metrics
- `predictive_models.py`: Forecasting and prediction models

**Interfaces:**
- Input: Processed DataFrames from data layer
- Output: Analysis results, insights, and visualizations

### 3. Dashboard Layer
**Purpose:** Present insights through interactive web interface

**Components:**
- `app.py`: Main Streamlit application
- `pages/`: Individual dashboard pages
  - `executive_overview.py`
  - `market_expansion.py`
  - `customer_analytics.py`
  - `seasonal_intelligence.py`
  - `payment_operations.py`
- `components/`: Reusable UI components
- `styling/`: CSS and theme configuration

**Interfaces:**
- Input: Analysis results and processed data
- Output: Interactive web dashboard

### 4. Documentation Layer
**Purpose:** Maintain comprehensive project documentation

**Components:**
- `reports/phase_reports/`: Step-by-step analysis documentation
- `reports/case_study.md`: Comprehensive business case study
- `reports/methodology.md`: Technical methodology documentation
- `notebooks/`: Jupyter notebooks for exploratory analysis

## Data Models

### Core Data Entities
```python
# Orders
orders_df: DataFrame
├── order_id (str): Unique order identifier
├── customer_id (str): Customer identifier
├── order_status (str): Order status
├── order_purchase_timestamp (datetime): Purchase date
├── order_delivered_customer_date (datetime): Delivery date
└── delivery_days (int): Calculated delivery time

# Customers
customers_df: DataFrame
├── customer_id (str): Unique customer identifier
├── customer_state (str): Brazilian state
├── customer_city (str): City name
└── customer_segment (str): RFM segment classification

# Products
products_df: DataFrame
├── product_id (str): Unique product identifier
├── product_category_name_english (str): Product category
├── product_weight_g (float): Product weight
└── product_dimensions (dict): Length, height, width

# Enhanced Analytics DataFrames
customer_metrics_df: DataFrame
├── customer_id (str)
├── total_orders (int)
├── total_revenue (float)
├── avg_order_value (float)
├── days_since_last_order (int)
├── customer_lifetime_value (float)
└── predicted_segment (str)
```

### Business Metrics Schema
```python
# KPI Metrics Structure
business_kpis = {
    'revenue': {
        'total_revenue': float,
        'monthly_growth': float,
        'avg_order_value': float
    },
    'customers': {
        'total_customers': int,
        'retention_rate': float,
        'clv_average': float
    },
    'operations': {
        'avg_delivery_days': float,
        'satisfaction_score': float,
        'on_time_delivery_rate': float
    }
}
```

## Error Handling

### Data Quality Issues
- **Missing Values:** Implement imputation strategies based on data type and business context
- **Outliers:** Use statistical methods (IQR, Z-score) to identify and handle outliers
- **Data Type Inconsistencies:** Automatic type conversion with validation
- **Foreign Key Mismatches:** Document and resolve relationship inconsistencies

### Dashboard Error Handling
- **Data Loading Errors:** Graceful fallback with user-friendly error messages
- **Visualization Errors:** Default to simplified charts if complex visualizations fail
- **Performance Issues:** Implement data caching and lazy loading
- **User Input Validation:** Validate filters and inputs before processing

## Testing Strategy

### Data Quality Testing
- **Unit Tests:** Test individual data processing functions
- **Integration Tests:** Validate end-to-end data pipeline
- **Data Validation Tests:** Ensure data quality metrics meet thresholds
- **Business Logic Tests:** Verify calculation accuracy for KPIs

### Dashboard Testing
- **Functional Tests:** Verify all dashboard features work correctly
- **Visual Tests:** Ensure charts render properly across different screen sizes
- **Performance Tests:** Validate dashboard load times and responsiveness
- **User Acceptance Tests:** Gather feedback on usability and insights clarity

## Collaborative Development Workflow

### Phase-Based Development
Each development phase includes:
1. **Planning Session:** Collaborative discussion of approach and expected outcomes
2. **Implementation:** Code development with regular check-ins
3. **Review Session:** Joint review of results and insights
4. **Documentation:** Comprehensive documentation of findings
5. **Git Commit:** Meaningful commit with descriptive message
6. **Feedback Loop:** Discussion of improvements and next steps

### Communication Protocol
- **Before Each Task:** Discuss approach, expected deliverables, and success criteria
- **During Implementation:** Regular progress updates and collaborative problem-solving
- **After Completion:** Joint review of results and planning for next phase
- **Documentation Reviews:** Collaborative editing of reports and insights

### Quality Assurance
- **Code Reviews:** Joint review of code quality and best practices
- **Insight Validation:** Collaborative verification of business insights
- **Dashboard UX Review:** Joint evaluation of user experience and design
- **Documentation Quality:** Collaborative editing for clarity and completeness

## Deployment Architecture

### Development Environment
- **Local Development:** Jupyter notebooks for exploration and analysis
- **Version Control:** Git with feature branches for major components
- **Testing Environment:** Local Streamlit server for dashboard testing

### Production Environment
- **Hosting:** Streamlit Cloud for public accessibility
- **Data Storage:** GitHub repository for data and code
- **Documentation:** GitHub Pages for comprehensive project documentation
- **Monitoring:** Basic error logging and performance monitoring

### CI/CD Pipeline
```
Local Development → GitHub Push → Streamlit Cloud Deployment
       ↓                ↓                    ↓
   Unit Tests    →  Code Review     →   Production Testing
```

## Dark Theme Design System

### Color Palette
```python
THEME_COLORS = {
    'primary_bg': '#1a1625',      # Dark purple background
    'secondary_bg': '#2a1f3d',    # Lighter purple for cards
    'card_bg': 'rgba(61, 47, 79, 0.8)',  # Translucent cards
    'text_primary': '#ffffff',     # White text
    'text_secondary': '#e0e0e0',   # Light gray text
    'accent_orange': '#ff9500',    # Revenue metrics
    'accent_blue': '#00d4ff',      # Customer metrics
    'accent_green': '#00e676',     # Performance metrics
    'accent_pink': '#e91e63',      # Alert/important metrics
    'accent_purple': '#9c27b0'     # Secondary metrics
}
```

### UI Components
- **KPI Cards:** Gradient backgrounds with neon accents
- **Charts:** Consistent color scheme with dark backgrounds
- **Navigation:** Sidebar with hover effects and active state highlighting
- **Interactive Elements:** Smooth transitions and hover effects
- **Typography:** Clean, readable fonts with proper contrast ratios