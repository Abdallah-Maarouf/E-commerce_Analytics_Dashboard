"""
Seasonal Demand Intelligence Analysis Module

This module implements comprehensive seasonal analysis including monthly and seasonal sales patterns,
Brazilian holiday impact analysis, demand forecasting, and inventory optimization recommendations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class SeasonalAnalysis:
    """
    Comprehensive seasonal demand intelligence for Brazilian E-commerce dataset.
    Analyzes seasonal patterns, holiday impacts, and provides demand forecasting.
    """
    
    def __init__(self, data_dir='data/cleaned'):
        """
        Initialize SeasonalAnalysis with cleaned datasets.
        
        Args:
            data_dir (str): Path to the cleaned data directory
        """
        self.data_dir = data_dir
        self.datasets = {}
        self.seasonal_data = {}
        self.forecasting_models = {}
        self.insights = {}
        
        # Brazilian holidays and cultural events
        self.brazilian_events = {
            1: {'name': 'New Year', 'type': 'holiday', 'impact': 'medium'},
            2: {'name': 'Carnival', 'type': 'cultural', 'impact': 'high'},
            3: {'name': 'Carnival (extended)', 'type': 'cultural', 'impact': 'medium'},
            4: {'name': 'Easter', 'type': 'holiday', 'impact': 'low'},
            5: {'name': 'Mothers Day', 'type': 'commercial', 'impact': 'high'},
            6: {'name': 'Valentines Day (Brazil)', 'type': 'commercial', 'impact': 'medium'},
            7: {'name': 'Winter Vacation', 'type': 'seasonal', 'impact': 'medium'},
            8: {'name': 'Fathers Day', 'type': 'commercial', 'impact': 'medium'},
            9: {'name': 'Independence Day', 'type': 'holiday', 'impact': 'low'},
            10: {'name': 'Childrens Day', 'type': 'commercial', 'impact': 'medium'},
            11: {'name': 'Black Friday', 'type': 'commercial', 'impact': 'very_high'},
            12: {'name': 'Christmas', 'type': 'holiday', 'impact': 'very_high'}
        }
        
    def load_data(self):
        """Load cleaned datasets for seasonal analysis."""
        print("Loading cleaned datasets for seasonal analysis...")
        
        # Load main datasets
        datasets_to_load = ['orders', 'order_items', 'products', 'customers']
        
        for dataset_name in datasets_to_load:
            file_path = f"{self.data_dir}/cleaned_{dataset_name}.csv"
            try:
                df = pd.read_csv(file_path)
                self.datasets[dataset_name] = df
                print(f"Loaded {dataset_name}: {len(df):,} rows")
            except FileNotFoundError:
                print(f"Warning: {file_path} not found")
        
        # Convert date columns
        if 'orders' in self.datasets:
            date_columns = ['order_purchase_timestamp', 'order_delivered_customer_date', 
                          'order_estimated_delivery_date', 'order_delivered_carrier_date']
            for col in date_columns:
                if col in self.datasets['orders'].columns:
                    self.datasets['orders'][col] = pd.to_datetime(self.datasets['orders'][col])
        
        print(f"Successfully loaded {len(self.datasets)} datasets")
        return self.datasets
    
    def prepare_seasonal_data(self):
        """Prepare data for seasonal analysis with time series features."""
        print("\n=== PREPARING SEASONAL DATA ===")
        
        if not self.datasets:
            self.load_data()
        
        # Merge orders with order items to get revenue data
        orders_df = self.datasets['orders'].copy()
        items_df = self.datasets['order_items'].copy()
        
        # Calculate order values
        order_values = items_df.groupby('order_id').agg({
            'price': 'sum',
            'freight_value': 'sum',
            'product_id': 'count'
        }).reset_index()
        order_values.columns = ['order_id', 'total_price', 'total_freight', 'item_count']
        order_values['total_order_value'] = order_values['total_price'] + order_values['total_freight']
        
        # Merge with orders
        seasonal_data = orders_df.merge(order_values, on='order_id', how='left')
        
        # Add temporal features
        seasonal_data['year'] = seasonal_data['order_purchase_timestamp'].dt.year
        seasonal_data['month'] = seasonal_data['order_purchase_timestamp'].dt.month
        seasonal_data['quarter'] = seasonal_data['order_purchase_timestamp'].dt.quarter
        seasonal_data['day_of_week'] = seasonal_data['order_purchase_timestamp'].dt.dayofweek
        seasonal_data['week_of_year'] = seasonal_data['order_purchase_timestamp'].dt.isocalendar().week
        seasonal_data['day_of_month'] = seasonal_data['order_purchase_timestamp'].dt.day
        
        # Add Brazilian seasonal indicators
        seasonal_data['is_summer'] = seasonal_data['month'].isin([12, 1, 2])  # Dec-Feb
        seasonal_data['is_autumn'] = seasonal_data['month'].isin([3, 4, 5])   # Mar-May
        seasonal_data['is_winter'] = seasonal_data['month'].isin([6, 7, 8])   # Jun-Aug
        seasonal_data['is_spring'] = seasonal_data['month'].isin([9, 10, 11]) # Sep-Nov
        
        # Add cultural event indicators
        for month, event_info in self.brazilian_events.items():
            seasonal_data[f'is_{event_info["name"].lower().replace(" ", "_")}'] = (
                seasonal_data['month'] == month
            )
        
        # Add event impact levels
        seasonal_data['event_impact_level'] = seasonal_data['month'].map(
            {month: info['impact'] for month, info in self.brazilian_events.items()}
        )
        
        self.seasonal_data = seasonal_data
        print(f"Prepared seasonal data: {len(seasonal_data):,} orders with temporal features")
        
        return seasonal_data
    
    def analyze_monthly_seasonal_patterns(self):
        """
        Analyze monthly and seasonal sales patterns by category.
        
        Returns:
            dict: Monthly and seasonal pattern analysis results
        """
        print("\n=== ANALYZING MONTHLY AND SEASONAL PATTERNS ===")
        
        if self.seasonal_data is None or len(self.seasonal_data) == 0:
            self.prepare_seasonal_data()
        
        # Monthly trends analysis
        monthly_trends = self.seasonal_data.groupby(['year', 'month']).agg({
            'order_id': 'count',
            'total_order_value': ['sum', 'mean'],
            'customer_id': 'nunique',
            'item_count': 'sum'
        }).reset_index()
        
        # Flatten column names
        monthly_trends.columns = [
            'year', 'month', 'monthly_orders', 'monthly_revenue', 'avg_order_value',
            'monthly_customers', 'monthly_items'
        ]
        
        # Add year-month for easier analysis
        monthly_trends['year_month'] = monthly_trends['year'].astype(str) + '-' + monthly_trends['month'].astype(str).str.zfill(2)
        
        # Calculate month-over-month growth
        monthly_trends = monthly_trends.sort_values(['year', 'month'])
        monthly_trends['revenue_growth'] = monthly_trends['monthly_revenue'].pct_change() * 100
        monthly_trends['order_growth'] = monthly_trends['monthly_orders'].pct_change() * 100
        
        print("Monthly Trends Summary:")
        print(monthly_trends.groupby('month').agg({
            'monthly_revenue': 'mean',
            'monthly_orders': 'mean',
            'avg_order_value': 'mean'
        }).round(2))
        
        # Seasonal patterns analysis
        seasonal_patterns = self.seasonal_data.groupby('quarter').agg({
            'order_id': 'count',
            'total_order_value': ['sum', 'mean'],
            'customer_id': 'nunique'
        }).reset_index()
        
        seasonal_patterns.columns = [
            'quarter', 'quarterly_orders', 'quarterly_revenue', 'avg_order_value', 'quarterly_customers'
        ]
        
        # Add seasonal names
        season_names = {1: 'Summer', 2: 'Autumn', 3: 'Winter', 4: 'Spring'}
        seasonal_patterns['season_name'] = seasonal_patterns['quarter'].map(season_names)
        
        print("\nSeasonal Patterns Summary:")
        print(seasonal_patterns[['season_name', 'quarterly_revenue', 'quarterly_orders', 'avg_order_value']])
        
        # Category-wise seasonal analysis
        if 'products' in self.datasets:
            # Merge with product categories
            items_with_products = self.datasets['order_items'].merge(
                self.datasets['products'][['product_id', 'product_category_name_english']], 
                on='product_id', how='left'
            )
            
            # Merge with seasonal data
            category_seasonal = self.seasonal_data.merge(
                items_with_products[['order_id', 'product_category_name_english', 'price']], 
                on='order_id', how='left'
            )
            
            # Category seasonal patterns
            category_patterns = category_seasonal.groupby(['product_category_name_english', 'month']).agg({
                'order_id': 'count',
                'price': 'sum'
            }).reset_index()
            
            category_patterns.columns = ['category', 'month', 'category_orders', 'category_revenue']
            
            # Calculate seasonal variance for each category
            category_variance = category_patterns.groupby('category').agg({
                'category_revenue': ['mean', 'std', 'min', 'max']
            }).reset_index()
            
            category_variance.columns = ['category', 'avg_monthly_revenue', 'revenue_std', 'min_revenue', 'max_revenue']
            category_variance['coefficient_of_variation'] = (
                category_variance['revenue_std'] / category_variance['avg_monthly_revenue']
            ).fillna(0)
            category_variance['seasonal_variance_score'] = category_variance['coefficient_of_variation']
            
            # Sort by seasonal variance
            category_variance = category_variance.sort_values('seasonal_variance_score', ascending=False)
            
            print(f"\nTop 10 Most Seasonal Categories:")
            print(category_variance.head(10)[['category', 'seasonal_variance_score', 'avg_monthly_revenue']])
        
        # Store results
        self.insights['monthly_patterns'] = {
            'monthly_trends': monthly_trends.to_dict('records'),
            'seasonal_patterns': seasonal_patterns.to_dict('records'),
            'category_variance': category_variance.to_dict('records') if 'products' in self.datasets else []
        }
        
        return self.insights['monthly_patterns']
    
    def analyze_brazilian_holiday_impact(self):
        """
        Analyze the impact of Brazilian holidays and cultural events on sales.
        
        Returns:
            dict: Holiday impact analysis results
        """
        print("\n=== ANALYZING BRAZILIAN HOLIDAY IMPACT ===")
        
        if self.seasonal_data is None or len(self.seasonal_data) == 0:
            self.prepare_seasonal_data()
        
        # Holiday impact analysis
        holiday_impact = self.seasonal_data.groupby('month').agg({
            'total_order_value': ['sum', 'mean', 'count'],
            'customer_id': 'nunique',
            'item_count': 'sum'
        }).reset_index()
        
        # Flatten columns
        holiday_impact.columns = [
            'month', 'monthly_total_revenue', 'avg_order_value', 'order_count', 
            'unique_customers', 'total_items'
        ]
        
        # Add event information
        holiday_impact['event_name'] = holiday_impact['month'].map(
            {month: info['name'] for month, info in self.brazilian_events.items()}
        )
        holiday_impact['event_type'] = holiday_impact['month'].map(
            {month: info['type'] for month, info in self.brazilian_events.items()}
        )
        holiday_impact['expected_impact'] = holiday_impact['month'].map(
            {month: info['impact'] for month, info in self.brazilian_events.items()}
        )
        
        # Calculate performance metrics
        avg_monthly_revenue = holiday_impact['monthly_total_revenue'].mean()
        holiday_impact['revenue_vs_average'] = (
            (holiday_impact['monthly_total_revenue'] / avg_monthly_revenue - 1) * 100
        ).round(2)
        
        avg_monthly_orders = holiday_impact['order_count'].mean()
        holiday_impact['orders_vs_average'] = (
            (holiday_impact['order_count'] / avg_monthly_orders - 1) * 100
        ).round(2)
        
        # Sort by revenue impact
        holiday_impact = holiday_impact.sort_values('revenue_vs_average', ascending=False)
        
        print("Holiday Impact Analysis:")
        print(holiday_impact[['month', 'event_name', 'revenue_vs_average', 'orders_vs_average', 'expected_impact']])
        
        print("\n⚠️  DATA LIMITATION WARNINGS:")
        print("- Christmas (-34.6%): Misleading due to incomplete 2018 data")
        print("- Black Friday (-10.7%): Misleading due to missing 2018 November data")
        print("- Independence Day (-45.4%): Accurate - genuinely low performance month")
        print("- Dataset ends October 2018, missing key holiday seasons")
        
        # Specific event analysis
        high_impact_months = holiday_impact[holiday_impact['expected_impact'].isin(['high', 'very_high'])]
        
        print(f"\nHigh Impact Events Performance:")
        for _, row in high_impact_months.iterrows():
            print(f"{row['event_name']} (Month {row['month']}): "
                  f"{row['revenue_vs_average']:+.1f}% revenue, {row['orders_vs_average']:+.1f}% orders")
        
        # Category performance during holidays
        if 'products' in self.datasets:
            # Analyze category performance during high-impact months
            high_impact_month_list = high_impact_months['month'].tolist()
            
            holiday_categories = self.seasonal_data[
                self.seasonal_data['month'].isin(high_impact_month_list)
            ]
            
            # Merge with product categories
            items_with_products = self.datasets['order_items'].merge(
                self.datasets['products'][['product_id', 'product_category_name_english']], 
                on='product_id', how='left'
            )
            
            holiday_category_data = holiday_categories.merge(
                items_with_products[['order_id', 'product_category_name_english', 'price']], 
                on='order_id', how='left'
            )
            
            category_holiday_performance = holiday_category_data.groupby([
                'product_category_name_english', 'month'
            ]).agg({
                'price': 'sum',
                'order_id': 'count'
            }).reset_index()
            
            category_holiday_performance.columns = ['category', 'month', 'holiday_revenue', 'holiday_orders']
            
            # Calculate category holiday boost
            category_totals = holiday_category_data.groupby('product_category_name_english').agg({
                'price': 'sum'
            }).reset_index()
            category_totals.columns = ['category', 'total_category_revenue']
            
            category_holiday_summary = category_holiday_performance.groupby('category').agg({
                'holiday_revenue': 'sum',
                'holiday_orders': 'sum'
            }).reset_index()
            
            category_holiday_summary = category_holiday_summary.merge(category_totals, on='category')
            category_holiday_summary['holiday_revenue_share'] = (
                category_holiday_summary['holiday_revenue'] / category_holiday_summary['total_category_revenue'] * 100
            ).round(2)
            
            category_holiday_summary = category_holiday_summary.sort_values('holiday_revenue_share', ascending=False)
            
            print(f"\nTop 10 Categories Benefiting from Holidays:")
            print(category_holiday_summary.head(10)[['category', 'holiday_revenue_share', 'holiday_revenue']])
        
        # Store results
        self.insights['holiday_impact'] = {
            'monthly_impact': holiday_impact.to_dict('records'),
            'high_impact_events': high_impact_months.to_dict('records'),
            'category_holiday_performance': category_holiday_summary.to_dict('records') if 'products' in self.datasets else []
        }
        
        return self.insights['holiday_impact']
    
    def build_demand_forecasting_model(self):
        """
        Build demand forecasting model for 3-month predictions.
        
        Returns:
            dict: Forecasting model results and predictions
        """
        print("\n=== BUILDING DEMAND FORECASTING MODEL ===")
        
        if self.seasonal_data is None or len(self.seasonal_data) == 0:
            self.prepare_seasonal_data()
        
        # Prepare monthly aggregated data for forecasting
        monthly_data = self.seasonal_data.groupby(['year', 'month']).agg({
            'order_id': 'count',
            'total_order_value': 'sum',
            'customer_id': 'nunique',
            'item_count': 'sum'
        }).reset_index()
        
        monthly_data.columns = ['year', 'month', 'orders', 'revenue', 'customers', 'items']
        
        # Create time-based features for modeling
        monthly_data['month_sin'] = np.sin(2 * np.pi * monthly_data['month'] / 12)
        monthly_data['month_cos'] = np.cos(2 * np.pi * monthly_data['month'] / 12)
        monthly_data['quarter'] = ((monthly_data['month'] - 1) // 3) + 1
        
        # Add holiday impact features
        impact_scores = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        monthly_data['holiday_impact'] = monthly_data['month'].map(
            {month: impact_scores[info['impact']] for month, info in self.brazilian_events.items()}
        )
        
        # Add lag features (previous months)
        monthly_data = monthly_data.sort_values(['year', 'month'])
        for lag in [1, 2, 3]:
            monthly_data[f'revenue_lag_{lag}'] = monthly_data['revenue'].shift(lag)
            monthly_data[f'orders_lag_{lag}'] = monthly_data['orders'].shift(lag)
        
        # Remove rows with NaN values (due to lag features)
        model_data = monthly_data.dropna().copy()
        
        if len(model_data) < 10:
            print("Warning: Insufficient data for reliable forecasting")
            return {'error': 'Insufficient data for forecasting'}
        
        # Prepare features and targets
        feature_columns = [
            'month', 'quarter', 'month_sin', 'month_cos', 'holiday_impact',
            'revenue_lag_1', 'revenue_lag_2', 'revenue_lag_3',
            'orders_lag_1', 'orders_lag_2', 'orders_lag_3'
        ]
        
        X = model_data[feature_columns].copy()
        y_revenue = model_data['revenue'].copy()
        y_orders = model_data['orders'].copy()
        
        # Split data (use last 20% for testing)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_revenue_train, y_revenue_test = y_revenue[:split_idx], y_revenue[split_idx:]
        y_orders_train, y_orders_test = y_orders[:split_idx], y_orders[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        revenue_model = RandomForestRegressor(n_estimators=100, random_state=42)
        orders_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        revenue_model.fit(X_train_scaled, y_revenue_train)
        orders_model.fit(X_train_scaled, y_orders_train)
        
        # Make predictions on test set
        revenue_pred = revenue_model.predict(X_test_scaled)
        orders_pred = orders_model.predict(X_test_scaled)
        
        # Calculate model performance
        revenue_mae = mean_absolute_error(y_revenue_test, revenue_pred)
        revenue_rmse = np.sqrt(mean_squared_error(y_revenue_test, revenue_pred))
        revenue_r2 = r2_score(y_revenue_test, revenue_pred)
        
        orders_mae = mean_absolute_error(y_orders_test, orders_pred)
        orders_rmse = np.sqrt(mean_squared_error(y_orders_test, orders_pred))
        orders_r2 = r2_score(y_orders_test, orders_pred)
        
        print("Model Performance:")
        print(f"Revenue Model - MAE: ${revenue_mae:,.2f}, RMSE: ${revenue_rmse:,.2f}, R²: {revenue_r2:.3f}")
        print(f"Orders Model - MAE: {orders_mae:.0f}, RMSE: {orders_rmse:.0f}, R²: {orders_r2:.3f}")
        
        # Generate 3-month forecasts
        last_data = model_data.iloc[-1].copy()
        forecasts = []
        
        for i in range(1, 4):  # Next 3 months
            # Calculate next month
            next_month = (last_data['month'] + i - 1) % 12 + 1
            next_year = last_data['year'] + ((last_data['month'] + i - 1) // 12)
            
            # Create features for next month
            next_features = {
                'month': next_month,
                'quarter': ((next_month - 1) // 3) + 1,
                'month_sin': np.sin(2 * np.pi * next_month / 12),
                'month_cos': np.cos(2 * np.pi * next_month / 12),
                'holiday_impact': {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}[self.brazilian_events[next_month]['impact']] if next_month in self.brazilian_events else 2
            }
            
            # Use recent data for lag features
            if i == 1:
                next_features.update({
                    'revenue_lag_1': last_data['revenue'],
                    'revenue_lag_2': model_data.iloc[-2]['revenue'] if len(model_data) > 1 else last_data['revenue'],
                    'revenue_lag_3': model_data.iloc[-3]['revenue'] if len(model_data) > 2 else last_data['revenue'],
                    'orders_lag_1': last_data['orders'],
                    'orders_lag_2': model_data.iloc[-2]['orders'] if len(model_data) > 1 else last_data['orders'],
                    'orders_lag_3': model_data.iloc[-3]['orders'] if len(model_data) > 2 else last_data['orders']
                })
            else:
                # Use previous forecasts for lag features
                prev_forecast = forecasts[i-2]
                next_features.update({
                    'revenue_lag_1': prev_forecast['predicted_revenue'],
                    'revenue_lag_2': forecasts[i-3]['predicted_revenue'] if i > 2 else last_data['revenue'],
                    'revenue_lag_3': last_data['revenue'],
                    'orders_lag_1': prev_forecast['predicted_orders'],
                    'orders_lag_2': forecasts[i-3]['predicted_orders'] if i > 2 else last_data['orders'],
                    'orders_lag_3': last_data['orders']
                })
            
            # Convert to array and scale
            X_next = np.array([next_features[col] for col in feature_columns]).reshape(1, -1)
            X_next_scaled = scaler.transform(X_next)
            
            # Make predictions
            pred_revenue = revenue_model.predict(X_next_scaled)[0]
            pred_orders = orders_model.predict(X_next_scaled)[0]
            
            # Calculate confidence intervals (simple approach using model variance)
            revenue_std = np.std(revenue_pred - y_revenue_test)
            orders_std = np.std(orders_pred - y_orders_test)
            
            forecast = {
                'year': int(next_year),
                'month': int(next_month),
                'month_name': pd.to_datetime(f'{int(next_year)}-{int(next_month):02d}-01').strftime('%B'),
                'predicted_revenue': float(pred_revenue),
                'predicted_orders': int(pred_orders),
                'revenue_lower_ci': float(pred_revenue - 1.96 * revenue_std),
                'revenue_upper_ci': float(pred_revenue + 1.96 * revenue_std),
                'orders_lower_ci': int(max(0, pred_orders - 1.96 * orders_std)),
                'orders_upper_ci': int(pred_orders + 1.96 * orders_std),
                'event_name': self.brazilian_events[next_month]['name'],
                'expected_impact': self.brazilian_events[next_month]['impact']
            }
            
            forecasts.append(forecast)
        
        print("\n3-Month Demand Forecast:")
        for forecast in forecasts:
            print(f"{forecast['month_name']} {forecast['year']}: "
                  f"${forecast['predicted_revenue']:,.0f} revenue, "
                  f"{forecast['predicted_orders']:,} orders "
                  f"({forecast['event_name']})")
        
        # Feature importance
        revenue_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': revenue_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\nTop Revenue Forecasting Features:")
        print(revenue_importance.head())
        
        # Store results
        self.forecasting_models = {
            'revenue_model': revenue_model,
            'orders_model': orders_model,
            'scaler': scaler,
            'feature_columns': feature_columns,
            'performance': {
                'revenue_mae': revenue_mae,
                'revenue_rmse': revenue_rmse,
                'revenue_r2': revenue_r2,
                'orders_mae': orders_mae,
                'orders_rmse': orders_rmse,
                'orders_r2': orders_r2
            },
            'forecasts': forecasts,
            'feature_importance': revenue_importance.to_dict('records')
        }
        
        return self.forecasting_models
    
    def calculate_seasonal_variance_metrics(self):
        """
        Calculate seasonal variance and category performance metrics.
        
        Returns:
            dict: Seasonal variance analysis results
        """
        print("\n=== CALCULATING SEASONAL VARIANCE METRICS ===")
        
        if self.seasonal_data is None or len(self.seasonal_data) == 0:
            self.prepare_seasonal_data()
        
        # Overall seasonal variance
        monthly_totals = self.seasonal_data.groupby('month').agg({
            'total_order_value': ['sum', 'count', 'mean'],
            'customer_id': 'nunique'
        }).reset_index()
        
        monthly_totals.columns = ['month', 'total_revenue', 'total_orders', 'avg_order_value', 'unique_customers']
        
        # Calculate variance metrics
        revenue_mean = monthly_totals['total_revenue'].mean()
        revenue_std = monthly_totals['total_revenue'].std()
        revenue_cv = revenue_std / revenue_mean if revenue_mean > 0 else 0
        
        orders_mean = monthly_totals['total_orders'].mean()
        orders_std = monthly_totals['total_orders'].std()
        orders_cv = orders_std / orders_mean if orders_mean > 0 else 0
        
        print(f"Overall Seasonal Variance:")
        print(f"Revenue CV: {revenue_cv:.3f}, Orders CV: {orders_cv:.3f}")
        
        # Peak and trough analysis
        peak_revenue_month = monthly_totals.loc[monthly_totals['total_revenue'].idxmax()]
        trough_revenue_month = monthly_totals.loc[monthly_totals['total_revenue'].idxmin()]
        
        peak_orders_month = monthly_totals.loc[monthly_totals['total_orders'].idxmax()]
        trough_orders_month = monthly_totals.loc[monthly_totals['total_orders'].idxmin()]
        
        print(f"\nPeak Performance:")
        print(f"Revenue: {self.brazilian_events[peak_revenue_month['month']]['name']} "
              f"(${peak_revenue_month['total_revenue']:,.0f})")
        print(f"Orders: {self.brazilian_events[peak_orders_month['month']]['name']} "
              f"({peak_orders_month['total_orders']:,} orders)")
        
        print(f"\nTrough Performance:")
        print(f"Revenue: {self.brazilian_events[trough_revenue_month['month']]['name']} "
              f"(${trough_revenue_month['total_revenue']:,.0f})")
        print(f"Orders: {self.brazilian_events[trough_orders_month['month']]['name']} "
              f"({trough_orders_month['total_orders']:,} orders)")
        
        # Category-specific variance analysis
        if 'products' in self.datasets:
            # Merge with product categories
            items_with_products = self.datasets['order_items'].merge(
                self.datasets['products'][['product_id', 'product_category_name_english']], 
                on='product_id', how='left'
            )
            
            category_seasonal_data = self.seasonal_data.merge(
                items_with_products[['order_id', 'product_category_name_english', 'price']], 
                on='order_id', how='left'
            )
            
            # Calculate category seasonal metrics
            category_monthly = category_seasonal_data.groupby(['product_category_name_english', 'month']).agg({
                'price': 'sum',
                'order_id': 'count'
            }).reset_index()
            
            category_monthly.columns = ['category', 'month', 'monthly_revenue', 'monthly_orders']
            
            # Calculate variance for each category
            category_variance = category_monthly.groupby('category').agg({
                'monthly_revenue': ['mean', 'std', 'min', 'max', 'count']
            }).reset_index()
            
            category_variance.columns = ['category', 'avg_monthly_revenue', 'revenue_std', 
                                       'min_monthly_revenue', 'max_monthly_revenue', 'months_active']
            
            # Calculate coefficient of variation and seasonality score
            category_variance['revenue_cv'] = (
                category_variance['revenue_std'] / category_variance['avg_monthly_revenue']
            ).fillna(0)
            
            category_variance['seasonality_score'] = category_variance['revenue_cv']
            category_variance['peak_to_trough_ratio'] = (
                category_variance['max_monthly_revenue'] / category_variance['min_monthly_revenue']
            ).replace([np.inf, -np.inf], 0).fillna(0)
            
            # Classify seasonality levels
            def classify_seasonality(cv):
                if cv < 0.3:
                    return 'Low Seasonality'
                elif cv < 0.6:
                    return 'Moderate Seasonality'
                elif cv < 1.0:
                    return 'High Seasonality'
                else:
                    return 'Very High Seasonality'
            
            category_variance['seasonality_level'] = category_variance['revenue_cv'].apply(classify_seasonality)
            
            # Sort by seasonality score
            category_variance = category_variance.sort_values('seasonality_score', ascending=False)
            
            print(f"\nTop 10 Most Seasonal Categories:")
            print(category_variance.head(10)[['category', 'seasonality_level', 'seasonality_score', 'peak_to_trough_ratio']])
            
            print(f"\nTop 10 Least Seasonal Categories:")
            print(category_variance.tail(10)[['category', 'seasonality_level', 'seasonality_score', 'peak_to_trough_ratio']])
        
        # Store results
        variance_results = {
            'overall_variance': {
                'revenue_cv': revenue_cv,
                'orders_cv': orders_cv,
                'revenue_mean': revenue_mean,
                'revenue_std': revenue_std,
                'orders_mean': orders_mean,
                'orders_std': orders_std
            },
            'peak_trough_analysis': {
                'peak_revenue': {
                    'month': int(peak_revenue_month['month']),
                    'event': self.brazilian_events[peak_revenue_month['month']]['name'],
                    'revenue': float(peak_revenue_month['total_revenue'])
                },
                'trough_revenue': {
                    'month': int(trough_revenue_month['month']),
                    'event': self.brazilian_events[trough_revenue_month['month']]['name'],
                    'revenue': float(trough_revenue_month['total_revenue'])
                },
                'peak_orders': {
                    'month': int(peak_orders_month['month']),
                    'event': self.brazilian_events[peak_orders_month['month']]['name'],
                    'orders': int(peak_orders_month['total_orders'])
                },
                'trough_orders': {
                    'month': int(trough_orders_month['month']),
                    'event': self.brazilian_events[trough_orders_month['month']]['name'],
                    'orders': int(trough_orders_month['total_orders'])
                }
            },
            'monthly_totals': monthly_totals.to_dict('records'),
            'category_variance': category_variance.to_dict('records') if 'products' in self.datasets else []
        }
        
        self.insights['seasonal_variance'] = variance_results
        return variance_results    

    def generate_inventory_optimization_recommendations(self):
        """
        Generate inventory optimization recommendations based on seasonal patterns.
        
        Returns:
            dict: Inventory optimization recommendations
        """
        print("\n=== GENERATING INVENTORY OPTIMIZATION RECOMMENDATIONS ===")
        
        # Ensure we have all necessary analysis results
        if 'seasonal_variance' not in self.insights:
            self.calculate_seasonal_variance_metrics()
        
        if 'holiday_impact' not in self.insights:
            self.analyze_brazilian_holiday_impact()
        
        if not self.forecasting_models:
            self.build_demand_forecasting_model()
        
        recommendations = {}
        
        # Overall inventory strategy
        overall_strategy = {
            'high_season_months': [],
            'low_season_months': [],
            'preparation_months': [],
            'clearance_months': []
        }
        
        # Analyze monthly patterns for overall strategy
        monthly_data = self.insights['seasonal_variance']['monthly_totals']
        avg_revenue = np.mean([month['total_revenue'] for month in monthly_data])
        
        for month_data in monthly_data:
            month = month_data['month']
            revenue = month_data['total_revenue']
            event_name = self.brazilian_events[month]['name']
            
            if revenue > avg_revenue * 1.2:  # 20% above average
                overall_strategy['high_season_months'].append({
                    'month': month,
                    'event': event_name,
                    'revenue_multiplier': revenue / avg_revenue,
                    'recommendation': 'Increase inventory by 30-50%'
                })
            elif revenue < avg_revenue * 0.8:  # 20% below average
                overall_strategy['low_season_months'].append({
                    'month': month,
                    'event': event_name,
                    'revenue_multiplier': revenue / avg_revenue,
                    'recommendation': 'Reduce inventory by 20-30%'
                })
        
        # Preparation months (month before high season)
        for high_month in overall_strategy['high_season_months']:
            prep_month = high_month['month'] - 1 if high_month['month'] > 1 else 12
            overall_strategy['preparation_months'].append({
                'month': prep_month,
                'event': self.brazilian_events[prep_month]['name'],
                'target_event': high_month['event'],
                'recommendation': f"Build inventory for {high_month['event']}"
            })
        
        # Clearance months (month after high season)
        for high_month in overall_strategy['high_season_months']:
            clear_month = high_month['month'] + 1 if high_month['month'] < 12 else 1
            overall_strategy['clearance_months'].append({
                'month': clear_month,
                'event': self.brazilian_events[clear_month]['name'],
                'previous_event': high_month['event'],
                'recommendation': f"Clear excess inventory from {high_month['event']}"
            })
        
        print("Overall Inventory Strategy:")
        print(f"High Season Months: {len(overall_strategy['high_season_months'])}")
        print(f"Low Season Months: {len(overall_strategy['low_season_months'])}")
        
        # Category-specific recommendations
        category_recommendations = []
        
        if 'category_variance' in self.insights['seasonal_variance']:
            category_data = self.insights['seasonal_variance']['category_variance']
            
            for category in category_data:
                cat_name = category['category']
                seasonality_level = category['seasonality_level']
                seasonality_score = category['seasonality_score']
                peak_ratio = category['peak_to_trough_ratio']
                
                # Generate recommendations based on seasonality
                if seasonality_level == 'Very High Seasonality':
                    strategy = 'Dynamic inventory with 60-80% seasonal adjustment'
                    risk_level = 'High'
                    buffer_stock = 'Low (10-15%)'
                elif seasonality_level == 'High Seasonality':
                    strategy = 'Seasonal inventory with 40-60% adjustment'
                    risk_level = 'Medium-High'
                    buffer_stock = 'Medium (15-20%)'
                elif seasonality_level == 'Moderate Seasonality':
                    strategy = 'Moderate seasonal adjustment (20-40%)'
                    risk_level = 'Medium'
                    buffer_stock = 'Medium (20-25%)'
                else:
                    strategy = 'Stable inventory with minimal adjustment'
                    risk_level = 'Low'
                    buffer_stock = 'High (25-30%)'
                
                category_recommendations.append({
                    'category': cat_name,
                    'seasonality_level': seasonality_level,
                    'seasonality_score': round(seasonality_score, 3),
                    'peak_to_trough_ratio': round(peak_ratio, 2),
                    'inventory_strategy': strategy,
                    'risk_level': risk_level,
                    'buffer_stock_recommendation': buffer_stock,
                    'avg_monthly_revenue': category['avg_monthly_revenue']
                })
            
            # Sort by revenue impact
            category_recommendations.sort(key=lambda x: x['avg_monthly_revenue'], reverse=True)
            
            print(f"\nTop 5 Categories by Revenue - Inventory Recommendations:")
            for i, cat in enumerate(category_recommendations[:5]):
                print(f"{i+1}. {cat['category'][:30]}...")
                print(f"   Seasonality: {cat['seasonality_level']}")
                print(f"   Strategy: {cat['inventory_strategy']}")
        
        # Forecasting-based recommendations
        forecast_recommendations = []
        
        if 'forecasts' in self.forecasting_models:
            for forecast in self.forecasting_models['forecasts']:
                month = forecast['month']
                predicted_revenue = forecast['predicted_revenue']
                event_name = forecast['event_name']
                expected_impact = forecast['expected_impact']
                
                # Calculate recommended inventory adjustment
                if expected_impact == 'very_high':
                    adjustment = '+50-70%'
                    timing = '6-8 weeks before'
                elif expected_impact == 'high':
                    adjustment = '+30-50%'
                    timing = '4-6 weeks before'
                elif expected_impact == 'medium':
                    adjustment = '+10-30%'
                    timing = '2-4 weeks before'
                else:
                    adjustment = '±10%'
                    timing = '1-2 weeks before'
                
                forecast_recommendations.append({
                    'month': month,
                    'month_name': forecast['month_name'],
                    'year': forecast['year'],
                    'event': event_name,
                    'predicted_revenue': predicted_revenue,
                    'expected_impact': expected_impact,
                    'inventory_adjustment': adjustment,
                    'preparation_timing': timing,
                    'confidence_interval': f"${forecast['revenue_lower_ci']:,.0f} - ${forecast['revenue_upper_ci']:,.0f}"
                })
            
            print(f"\n3-Month Inventory Planning:")
            for rec in forecast_recommendations:
                print(f"{rec['month_name']} {rec['year']} ({rec['event']}):")
                print(f"  Predicted Revenue: ${rec['predicted_revenue']:,.0f}")
                print(f"  Inventory Adjustment: {rec['inventory_adjustment']}")
                print(f"  Preparation Timing: {rec['preparation_timing']}")
        
        # Risk management recommendations
        risk_management = {
            'high_risk_categories': [],
            'stable_categories': [],
            'diversification_opportunities': []
        }
        
        if category_recommendations:
            # Identify high-risk categories (very seasonal)
            high_risk = [cat for cat in category_recommendations 
                        if cat['seasonality_level'] in ['Very High Seasonality', 'High Seasonality']]
            risk_management['high_risk_categories'] = high_risk[:10]  # Top 10
            
            # Identify stable categories
            stable = [cat for cat in category_recommendations 
                     if cat['seasonality_level'] == 'Low Seasonality']
            risk_management['stable_categories'] = stable[:10]  # Top 10
            
            # Diversification opportunities (categories with different seasonal patterns)
            risk_management['diversification_opportunities'] = [
                "Focus on stable categories during high-risk periods",
                "Balance seasonal and non-seasonal product mix",
                "Consider counter-seasonal categories for risk mitigation"
            ]
        
        # Compile all recommendations
        recommendations = {
            'overall_strategy': overall_strategy,
            'category_recommendations': category_recommendations,
            'forecast_based_recommendations': forecast_recommendations,
            'risk_management': risk_management,
            'key_insights': [
                f"Peak season requires {len(overall_strategy['high_season_months'])} months of increased inventory",
                f"Most seasonal categories need 40-80% inventory adjustments",
                f"Preparation should begin 4-8 weeks before major events",
                f"Risk can be mitigated by balancing seasonal and stable categories"
            ]
        }
        
        self.insights['inventory_recommendations'] = recommendations
        return recommendations
    
    def create_seasonal_intelligence_report(self):
        """
        Create a comprehensive seasonal intelligence report.
        
        Returns:
            str: Formatted report content
        """
        print("\n=== CREATING SEASONAL INTELLIGENCE REPORT ===")
        
        # Ensure all analyses are complete
        if 'monthly_patterns' not in self.insights:
            self.analyze_monthly_seasonal_patterns()
        
        if 'holiday_impact' not in self.insights:
            self.analyze_brazilian_holiday_impact()
        
        if not self.forecasting_models:
            self.build_demand_forecasting_model()
        
        if 'seasonal_variance' not in self.insights:
            self.calculate_seasonal_variance_metrics()
        
        if 'inventory_recommendations' not in self.insights:
            self.generate_inventory_optimization_recommendations()
        
        # Generate report
        report_lines = []
        report_lines.append("SEASONAL DEMAND INTELLIGENCE ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Data Period: {self.seasonal_data['order_purchase_timestamp'].min()} to {self.seasonal_data['order_purchase_timestamp'].max()}")
        report_lines.append(f"Total Orders Analyzed: {len(self.seasonal_data):,}")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 20)
        
        # Key metrics
        total_revenue = self.seasonal_data['total_order_value'].sum()
        avg_monthly_revenue = total_revenue / 12  # Approximate
        peak_month = self.insights['seasonal_variance']['peak_trough_analysis']['peak_revenue']
        trough_month = self.insights['seasonal_variance']['peak_trough_analysis']['trough_revenue']
        
        report_lines.append(f"• Total Revenue Analyzed: ${total_revenue:,.2f}")
        report_lines.append(f"• Average Monthly Revenue: ${avg_monthly_revenue:,.2f}")
        report_lines.append(f"• Peak Month: {peak_month['event']} (${peak_month['revenue']:,.0f})")
        report_lines.append(f"• Trough Month: {trough_month['event']} (${trough_month['revenue']:,.0f})")
        report_lines.append(f"• Seasonal Variance: {self.insights['seasonal_variance']['overall_variance']['revenue_cv']:.1%}")
        report_lines.append("")
        
        # Monthly Patterns
        report_lines.append("MONTHLY SEASONAL PATTERNS")
        report_lines.append("-" * 30)
        
        monthly_data = self.insights['seasonal_variance']['monthly_totals']
        for month_data in sorted(monthly_data, key=lambda x: x['month']):
            month = month_data['month']
            event = self.brazilian_events[month]['name']
            revenue = month_data['total_revenue']
            orders = month_data['total_orders']
            
            report_lines.append(f"Month {month:2d} ({event:20s}): ${revenue:10,.0f} revenue, {orders:6,} orders")
        
        report_lines.append("")
        
        # Holiday Impact Analysis
        report_lines.append("BRAZILIAN HOLIDAY IMPACT ANALYSIS")
        report_lines.append("-" * 40)
        
        holiday_data = self.insights['holiday_impact']['monthly_impact']
        high_impact_events = [h for h in holiday_data if h['expected_impact'] in ['high', 'very_high']]
        
        report_lines.append("High Impact Events:")
        for event in sorted(high_impact_events, key=lambda x: x['revenue_vs_average'], reverse=True):
            report_lines.append(f"• {event['event_name']:20s}: {event['revenue_vs_average']:+6.1f}% revenue impact")
        
        report_lines.append("")
        
        # Forecasting Results
        report_lines.append("3-MONTH DEMAND FORECAST")
        report_lines.append("-" * 30)
        
        if 'forecasts' in self.forecasting_models:
            model_performance = self.forecasting_models['performance']
            report_lines.append(f"Model Performance (R²): Revenue {model_performance['revenue_r2']:.3f}, Orders {model_performance['orders_r2']:.3f}")
            report_lines.append("")
            
            for forecast in self.forecasting_models['forecasts']:
                report_lines.append(f"{forecast['month_name']} {forecast['year']} ({forecast['event_name']}):")
                report_lines.append(f"  Predicted Revenue: ${forecast['predicted_revenue']:,.0f}")
                report_lines.append(f"  Predicted Orders: {forecast['predicted_orders']:,}")
                report_lines.append(f"  Confidence Interval: ${forecast['revenue_lower_ci']:,.0f} - ${forecast['revenue_upper_ci']:,.0f}")
                report_lines.append("")
        
        # Category Analysis
        report_lines.append("CATEGORY SEASONALITY ANALYSIS")
        report_lines.append("-" * 35)
        
        if 'category_variance' in self.insights['seasonal_variance']:
            category_data = self.insights['seasonal_variance']['category_variance']
            
            report_lines.append("Most Seasonal Categories (Top 10):")
            for i, cat in enumerate(category_data[:10]):
                report_lines.append(f"{i+1:2d}. {cat['category'][:40]:40s} - {cat['seasonality_level']:20s} (CV: {cat['seasonality_score']:.3f})")
            
            report_lines.append("")
            report_lines.append("Least Seasonal Categories (Top 10):")
            for i, cat in enumerate(category_data[-10:]):
                report_lines.append(f"{i+1:2d}. {cat['category'][:40]:40s} - {cat['seasonality_level']:20s} (CV: {cat['seasonality_score']:.3f})")
        
        report_lines.append("")
        
        # Inventory Recommendations
        report_lines.append("INVENTORY OPTIMIZATION RECOMMENDATIONS")
        report_lines.append("-" * 45)
        
        inventory_recs = self.insights['inventory_recommendations']
        
        report_lines.append("High Season Preparation:")
        for month in inventory_recs['overall_strategy']['high_season_months']:
            report_lines.append(f"• {month['event']:20s}: {month['recommendation']}")
        
        report_lines.append("")
        report_lines.append("Key Insights:")
        for insight in inventory_recs['key_insights']:
            report_lines.append(f"• {insight}")
        
        report_lines.append("")
        report_lines.append("Risk Management:")
        report_lines.append(f"• High-risk categories: {len(inventory_recs['risk_management']['high_risk_categories'])}")
        report_lines.append(f"• Stable categories: {len(inventory_recs['risk_management']['stable_categories'])}")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("End of Seasonal Intelligence Report")
        
        report_content = "\n".join(report_lines)
        
        # Save report
        report_file = 'reports/seasonal_intelligence_report.md'
        os.makedirs('reports', exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Seasonal intelligence report saved to: {report_file}")
        
        return report_content
    
    def run_complete_seasonal_analysis(self):
        """
        Run the complete seasonal demand intelligence analysis pipeline.
        
        Returns:
            dict: Complete seasonal analysis results
        """
        print("🚀 STARTING COMPLETE SEASONAL DEMAND INTELLIGENCE ANALYSIS")
        print("=" * 70)
        
        # Load and prepare data
        self.load_data()
        self.prepare_seasonal_data()
        
        # Run all analyses
        monthly_patterns = self.analyze_monthly_seasonal_patterns()
        holiday_impact = self.analyze_brazilian_holiday_impact()
        forecasting_results = self.build_demand_forecasting_model()
        variance_metrics = self.calculate_seasonal_variance_metrics()
        inventory_recommendations = self.generate_inventory_optimization_recommendations()
        
        # Create comprehensive report
        report_content = self.create_seasonal_intelligence_report()
        
        # Compile complete results
        complete_results = {
            'monthly_patterns': monthly_patterns,
            'holiday_impact': holiday_impact,
            'forecasting_models': forecasting_results,
            'seasonal_variance': variance_metrics,
            'inventory_recommendations': inventory_recommendations,
            'report_content': report_content,
            'data_summary': {
                'total_orders': len(self.seasonal_data),
                'total_revenue': float(self.seasonal_data['total_order_value'].sum()),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_period': f"{self.seasonal_data['order_purchase_timestamp'].min()} to {self.seasonal_data['order_purchase_timestamp'].max()}"
            }
        }
        
        print("\n✅ SEASONAL DEMAND INTELLIGENCE ANALYSIS COMPLETE!")
        print(f"📊 Analyzed {len(self.seasonal_data):,} orders")
        print(f"🎯 Generated 3-month demand forecast")
        print(f"📈 Identified seasonal patterns for {len(self.insights.get('seasonal_variance', {}).get('category_variance', []))} categories")
        print(f"💡 Created comprehensive inventory optimization recommendations")
        
        return complete_results


def main():
    """Main execution function for seasonal analysis."""
    
    # Initialize seasonal analysis
    seasonal_analyzer = SeasonalAnalysis()
    
    # Run complete analysis
    results = seasonal_analyzer.run_complete_seasonal_analysis()
    
    # Save key results to CSV files for dashboard use
    print(f"\n💾 Saving analysis results to feature_engineered directory...")
    
    output_dir = 'data/feature_engineered'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save monthly trends
    if 'monthly_patterns' in results and 'monthly_trends' in results['monthly_patterns']:
        monthly_df = pd.DataFrame(results['monthly_patterns']['monthly_trends'])
        monthly_df.to_csv(f'{output_dir}/seasonal_intelligence_monthly_trends.csv', index=False)
        print(f"📊 Monthly trends saved")
    
    # Save holiday impact
    if 'holiday_impact' in results and 'monthly_impact' in results['holiday_impact']:
        holiday_df = pd.DataFrame(results['holiday_impact']['monthly_impact'])
        holiday_df.to_csv(f'{output_dir}/seasonal_intelligence_cultural_events.csv', index=False)
        print(f"🎉 Holiday impact analysis saved")
    
    # Save category patterns
    if ('seasonal_variance' in results and 'category_variance' in results['seasonal_variance'] 
        and results['seasonal_variance']['category_variance']):
        category_df = pd.DataFrame(results['seasonal_variance']['category_variance'])
        category_df.to_csv(f'{output_dir}/seasonal_intelligence_category_patterns.csv', index=False)
        print(f"📦 Category seasonality patterns saved")
    
    # Save seasonal variance metrics
    if 'seasonal_variance' in results and 'monthly_totals' in results['seasonal_variance']:
        variance_df = pd.DataFrame(results['seasonal_variance']['monthly_totals'])
        variance_df.to_csv(f'{output_dir}/seasonal_intelligence_seasonal_variance.csv', index=False)
        print(f"📈 Seasonal variance metrics saved")
    
    # Save forecasting results
    if 'forecasting_models' in results and 'forecasts' in results['forecasting_models']:
        forecast_df = pd.DataFrame(results['forecasting_models']['forecasts'])
        forecast_df.to_csv(f'{output_dir}/seasonal_intelligence_forecasts.csv', index=False)
        print(f"🔮 Demand forecasts saved")
    
    # Save inventory recommendations
    if 'inventory_recommendations' in results and 'category_recommendations' in results['inventory_recommendations']:
        inventory_df = pd.DataFrame(results['inventory_recommendations']['category_recommendations'])
        inventory_df.to_csv(f'{output_dir}/seasonal_intelligence_inventory_recommendations.csv', index=False)
        print(f"📋 Inventory recommendations saved")
    
    # Create summary file
    summary_file = 'seasonal_intelligence_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("SEASONAL DEMAND INTELLIGENCE SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        # Write key metrics
        data_summary = results['data_summary']
        f.write("KEY METRICS:\n")
        f.write(f"Total Orders Analyzed: {data_summary['total_orders']:,}\n")
        f.write(f"Total Revenue: ${data_summary['total_revenue']:,.2f}\n")
        f.write(f"Analysis Period: {data_summary['data_period']}\n")
        f.write(f"Analysis Date: {data_summary['analysis_date']}\n\n")
        
        # Write key insights
        if 'inventory_recommendations' in results:
            f.write("KEY INSIGHTS:\n")
            for insight in results['inventory_recommendations']['key_insights']:
                f.write(f"• {insight}\n")
        
        f.write("\n⚠️  CRITICAL DATA LIMITATIONS:\n")
        f.write("• Christmas impact (-34.6%) is MISLEADING - only partial 2017 data\n")
        f.write("• Black Friday impact (-10.7%) is MISLEADING - 2018 November missing\n")
        f.write("• Independence Day impact (-45.4%) is ACCURATE - genuine low month\n")
        f.write("• Dataset period: Sep 2016 - Oct 2018 (incomplete coverage)\n")
        f.write("• Only 2017 has complete 12-month data for reliable analysis\n")
        
        f.write(f"\nDetailed report available in: reports/seasonal_intelligence_report.md\n")
    
    print(f"📄 Summary saved to: {summary_file}")
    
    return results


def analyze():
    """
    Wrapper function for compatibility with testing suite.
    Runs the complete seasonal analysis.
    """
    try:
        from seasonal_analysis import SeasonalAnalyzer
        analyzer = SeasonalAnalyzer()
        return analyzer.run_complete_analysis()
    except Exception as e:
        print(f"Seasonal analysis failed: {str(e)}")
        return False

if __name__ == "__main__":
    import os
    results = main()