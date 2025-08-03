"""
Customer Analytics and Lifetime Value Analysis Module

This module implements comprehensive customer analytics including RFM analysis,
customer lifetime value calculation, and predictive modeling for customer value identification.

Note: This dataset contains only single-purchase customers, so traditional retention
analysis is adapted to focus on purchase value, timing, and delivery experience patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class CustomerAnalytics:
    """
    Comprehensive customer analytics for Brazilian E-commerce dataset.
    Handles RFM analysis, CLV calculation, and predictive modeling.
    """
    
    def __init__(self, data_path='data/feature_engineered/customer_analytics.csv'):
        """
        Initialize CustomerAnalytics with feature-engineered data.
        
        Args:
            data_path (str): Path to the customer analytics CSV file
        """
        self.data_path = data_path
        self.customer_data = None
        self.rfm_segments = None
        self.clv_analysis = None
        self.predictive_model = None
        self.insights = {}
        
    def load_data(self):
        """Load and prepare customer analytics data."""
        print("Loading customer analytics data...")
        
        self.customer_data = pd.read_csv(self.data_path)
        
        # Convert date columns
        date_columns = ['last_order_date', 'first_order_date']
        for col in date_columns:
            if col in self.customer_data.columns:
                self.customer_data[col] = pd.to_datetime(self.customer_data[col])
        
        print(f"Loaded {len(self.customer_data):,} customer records")
        print(f"Data period: {self.customer_data['first_order_date'].min()} to {self.customer_data['last_order_date'].max()}")
        
        return self.customer_data
    
    def perform_rfm_analysis(self):
        """
        Perform RFM (Recency, Frequency, Monetary) analysis and customer segmentation.
        
        Returns:
            pd.DataFrame: RFM analysis results with segments
        """
        print("\n=== PERFORMING RFM ANALYSIS ===")
        
        if self.customer_data is None:
            self.load_data()
        
        # RFM scores are already calculated in the feature engineering
        # Let's analyze the distribution and create enhanced segments
        
        rfm_data = self.customer_data[['customer_id', 'recency_score', 'frequency_score', 
                                     'monetary_score', 'rfm_score', 'customer_segment',
                                     'total_revenue', 'days_since_last_order']].copy()
        
        # Analyze RFM score distributions
        print("RFM Score Distributions:")
        print(f"Recency Score: {rfm_data['recency_score'].describe()}")
        print(f"Frequency Score: {rfm_data['frequency_score'].describe()}")
        print(f"Monetary Score: {rfm_data['monetary_score'].describe()}")
        
        # Customer segment analysis
        segment_analysis = rfm_data.groupby('customer_segment').agg({
            'customer_id': 'count',
            'total_revenue': ['mean', 'sum'],
            'days_since_last_order': 'mean',
            'recency_score': 'mean',
            'frequency_score': 'mean',
            'monetary_score': 'mean'
        }).round(2)
        
        # Flatten column names
        segment_analysis.columns = [
            'customer_count', 'avg_revenue', 'total_revenue', 
            'avg_days_since_last_order', 'avg_recency_score',
            'avg_frequency_score', 'avg_monetary_score'
        ]
        
        # Calculate segment percentages
        segment_analysis['percentage'] = (
            segment_analysis['customer_count'] / len(rfm_data) * 100
        ).round(2)
        
        # Sort by customer count
        segment_analysis = segment_analysis.sort_values('customer_count', ascending=False)
        
        print("\nCustomer Segment Analysis:")
        print(segment_analysis)
        
        # Store insights
        self.insights['rfm_segments'] = segment_analysis.to_dict('index')
        self.rfm_segments = rfm_data
        
        return rfm_data
    
    def calculate_customer_lifetime_value(self):
        """
        Calculate and analyze Customer Lifetime Value (CLV).
        
        Note: Since all customers have single purchases, CLV is adapted to focus on
        purchase value potential and delivery experience impact.
        
        Returns:
            dict: CLV analysis results
        """
        print("\n=== CUSTOMER LIFETIME VALUE ANALYSIS ===")
        
        if self.customer_data is None:
            self.load_data()
        
        # CLV components analysis
        clv_data = self.customer_data[['customer_id', 'total_revenue', 'avg_order_value',
                                     'estimated_clv', 'clv_category', 'customer_segment',
                                     'avg_delivery_experience', 'delivery_reliability']].copy()
        
        # CLV distribution analysis
        print("CLV Distribution Analysis:")
        print(clv_data['estimated_clv'].describe())
        
        # CLV by category
        clv_by_category = clv_data.groupby('clv_category').agg({
            'customer_id': 'count',
            'estimated_clv': ['mean', 'sum'],
            'avg_delivery_experience': 'mean',
            'delivery_reliability': 'mean'
        }).round(2)
        
        clv_by_category.columns = [
            'customer_count', 'avg_clv', 'total_clv',
            'avg_delivery_days', 'avg_delivery_reliability'
        ]
        
        clv_by_category['percentage'] = (
            clv_by_category['customer_count'] / len(clv_data) * 100
        ).round(2)
        
        print("\nCLV by Category:")
        print(clv_by_category)
        
        # CLV by customer segment
        clv_by_segment = clv_data.groupby('customer_segment').agg({
            'estimated_clv': ['mean', 'sum', 'count'],
            'avg_delivery_experience': 'mean'
        }).round(2)
        
        clv_by_segment.columns = ['avg_clv', 'total_clv', 'customer_count', 'avg_delivery_days']
        
        print("\nCLV by Customer Segment:")
        print(clv_by_segment.sort_values('avg_clv', ascending=False))
        
        # Store results
        self.clv_analysis = {
            'clv_by_category': clv_by_category.to_dict('index'),
            'clv_by_segment': clv_by_segment.to_dict('index'),
            'clv_distribution': clv_data['estimated_clv'].describe().to_dict()
        }
        
        return self.clv_analysis
    
    def analyze_delivery_experience_impact(self):
        """
        Analyze the relationship between delivery experience and customer value.
        
        Returns:
            dict: Delivery experience analysis results
        """
        print("\n=== DELIVERY EXPERIENCE IMPACT ANALYSIS ===")
        
        if self.customer_data is None:
            self.load_data()
        
        # Delivery experience vs customer value
        delivery_data = self.customer_data[['customer_id', 'avg_delivery_experience', 
                                          'delivery_reliability', 'total_revenue',
                                          'customer_segment', 'clv_category']].copy()
        
        # Create delivery experience categories
        delivery_data['delivery_speed_category'] = pd.cut(
            delivery_data['avg_delivery_experience'],
            bins=[0, 7, 14, 21, 30, float('inf')],
            labels=['Very Fast (≤7d)', 'Fast (8-14d)', 'Normal (15-21d)', 'Slow (22-30d)', 'Very Slow (>30d)']
        )
        
        # Analyze delivery impact on customer value
        delivery_impact = delivery_data.groupby('delivery_speed_category').agg({
            'customer_id': 'count',
            'total_revenue': ['mean', 'sum'],
            'delivery_reliability': 'mean'
        }).round(2)
        
        delivery_impact.columns = ['customer_count', 'avg_revenue', 'total_revenue', 'avg_reliability']
        delivery_impact['percentage'] = (
            delivery_impact['customer_count'] / len(delivery_data) * 100
        ).round(2)
        
        print("Delivery Speed vs Customer Value:")
        print(delivery_impact)
        
        # Delivery reliability impact
        reliable_delivery = delivery_data[delivery_data['delivery_reliability'] == 1.0]
        unreliable_delivery = delivery_data[delivery_data['delivery_reliability'] < 1.0]
        
        print(f"\nDelivery Reliability Impact:")
        print(f"Customers with reliable delivery: {len(reliable_delivery):,} ({len(reliable_delivery)/len(delivery_data)*100:.1f}%)")
        print(f"Average revenue (reliable): ${reliable_delivery['total_revenue'].mean():.2f}")
        
        if len(unreliable_delivery) > 0:
            print(f"Customers with unreliable delivery: {len(unreliable_delivery):,} ({len(unreliable_delivery)/len(delivery_data)*100:.1f}%)")
            print(f"Average revenue (unreliable): ${unreliable_delivery['total_revenue'].mean():.2f}")
        
        # Store insights
        self.insights['delivery_impact'] = {
            'delivery_speed_analysis': delivery_impact.to_dict('index'),
            'reliability_impact': {
                'reliable_customers': len(reliable_delivery),
                'reliable_avg_revenue': reliable_delivery['total_revenue'].mean(),
                'unreliable_customers': len(unreliable_delivery),
                'unreliable_avg_revenue': unreliable_delivery['total_revenue'].mean() if len(unreliable_delivery) > 0 else 0
            }
        }
        
        return self.insights['delivery_impact']
    
    def build_high_value_customer_model(self):
        """
        Build a predictive model to identify high-value customers.
        
        Returns:
            dict: Model performance and feature importance results
        """
        print("\n=== BUILDING HIGH-VALUE CUSTOMER PREDICTIVE MODEL ===")
        
        if self.customer_data is None:
            self.load_data()
        
        # Prepare features for modeling
        model_data = self.customer_data.copy()
        
        # Create target variable (high-value customers)
        # Since we don't have repeat purchases, we'll predict high CLV customers
        model_data['is_high_value'] = (model_data['clv_category'].isin(['High Value', 'VIP'])).astype(int)
        
        # Select features for modeling
        feature_columns = [
            'recency_score', 'frequency_score', 'monetary_score',
            'avg_delivery_experience', 'delivery_reliability',
            'days_since_last_order', 'total_revenue'
        ]
        
        # Prepare features and target
        X = model_data[feature_columns].copy()
        y = model_data['is_high_value']
        
        # Handle any missing values
        X = X.fillna(X.mean())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        rf_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        
        rf_model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = rf_model.predict(X_test_scaled)
        y_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]
        
        # Model performance
        print("Model Performance:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(feature_importance)
        
        # Store model and results
        self.predictive_model = {
            'model': rf_model,
            'scaler': scaler,
            'feature_columns': feature_columns,
            'feature_importance': feature_importance.to_dict('records'),
            'performance': classification_report(y_test, y_pred, output_dict=True)
        }
        
        return self.predictive_model
    
    def generate_customer_insights(self):
        """
        Generate comprehensive customer journey and retention insights.
        
        Returns:
            dict: Comprehensive customer insights
        """
        print("\n=== GENERATING CUSTOMER INSIGHTS ===")
        
        if self.customer_data is None:
            self.load_data()
        
        # Customer journey analysis (adapted for single-purchase customers)
        journey_insights = {}
        
        # 1. Customer acquisition patterns
        acquisition_by_month = self.customer_data.groupby(
            self.customer_data['first_order_date'].dt.to_period('M')
        ).agg({
            'customer_id': 'count',
            'total_revenue': ['sum', 'mean']
        })
        
        acquisition_by_month.columns = ['new_customers', 'total_revenue', 'avg_revenue']
        
        # 2. Customer value distribution
        value_distribution = self.customer_data['clv_category'].value_counts(normalize=True) * 100
        
        # 3. Customer lifecycle insights (adapted for single purchases)
        lifecycle_insights = self.customer_data.groupby('customer_segment').agg({
            'customer_id': 'count',
            'total_revenue': ['mean', 'sum'],
            'avg_delivery_experience': 'mean',
            'days_since_last_order': 'mean'
        }).round(2)
        
        # 4. Key business insights
        total_customers = len(self.customer_data)
        total_revenue = self.customer_data['total_revenue'].sum()
        avg_order_value = self.customer_data['total_revenue'].mean()
        
        # High-value customer characteristics
        high_value_customers = self.customer_data[
            self.customer_data['clv_category'].isin(['High Value', 'VIP'])
        ]
        
        insights_summary = {
            'total_customers': total_customers,
            'total_revenue': total_revenue,
            'average_order_value': avg_order_value,
            'high_value_customer_rate': len(high_value_customers) / total_customers * 100,
            'avg_delivery_days': self.customer_data['avg_delivery_experience'].mean(),
            'delivery_reliability_rate': (self.customer_data['delivery_reliability'] == 1.0).mean() * 100
        }
        
        print("Key Customer Insights:")
        for key, value in insights_summary.items():
            if isinstance(value, float):
                print(f"{key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value:,}")
        
        # Store all insights
        self.insights.update({
            'acquisition_patterns': acquisition_by_month.to_dict('index'),
            'value_distribution': value_distribution.to_dict(),
            'lifecycle_insights': lifecycle_insights.to_dict('index'),
            'summary_metrics': insights_summary
        })
        
        return self.insights
    
    def create_customer_segments_report(self):
        """
        Create a comprehensive customer segmentation report.
        
        Returns:
            pd.DataFrame: Detailed segmentation report
        """
        print("\n=== CREATING CUSTOMER SEGMENTATION REPORT ===")
        
        if self.customer_data is None:
            self.load_data()
        
        # Create comprehensive segment analysis
        segment_report = self.customer_data.groupby('customer_segment').agg({
            'customer_id': 'count',
            'total_revenue': ['sum', 'mean', 'std'],
            'avg_delivery_experience': ['mean', 'std'],
            'delivery_reliability': 'mean',
            'days_since_last_order': 'mean',
            'recency_score': 'mean',
            'frequency_score': 'mean',
            'monetary_score': 'mean'
        }).round(2)
        
        # Flatten column names
        segment_report.columns = [
            'customer_count', 'total_revenue', 'avg_revenue', 'revenue_std',
            'avg_delivery_days', 'delivery_days_std', 'delivery_reliability',
            'avg_days_since_last_order', 'avg_recency_score', 'avg_frequency_score',
            'avg_monetary_score'
        ]
        
        # Add percentage and revenue share
        segment_report['customer_percentage'] = (
            segment_report['customer_count'] / segment_report['customer_count'].sum() * 100
        ).round(2)
        
        segment_report['revenue_share'] = (
            segment_report['total_revenue'] / segment_report['total_revenue'].sum() * 100
        ).round(2)
        
        # Sort by revenue contribution
        segment_report = segment_report.sort_values('revenue_share', ascending=False)
        
        print("Customer Segmentation Report:")
        print(segment_report)
        
        return segment_report
    
    def run_complete_analysis(self):
        """
        Run the complete customer analytics pipeline.
        
        Returns:
            dict: Complete analysis results
        """
        print("🚀 STARTING COMPLETE CUSTOMER ANALYTICS ANALYSIS")
        print("=" * 60)
        
        # Load data
        self.load_data()
        
        # Run all analyses
        rfm_results = self.perform_rfm_analysis()
        clv_results = self.calculate_customer_lifetime_value()
        delivery_results = self.analyze_delivery_experience_impact()
        model_results = self.build_high_value_customer_model()
        insights = self.generate_customer_insights()
        segment_report = self.create_customer_segments_report()
        
        # Compile complete results
        complete_results = {
            'rfm_analysis': rfm_results,
            'clv_analysis': clv_results,
            'delivery_impact': delivery_results,
            'predictive_model': model_results,
            'customer_insights': insights,
            'segmentation_report': segment_report,
            'data_summary': {
                'total_customers': len(self.customer_data),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_period': f"{self.customer_data['first_order_date'].min()} to {self.customer_data['last_order_date'].max()}"
            }
        }
        
        print("\n✅ CUSTOMER ANALYTICS ANALYSIS COMPLETE!")
        print(f"📊 Analyzed {len(self.customer_data):,} customers")
        print(f"🎯 Identified {len(self.customer_data[self.customer_data['clv_category'].isin(['High Value', 'VIP'])]):,} high-value customers")
        
        return complete_results


def main():
    """Main execution function for customer analytics."""
    
    # Initialize customer analytics
    analytics = CustomerAnalytics()
    
    # Run complete analysis
    results = analytics.run_complete_analysis()
    
    # Save results summary
    print(f"\n💾 Saving analysis results...")
    
    # Save key insights to a summary file
    summary_file = 'customer_analytics_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("CUSTOMER ANALYTICS SUMMARY REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        # Write key metrics
        summary_metrics = results['customer_insights']['summary_metrics']
        f.write("KEY METRICS:\n")
        for key, value in summary_metrics.items():
            if isinstance(value, float):
                f.write(f"{key.replace('_', ' ').title()}: {value:.2f}\n")
            else:
                f.write(f"{key.replace('_', ' ').title()}: {value:,}\n")
        
        f.write(f"\nAnalysis completed: {results['data_summary']['analysis_date']}\n")
        f.write(f"Data period: {results['data_summary']['data_period']}\n")
    
    print(f"📄 Summary saved to: {summary_file}")
    
    return results


if __name__ == "__main__":
    results = main()