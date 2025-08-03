"""
Payment Behavior and Operations Analysis Module

This module analyzes payment behaviors, operational performance metrics,
and their relationships with customer satisfaction across Brazilian regions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime
import logging

# Configure logging and warnings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('default')
sns.set_palette("husl")

class PaymentOperationsAnalyzer:
    """
    Comprehensive analyzer for payment behavior and operational performance.
    """
    
    def __init__(self):
        """Initialize the analyzer and load datasets."""
        self.payment_data = None
        self.customer_data = None
        self.analysis_results = {}
        self.insights = []
        
        # Load the datasets
        self._load_datasets()
        
    def _load_datasets(self):
        """Load cleaned and feature-engineered datasets."""
        try:
            logger.info("Loading payment operations and customer datasets...")
            
            # Load payment operations data (feature-engineered)
            self.payment_data = pd.read_csv('data/feature_engineered/payment_operations.csv')
            
            # Convert datetime columns
            datetime_cols = ['order_purchase_timestamp', 'order_approved_at', 
                           'order_delivered_carrier_date', 'order_delivered_customer_date', 
                           'order_estimated_delivery_date']
            
            for col in datetime_cols:
                if col in self.payment_data.columns:
                    self.payment_data[col] = pd.to_datetime(self.payment_data[col], errors='coerce')
            
            # Load customer data for regional analysis
            self.customer_data = pd.read_csv('data/cleaned/cleaned_customers.csv')
            
            # Merge customer location data with payment data
            self.payment_data = self.payment_data.merge(
                self.customer_data[['customer_id', 'customer_state', 'customer_city']], 
                on='customer_id', 
                how='left'
            )
            
            logger.info(f"Loaded payment data: {len(self.payment_data):,} records")
            logger.info(f"Payment methods available: {self.payment_data['payment_type'].unique()}")
            logger.info(f"States covered: {self.payment_data['customer_state'].nunique()}")
            
        except Exception as e:
            logger.error(f"Error loading datasets: {str(e)}")
            raise    

    def analyze_payment_method_preferences(self):
        """Analyze payment method preferences by region and customer segment."""
        logger.info("Analyzing payment method preferences by region...")
        
        # Overall payment method distribution
        payment_distribution = self.payment_data['payment_type'].value_counts(normalize=True) * 100
        
        # Payment methods by state
        state_payment = pd.crosstab(
            self.payment_data['customer_state'], 
            self.payment_data['payment_type'], 
            normalize='index'
        ) * 100
        
        # Payment methods by installment usage
        installment_analysis = self.payment_data.groupby('payment_type').agg({
            'payment_installments': ['mean', 'median', 'std'],
            'payment_value': ['mean', 'median'],
            'order_id': 'count'
        }).round(2)
        
        installment_analysis.columns = [
            'avg_installments', 'median_installments', 'std_installments',
            'avg_payment_value', 'median_payment_value', 'order_count'
        ]
        
        # Regional payment behavior analysis
        regional_payment = self.payment_data.groupby(['customer_state', 'payment_type']).agg({
            'payment_value': ['mean', 'count'],
            'payment_installments': 'mean'
        }).reset_index()
        
        regional_payment.columns = [
            'customer_state', 'payment_type', 'avg_payment_value', 
            'payment_count', 'avg_installments'
        ]
        
        # Calculate payment method market share by state
        regional_payment['state_total'] = regional_payment.groupby('customer_state')['payment_count'].transform('sum')
        regional_payment['market_share'] = (regional_payment['payment_count'] / regional_payment['state_total']) * 100
        
        self.analysis_results['payment_distribution'] = payment_distribution
        self.analysis_results['state_payment_preferences'] = state_payment
        self.analysis_results['installment_analysis'] = installment_analysis
        self.analysis_results['regional_payment_behavior'] = regional_payment
        
        # Generate insights
        dominant_payment = payment_distribution.index[0]
        dominant_percentage = payment_distribution.iloc[0]
        
        self.insights.append(f"Credit card is the dominant payment method, accounting for {dominant_percentage:.1f}% of all transactions")
        
        # Find states with highest credit card usage
        if 'credit_card' in state_payment.columns:
            top_cc_states = state_payment['credit_card'].nlargest(3)
            self.insights.append(f"States with highest credit card usage: {', '.join(top_cc_states.index)} ({top_cc_states.iloc[0]:.1f}% average)")
        
        return {
            'payment_distribution': payment_distribution,
            'regional_preferences': state_payment,
            'installment_patterns': installment_analysis,
            'regional_behavior': regional_payment
        }    

    def analyze_installment_satisfaction_relationship(self):
        """Examine relationship between installment plans and customer satisfaction."""
        logger.info("Analyzing installment plans vs customer satisfaction...")
        
        # Filter data with review scores
        satisfaction_data = self.payment_data[self.payment_data['review_score'].notna()].copy()
        
        # Create installment categories
        satisfaction_data['installment_category'] = pd.cut(
            satisfaction_data['payment_installments'],
            bins=[0, 1, 3, 6, 12, float('inf')],
            labels=['Single Payment', '2-3 Installments', '4-6 Installments', 
                   '7-12 Installments', '12+ Installments'],
            include_lowest=True
        )
        
        # Satisfaction by installment category
        installment_satisfaction = satisfaction_data.groupby('installment_category').agg({
            'review_score': ['mean', 'std', 'count'],
            'payment_value': ['mean', 'median'],
            'delivery_days': 'mean',
            'on_time_delivery': lambda x: x.sum() / len(x) * 100
        }).round(2)
        
        installment_satisfaction.columns = [
            'avg_satisfaction', 'satisfaction_std', 'review_count',
            'avg_payment_value', 'median_payment_value', 'avg_delivery_days',
            'on_time_delivery_rate'
        ]
        
        # Satisfaction by payment method
        payment_satisfaction = satisfaction_data.groupby('payment_type').agg({
            'review_score': ['mean', 'std', 'count'],
            'payment_installments': 'mean',
            'payment_value': 'mean',
            'on_time_delivery': lambda x: x.sum() / len(x) * 100
        }).round(2)
        
        payment_satisfaction.columns = [
            'avg_satisfaction', 'satisfaction_std', 'review_count',
            'avg_installments', 'avg_payment_value', 'on_time_delivery_rate'
        ]
        
        # Correlation analysis
        correlation_data = satisfaction_data[['payment_installments', 'payment_value', 
                                           'review_score', 'delivery_days']].corr()
        
        # Regional satisfaction analysis
        regional_satisfaction = satisfaction_data.groupby(['customer_state', 'payment_type']).agg({
            'review_score': 'mean',
            'payment_installments': 'mean',
            'on_time_delivery': lambda x: x.sum() / len(x) * 100,
            'order_id': 'count'
        }).reset_index()
        
        regional_satisfaction.columns = [
            'customer_state', 'payment_type', 'avg_satisfaction',
            'avg_installments', 'on_time_delivery_rate', 'order_count'
        ]
        
        # Filter for significant sample sizes
        regional_satisfaction = regional_satisfaction[regional_satisfaction['order_count'] >= 50]
        
        self.analysis_results['installment_satisfaction'] = installment_satisfaction
        self.analysis_results['payment_satisfaction'] = payment_satisfaction
        self.analysis_results['payment_correlations'] = correlation_data
        self.analysis_results['regional_satisfaction'] = regional_satisfaction
        
        # Generate insights
        best_satisfaction_payment = payment_satisfaction['avg_satisfaction'].idxmax()
        best_satisfaction_score = payment_satisfaction.loc[best_satisfaction_payment, 'avg_satisfaction']
        
        self.insights.append(f"{best_satisfaction_payment} payments show highest satisfaction ({best_satisfaction_score:.2f}/5.0)")
        
        # Installment insights
        if len(installment_satisfaction) > 0:
            best_installment_category = installment_satisfaction['avg_satisfaction'].idxmax()
            self.insights.append(f"Customers using {best_installment_category} show highest satisfaction")
        
        return {
            'installment_satisfaction': installment_satisfaction,
            'payment_satisfaction': payment_satisfaction,
            'correlations': correlation_data,
            'regional_satisfaction': regional_satisfaction
        }    

    def calculate_operational_performance_metrics(self):
        """Calculate comprehensive operational performance metrics."""
        logger.info("Calculating operational performance metrics...")
        
        # Overall operational metrics
        total_orders = len(self.payment_data)
        delivered_orders = len(self.payment_data[self.payment_data['order_status'] == 'delivered'])
        
        # Delivery performance metrics
        delivery_metrics = {
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
            'delivery_rate': (delivered_orders / total_orders) * 100,
            'avg_delivery_days': self.payment_data['delivery_days'].mean(),
            'median_delivery_days': self.payment_data['delivery_days'].median(),
            'on_time_delivery_rate': (self.payment_data['on_time_delivery'].sum() / 
                                    self.payment_data['on_time_delivery'].count()) * 100,
            'avg_processing_days': self.payment_data['processing_days'].mean(),
            'avg_shipping_days': self.payment_data['shipping_days'].mean()
        }
        
        # Performance by payment method
        payment_performance = self.payment_data.groupby('payment_type').agg({
            'delivery_days': ['mean', 'median', 'std'],
            'on_time_delivery': lambda x: x.sum() / len(x) * 100,
            'processing_days': 'mean',
            'shipping_days': 'mean',
            'review_score': 'mean',
            'order_id': 'count'
        }).round(2)
        
        payment_performance.columns = [
            'avg_delivery_days', 'median_delivery_days', 'delivery_days_std',
            'on_time_rate', 'avg_processing_days', 'avg_shipping_days',
            'avg_satisfaction', 'order_count'
        ]
        
        # Performance by state
        state_performance = self.payment_data.groupby('customer_state').agg({
            'delivery_days': ['mean', 'median'],
            'on_time_delivery': lambda x: x.sum() / len(x) * 100,
            'review_score': 'mean',
            'payment_value': 'mean',
            'order_id': 'count'
        }).round(2)
        
        state_performance.columns = [
            'avg_delivery_days', 'median_delivery_days', 'on_time_rate',
            'avg_satisfaction', 'avg_order_value', 'order_count'
        ]
        
        # Sort by performance metrics
        state_performance = state_performance.sort_values('on_time_rate', ascending=False)
        
        # Delivery delay impact analysis
        delay_impact = self.payment_data.groupby('delivery_accuracy').agg({
            'review_score': 'mean',
            'order_id': 'count'
        }).round(2)
        
        delay_impact.columns = ['avg_satisfaction', 'order_count']
        delay_impact['satisfaction_impact'] = delay_impact['avg_satisfaction'] - delivery_metrics.get('avg_satisfaction', 4.0)
        
        # Review rate analysis
        review_analysis = self.payment_data.groupby('payment_type').agg({
            'review_score': lambda x: x.notna().sum(),
            'order_id': 'count'
        })
        
        review_analysis['review_rate'] = (review_analysis['review_score'] / review_analysis['order_id']) * 100
        review_analysis = review_analysis.round(2)
        
        self.analysis_results['delivery_metrics'] = delivery_metrics
        self.analysis_results['payment_performance'] = payment_performance
        self.analysis_results['state_performance'] = state_performance
        self.analysis_results['delay_impact'] = delay_impact
        self.analysis_results['review_rates'] = review_analysis
        
        # Generate insights
        best_performing_state = state_performance.index[0]
        best_on_time_rate = state_performance.iloc[0]['on_time_rate']
        
        self.insights.append(f"Best performing state: {best_performing_state} with {best_on_time_rate:.1f}% on-time delivery")
        
        worst_performing_state = state_performance.index[-1]
        worst_on_time_rate = state_performance.iloc[-1]['on_time_rate']
        
        self.insights.append(f"Improvement opportunity: {worst_performing_state} with {worst_on_time_rate:.1f}% on-time delivery")
        
        return {
            'overall_metrics': delivery_metrics,
            'payment_performance': payment_performance,
            'state_performance': state_performance,
            'delay_impact': delay_impact,
            'review_rates': review_analysis
        }  
  
    def analyze_regional_payment_behavior(self):
        """Analyze regional payment behavior and economic correlations."""
        logger.info("Analyzing regional payment behavior and economic patterns...")
        
        # Regional payment patterns
        regional_analysis = self.payment_data.groupby('customer_state').agg({
            'payment_value': ['mean', 'median', 'std'],
            'payment_installments': ['mean', 'median'],
            'review_score': 'mean',
            'delivery_days': 'mean',
            'order_id': 'count'
        }).round(2)
        
        regional_analysis.columns = [
            'avg_payment_value', 'median_payment_value', 'payment_value_std',
            'avg_installments', 'median_installments', 'avg_satisfaction',
            'avg_delivery_days', 'order_count'
        ]
        
        # Payment method preferences by region
        regional_payment_mix = pd.crosstab(
            self.payment_data['customer_state'],
            self.payment_data['payment_type'],
            normalize='index'
        ) * 100
        
        # Economic indicators (based on payment behavior)
        regional_analysis['payment_diversity'] = regional_payment_mix.apply(
            lambda x: 1 - sum((x/100)**2), axis=1
        )  # Herfindahl index for payment method diversity
        
        regional_analysis['installment_preference'] = np.where(
            regional_analysis['avg_installments'] > regional_analysis['avg_installments'].median(),
            'High Installment Usage', 'Low Installment Usage'
        )
        
        regional_analysis['economic_segment'] = pd.cut(
            regional_analysis['avg_payment_value'],
            bins=3,
            labels=['Lower Economic Segment', 'Middle Economic Segment', 'Higher Economic Segment']
        )
        
        # Seasonal payment behavior
        seasonal_payment = self.payment_data.groupby(['order_month', 'payment_type']).agg({
            'payment_value': 'mean',
            'payment_installments': 'mean',
            'order_id': 'count'
        }).reset_index()
        
        # Holiday season analysis
        holiday_payment = self.payment_data.groupby(['is_holiday_season', 'payment_type']).agg({
            'payment_value': 'mean',
            'payment_installments': 'mean',
            'order_id': 'count'
        }).reset_index()
        
        self.analysis_results['regional_analysis'] = regional_analysis
        self.analysis_results['regional_payment_mix'] = regional_payment_mix
        self.analysis_results['seasonal_payment'] = seasonal_payment
        self.analysis_results['holiday_payment'] = holiday_payment
        
        # Generate insights
        highest_value_state = regional_analysis['avg_payment_value'].idxmax()
        highest_value = regional_analysis.loc[highest_value_state, 'avg_payment_value']
        
        self.insights.append(f"Highest average payment value: {highest_value_state} (R$ {highest_value:.2f})")
        
        # Installment usage insights
        high_installment_states = regional_analysis[
            regional_analysis['installment_preference'] == 'High Installment Usage'
        ].index.tolist()
        
        if high_installment_states:
            self.insights.append(f"States with high installment usage: {', '.join(high_installment_states[:3])}")
        
        return {
            'regional_patterns': regional_analysis,
            'payment_mix': regional_payment_mix,
            'seasonal_patterns': seasonal_payment,
            'holiday_patterns': holiday_payment
        }    

    def generate_operational_recommendations(self):
        """Generate actionable operational improvement recommendations."""
        logger.info("Generating operational improvement recommendations...")
        
        recommendations = []
        
        # Payment method optimization
        if 'payment_satisfaction' in self.analysis_results:
            payment_sat = self.analysis_results['payment_satisfaction']
            best_payment = payment_sat['avg_satisfaction'].idxmax()
            worst_payment = payment_sat['avg_satisfaction'].idxmin()
            
            recommendations.append({
                'category': 'Payment Method Optimization',
                'priority': 'High',
                'recommendation': f'Promote {best_payment} payments as they show highest satisfaction ({payment_sat.loc[best_payment, "avg_satisfaction"]:.2f}/5.0)',
                'impact': 'Customer Satisfaction',
                'implementation': f'Offer incentives for {best_payment} usage, improve {worst_payment} experience'
            })
        
        # Regional performance improvements
        if 'state_performance' in self.analysis_results:
            state_perf = self.analysis_results['state_performance']
            worst_states = state_perf.tail(3).index.tolist()
            
            recommendations.append({
                'category': 'Regional Operations',
                'priority': 'High',
                'recommendation': f'Focus delivery improvements in {", ".join(worst_states)} - lowest on-time delivery rates',
                'impact': 'Operational Efficiency',
                'implementation': 'Increase local fulfillment centers, optimize logistics partnerships'
            })
        
        # Installment strategy
        if 'installment_satisfaction' in self.analysis_results:
            installment_sat = self.analysis_results['installment_satisfaction']
            if len(installment_sat) > 0:
                best_installment = installment_sat['avg_satisfaction'].idxmax()
                
                recommendations.append({
                    'category': 'Payment Terms',
                    'priority': 'Medium',
                    'recommendation': f'Optimize installment offerings - {best_installment} show highest satisfaction',
                    'impact': 'Customer Experience',
                    'implementation': 'Adjust installment options, provide clear payment terms'
                })
        
        # Delivery performance
        if 'delivery_metrics' in self.analysis_results:
            delivery_metrics = self.analysis_results['delivery_metrics']
            on_time_rate = delivery_metrics.get('on_time_delivery_rate', 0)
            
            if on_time_rate < 80:
                recommendations.append({
                    'category': 'Delivery Operations',
                    'priority': 'Critical',
                    'recommendation': f'Improve on-time delivery rate from {on_time_rate:.1f}% to 85%+',
                    'impact': 'Customer Retention',
                    'implementation': 'Review logistics processes, set realistic delivery estimates'
                })
        
        # Review engagement
        if 'review_rates' in self.analysis_results:
            review_rates = self.analysis_results['review_rates']
            low_review_payments = review_rates[review_rates['review_rate'] < 50].index.tolist()
            
            if low_review_payments:
                recommendations.append({
                    'category': 'Customer Engagement',
                    'priority': 'Medium',
                    'recommendation': f'Increase review rates for {", ".join(low_review_payments)} payments',
                    'impact': 'Data Quality & Insights',
                    'implementation': 'Implement review incentives, simplify review process'
                })
        
        self.analysis_results['recommendations'] = recommendations
        
        return recommendations    

    def create_visualizations(self):
        """Create comprehensive visualizations for payment and operations analysis."""
        logger.info("Creating payment and operations visualizations...")
        
        # Set up the plotting style
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        visualizations = {}
        
        # 1. Payment Method Distribution
        if 'payment_distribution' in self.analysis_results:
            fig, ax = plt.subplots(figsize=(10, 6))
            payment_dist = self.analysis_results['payment_distribution']
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            bars = ax.bar(payment_dist.index, payment_dist.values, color=colors[:len(payment_dist)])
            
            ax.set_title('Payment Method Distribution', fontsize=16, fontweight='bold')
            ax.set_ylabel('Percentage of Orders (%)')
            ax.set_xlabel('Payment Method')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{height:.1f}%', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('reports/payment_method_distribution.png', dpi=300, bbox_inches='tight')
            visualizations['payment_distribution'] = fig
        
        # 2. Satisfaction by Payment Method
        if 'payment_satisfaction' in self.analysis_results:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            payment_sat = self.analysis_results['payment_satisfaction']
            
            # Satisfaction scores
            bars1 = ax1.bar(payment_sat.index, payment_sat['avg_satisfaction'], 
                           color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'][:len(payment_sat)])
            ax1.set_title('Average Satisfaction by Payment Method')
            ax1.set_ylabel('Average Review Score')
            ax1.set_ylim(0, 5)
            
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                        f'{height:.2f}', ha='center', va='bottom')
            
            # On-time delivery rates
            bars2 = ax2.bar(payment_sat.index, payment_sat['on_time_delivery_rate'],
                           color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'][:len(payment_sat)])
            ax2.set_title('On-Time Delivery Rate by Payment Method')
            ax2.set_ylabel('On-Time Delivery Rate (%)')
            
            for bar in bars2:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('reports/payment_satisfaction_analysis.png', dpi=300, bbox_inches='tight')
            visualizations['payment_satisfaction'] = fig
        
        # 3. Regional Performance Heatmap
        if 'state_performance' in self.analysis_results:
            fig, ax = plt.subplots(figsize=(12, 8))
            state_perf = self.analysis_results['state_performance'].head(15)  # Top 15 states
            
            # Create heatmap data
            heatmap_data = state_perf[['on_time_rate', 'avg_satisfaction', 'avg_delivery_days']].T
            
            sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlGn', 
                       ax=ax, cbar_kws={'label': 'Performance Score'})
            ax.set_title('Regional Performance Heatmap (Top 15 States)', fontsize=16, fontweight='bold')
            ax.set_xlabel('States')
            ax.set_ylabel('Performance Metrics')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('reports/regional_performance_heatmap.png', dpi=300, bbox_inches='tight')
            visualizations['regional_performance'] = fig
        
        # 4. Installment vs Satisfaction Analysis
        if 'installment_satisfaction' in self.analysis_results:
            fig, ax = plt.subplots(figsize=(12, 6))
            installment_sat = self.analysis_results['installment_satisfaction']
            
            x_pos = range(len(installment_sat))
            bars = ax.bar(x_pos, installment_sat['avg_satisfaction'], 
                         color='#45B7D1', alpha=0.7)
            
            ax.set_title('Customer Satisfaction by Installment Category', fontsize=16, fontweight='bold')
            ax.set_ylabel('Average Satisfaction Score')
            ax.set_xlabel('Installment Category')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(installment_sat.index, rotation=45)
            ax.set_ylim(0, 5)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       f'{height:.2f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig('reports/installment_satisfaction_analysis.png', dpi=300, bbox_inches='tight')
            visualizations['installment_satisfaction'] = fig
        
        return visualizations    

    def generate_comprehensive_report(self):
        """Generate a comprehensive payment and operations analysis report."""
        logger.info("Generating comprehensive payment and operations report...")
        
        report_sections = []
        
        # Executive Summary
        report_sections.append("# Payment Behavior and Operations Analysis Report")
        report_sections.append("=" * 60)
        report_sections.append("")
        report_sections.append("## Executive Summary")
        report_sections.append("")
        
        # Add key insights
        for insight in self.insights:
            report_sections.append(f"• {insight}")
        report_sections.append("")
        
        # Payment Method Analysis
        if 'payment_distribution' in self.analysis_results:
            report_sections.append("## Payment Method Analysis")
            report_sections.append("")
            
            payment_dist = self.analysis_results['payment_distribution']
            report_sections.append("### Payment Method Distribution:")
            for method, percentage in payment_dist.items():
                report_sections.append(f"• {method}: {percentage:.1f}%")
            report_sections.append("")
        
        # Regional Analysis
        if 'regional_analysis' in self.analysis_results:
            report_sections.append("## Regional Payment Behavior")
            report_sections.append("")
            
            regional = self.analysis_results['regional_analysis']
            top_states = regional.nlargest(5, 'avg_payment_value')
            
            report_sections.append("### Top 5 States by Average Payment Value:")
            for state, row in top_states.iterrows():
                report_sections.append(f"• {state}: R$ {row['avg_payment_value']:.2f}")
            report_sections.append("")
        
        # Operational Performance
        if 'delivery_metrics' in self.analysis_results:
            report_sections.append("## Operational Performance Metrics")
            report_sections.append("")
            
            metrics = self.analysis_results['delivery_metrics']
            report_sections.append(f"• Total Orders Analyzed: {metrics['total_orders']:,}")
            report_sections.append(f"• Delivery Rate: {metrics['delivery_rate']:.1f}%")
            report_sections.append(f"• Average Delivery Time: {metrics['avg_delivery_days']:.1f} days")
            report_sections.append(f"• On-Time Delivery Rate: {metrics['on_time_delivery_rate']:.1f}%")
            report_sections.append("")
        
        # Recommendations
        if 'recommendations' in self.analysis_results:
            report_sections.append("## Strategic Recommendations")
            report_sections.append("")
            
            for i, rec in enumerate(self.analysis_results['recommendations'], 1):
                report_sections.append(f"### {i}. {rec['category']} (Priority: {rec['priority']})")
                report_sections.append(f"**Recommendation:** {rec['recommendation']}")
                report_sections.append(f"**Impact:** {rec['impact']}")
                report_sections.append(f"**Implementation:** {rec['implementation']}")
                report_sections.append("")
        
        # Methodology
        report_sections.append("## Methodology")
        report_sections.append("")
        report_sections.append("This analysis was conducted using:")
        report_sections.append("• Brazilian E-commerce dataset with payment and delivery data")
        report_sections.append("• Statistical analysis of payment preferences by region")
        report_sections.append("• Correlation analysis between payment methods and satisfaction")
        report_sections.append("• Operational performance metrics calculation")
        report_sections.append("• Regional economic behavior analysis")
        report_sections.append("")
        
        report_content = "\n".join(report_sections)
        
        # Save report
        with open('reports/payment_operations_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info("Payment and operations report saved to reports/payment_operations_report.md")
        
        return report_content
    
    def run_complete_analysis(self):
        """Run the complete payment behavior and operations analysis."""
        logger.info("Starting comprehensive payment behavior and operations analysis...")
        
        try:
            # Run all analysis components
            payment_preferences = self.analyze_payment_method_preferences()
            installment_analysis = self.analyze_installment_satisfaction_relationship()
            operational_metrics = self.calculate_operational_performance_metrics()
            regional_behavior = self.analyze_regional_payment_behavior()
            recommendations = self.generate_operational_recommendations()
            
            # Create visualizations
            visualizations = self.create_visualizations()
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report()
            
            logger.info("Payment behavior and operations analysis completed successfully!")
            
            return {
                'payment_preferences': payment_preferences,
                'installment_analysis': installment_analysis,
                'operational_metrics': operational_metrics,
                'regional_behavior': regional_behavior,
                'recommendations': recommendations,
                'visualizations': visualizations,
                'report': report,
                'insights': self.insights
            }
            
        except Exception as e:
            logger.error(f"Error in payment analysis: {str(e)}")
            raise


def main():
    """Main function to run the payment behavior and operations analysis."""
    print("🔄 Starting Payment Behavior and Operations Analysis...")
    print("=" * 60)
    
    try:
        # Initialize analyzer
        analyzer = PaymentOperationsAnalyzer()
        
        # Run complete analysis
        results = analyzer.run_complete_analysis()
        
        print("\n✅ Analysis completed successfully!")
        print(f"📊 Generated {len(results['visualizations'])} visualizations")
        print(f"💡 Identified {len(results['insights'])} key insights")
        print(f"📋 Created {len(results['recommendations'])} recommendations")
        
        print("\n🔍 Key Insights:")
        for insight in results['insights']:
            print(f"• {insight}")
        
        print(f"\n📄 Comprehensive report saved to: reports/payment_operations_report.md")
        print("\n🎯 Analysis Focus Areas Completed:")
        print("• Payment method preferences by region and customer segment")
        print("• Installment plans vs customer satisfaction relationship")
        print("• Operational performance metrics and delivery analysis")
        print("• Regional payment behavior and economic correlations")
        print("• Strategic recommendations for operational improvements")
        
    except Exception as e:
        print(f"❌ Error in analysis: {str(e)}")
        raise


if __name__ == "__main__":
    main()