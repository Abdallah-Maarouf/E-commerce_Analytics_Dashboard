"""
Market Expansion Analysis Module for Brazilian E-commerce Dataset

This module analyzes market penetration by Brazilian state, calculates untapped 
market potential, evaluates seller distribution vs customer demand, and analyzes 
delivery performance by geographic distance to generate expansion opportunity 
matrix and recommendations.

Requirements addressed: 2.1, 2.2, 2.3, 2.4, 2.5, 7.1, 7.2
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class MarketExpansionAnalyzer:
    """
    Comprehensive market expansion analysis for Brazilian e-commerce data.
    Analyzes geographic opportunities, seller distribution, and delivery performance.
    """
    
    def __init__(self):
        """Initialize the Market Expansion Analyzer."""
        self.market_data = None
        self.state_summary = None
        self.expansion_opportunities = None
        self.delivery_analysis = None
        self.insights = []
        
    def load_data(self):
        """Load the required datasets for market expansion analysis."""
        try:
            logger.info("Loading market expansion datasets...")
            
            # Load feature-engineered market expansion data
            self.market_data = pd.read_csv('data/feature_engineered/market_expansion.csv')
            
            # Load cleaned datasets for additional analysis
            self.orders_df = pd.read_csv('data/cleaned/cleaned_orders.csv')
            self.customers_df = pd.read_csv('data/cleaned/cleaned_customers.csv')
            self.sellers_df = pd.read_csv('data/cleaned/cleaned_sellers.csv')
            
            # Convert date columns
            self.orders_df['order_purchase_timestamp'] = pd.to_datetime(self.orders_df['order_purchase_timestamp'])
            if 'order_delivered_customer_date' in self.orders_df.columns:
                self.orders_df['order_delivered_customer_date'] = pd.to_datetime(self.orders_df['order_delivered_customer_date'])
            
            logger.info(f"Loaded market data with {len(self.market_data)} records")
            logger.info(f"Loaded {len(self.orders_df)} orders, {len(self.customers_df)} customers, {len(self.sellers_df)} sellers")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def analyze_market_penetration(self):
        """
        Analyze market penetration by Brazilian state to identify underserved areas.
        Addresses Requirements 2.1, 2.2
        """
        logger.info("Analyzing market penetration by Brazilian state...")
        
        # Create state-level summary from market data
        self.state_summary = self.market_data.groupby('state').agg({
            'customer_count': 'sum',
            'seller_count': 'sum', 
            'total_orders': 'sum',
            'total_revenue': 'sum',
            'cities_count': 'first',  # This should be the same for all cities in a state
            'market_opportunity_score': 'mean',
            'avg_delivery_days': 'mean',
            'on_time_rate': 'mean'
        }).reset_index()
        
        # Calculate additional penetration metrics
        self.state_summary['revenue_per_customer'] = np.where(
            self.state_summary['customer_count'] > 0,
            self.state_summary['total_revenue'] / self.state_summary['customer_count'],
            0
        )
        
        self.state_summary['orders_per_customer'] = np.where(
            self.state_summary['customer_count'] > 0,
            self.state_summary['total_orders'] / self.state_summary['customer_count'],
            0
        )
        
        self.state_summary['customer_to_seller_ratio'] = np.where(
            self.state_summary['seller_count'] > 0,
            self.state_summary['customer_count'] / self.state_summary['seller_count'],
            self.state_summary['customer_count']
        )
        
        # Market penetration categories
        self.state_summary['penetration_level'] = pd.cut(
            self.state_summary['customer_count'],
            bins=[0, 100, 1000, 5000, float('inf')],
            labels=['Very Low', 'Low', 'Medium', 'High']
        )
        
        # Sort by market opportunity score
        self.state_summary = self.state_summary.sort_values('market_opportunity_score', ascending=False)
        
        # Generate insights
        top_opportunity_states = self.state_summary.head(5)['state'].tolist()
        low_penetration_states = self.state_summary[
            self.state_summary['penetration_level'] == 'Very Low'
        ]['state'].tolist()
        
        self.insights.append({
            'category': 'Market Penetration',
            'insight': f"Top 5 expansion opportunity states: {', '.join(top_opportunity_states)}",
            'data': top_opportunity_states
        })
        
        self.insights.append({
            'category': 'Market Penetration', 
            'insight': f"States with very low penetration ({len(low_penetration_states)} total): {', '.join(low_penetration_states[:10])}{'...' if len(low_penetration_states) > 10 else ''}",
            'data': low_penetration_states
        })
        
        logger.info(f"Analyzed market penetration for {len(self.state_summary)} states")
        return self.state_summary
    
    def calculate_untapped_potential(self):
        """
        Calculate untapped market potential using population data, economic context, and realistic penetration benchmarks.
        Addresses Requirement 2.2
        """
        logger.info("Calculating untapped market potential with economic context...")
        
        # Brazilian state data (2020 census + economic data)
        state_data = {
            'SP': {'population': 46649132, 'gdp_per_capita': 56956, 'tier': 1, 'urban_rate': 0.96},
            'RJ': {'population': 17463349, 'gdp_per_capita': 51929, 'tier': 1, 'urban_rate': 0.97},
            'MG': {'population': 21411923, 'gdp_per_capita': 35219, 'tier': 1, 'urban_rate': 0.85},
            'BA': {'population': 15203934, 'gdp_per_capita': 22045, 'tier': 2, 'urban_rate': 0.73},
            'PR': {'population': 11597484, 'gdp_per_capita': 42791, 'tier': 2, 'urban_rate': 0.85},
            'RS': {'population': 11466630, 'gdp_per_capita': 45180, 'tier': 2, 'urban_rate': 0.85},
            'PE': {'population': 9674793, 'gdp_per_capita': 21077, 'tier': 2, 'urban_rate': 0.80},
            'CE': {'population': 9240580, 'gdp_per_capita': 18320, 'tier': 2, 'urban_rate': 0.75},
            'PA': {'population': 8777124, 'gdp_per_capita': 17179, 'tier': 3, 'urban_rate': 0.68},
            'SC': {'population': 7338473, 'gdp_per_capita': 46016, 'tier': 2, 'urban_rate': 0.84},
            'GO': {'population': 7206589, 'gdp_per_capita': 30544, 'tier': 2, 'urban_rate': 0.90},
            'MA': {'population': 7153262, 'gdp_per_capita': 14748, 'tier': 3, 'urban_rate': 0.64},
            'PB': {'population': 4059905, 'gdp_per_capita': 17687, 'tier': 3, 'urban_rate': 0.75},
            'AM': {'population': 4269995, 'gdp_per_capita': 23894, 'tier': 3, 'urban_rate': 0.79},
            'ES': {'population': 4108508, 'gdp_per_capita': 38177, 'tier': 2, 'urban_rate': 0.83},
            'MT': {'population': 3567234, 'gdp_per_capita': 49265, 'tier': 2, 'urban_rate': 0.82},
            'AL': {'population': 3365351, 'gdp_per_capita': 16463, 'tier': 3, 'urban_rate': 0.73},
            'PI': {'population': 3289290, 'gdp_per_capita': 14454, 'tier': 3, 'urban_rate': 0.66},
            'DF': {'population': 3094325, 'gdp_per_capita': 85830, 'tier': 1, 'urban_rate': 0.97},
            'MS': {'population': 2839188, 'gdp_per_capita': 39265, 'tier': 2, 'urban_rate': 0.86},
            'RN': {'population': 3560903, 'gdp_per_capita': 18690, 'tier': 3, 'urban_rate': 0.77},
            'RO': {'population': 1815278, 'gdp_per_capita': 26157, 'tier': 3, 'urban_rate': 0.74},
            'AC': {'population': 906876, 'gdp_per_capita': 18327, 'tier': 3, 'urban_rate': 0.73},
            'AP': {'population': 877613, 'gdp_per_capita': 19952, 'tier': 3, 'urban_rate': 0.90},
            'SE': {'population': 2338474, 'gdp_per_capita': 22942, 'tier': 3, 'urban_rate': 0.74},
            'TO': {'population': 1607363, 'gdp_per_capita': 22555, 'tier': 3, 'urban_rate': 0.79},
            'RR': {'population': 652713, 'gdp_per_capita': 22896, 'tier': 3, 'urban_rate': 0.76}
        }
        
        # Add economic context to state summary
        for state in self.state_summary['state']:
            if state in state_data:
                self.state_summary.loc[self.state_summary['state'] == state, 'population'] = state_data[state]['population']
                self.state_summary.loc[self.state_summary['state'] == state, 'gdp_per_capita'] = state_data[state]['gdp_per_capita']
                self.state_summary.loc[self.state_summary['state'] == state, 'tier'] = state_data[state]['tier']
                self.state_summary.loc[self.state_summary['state'] == state, 'urban_rate'] = state_data[state]['urban_rate']
        
        # Calculate realistic market penetration rate (customers per 1000 urban population)
        self.state_summary['urban_population'] = self.state_summary['population'] * self.state_summary['urban_rate']
        self.state_summary['penetration_rate'] = (
            self.state_summary['customer_count'] / self.state_summary['urban_population'] * 1000
        )
        
        # Calculate tier-specific penetration benchmarks (more realistic than national average)
        tier_benchmarks = {}
        for tier in [1, 2, 3]:
            tier_states = self.state_summary[self.state_summary['tier'] == tier]
            if len(tier_states) > 0:
                tier_benchmarks[tier] = (
                    tier_states['customer_count'].sum() / tier_states['urban_population'].sum() * 1000
                )
        
        # Calculate untapped potential using tier-specific benchmarks
        self.state_summary['benchmark_penetration'] = self.state_summary['tier'].map(tier_benchmarks)
        
        # Only consider untapped potential where current penetration is below benchmark
        self.state_summary['untapped_customers'] = np.maximum(
            0,
            (self.state_summary['benchmark_penetration'] * self.state_summary['urban_population'] / 1000) - 
            self.state_summary['customer_count']
        )
        
        # Adjust untapped potential by economic capacity (GDP per capita factor)
        national_avg_gdp = self.state_summary['gdp_per_capita'].mean()
        self.state_summary['economic_factor'] = np.minimum(
            2.0,  # Cap at 2x to avoid extreme values
            self.state_summary['gdp_per_capita'] / national_avg_gdp
        )
        
        self.state_summary['adjusted_untapped_customers'] = (
            self.state_summary['untapped_customers'] * self.state_summary['economic_factor']
        )
        
        # Calculate potential revenue with economic adjustment
        national_avg_revenue_per_customer = self.state_summary['total_revenue'].sum() / self.state_summary['customer_count'].sum()
        
        self.state_summary['untapped_revenue_potential'] = (
            self.state_summary['adjusted_untapped_customers'] * 
            national_avg_revenue_per_customer * 
            self.state_summary['economic_factor']
        )
        
        # Market potential score based on absolute opportunity size and economic viability
        max_revenue_potential = self.state_summary['untapped_revenue_potential'].max()
        if max_revenue_potential > 0:
            self.state_summary['market_potential_score'] = (
                self.state_summary['untapped_revenue_potential'] / max_revenue_potential
            )
        else:
            self.state_summary['market_potential_score'] = 0
        
        # Generate insights
        top_potential_states = self.state_summary.nlargest(5, 'untapped_customers')
        total_untapped_revenue = self.state_summary['untapped_revenue_potential'].sum()
        
        self.insights.append({
            'category': 'Untapped Potential',
            'insight': f"Total untapped revenue potential: R$ {total_untapped_revenue:,.2f}",
            'data': total_untapped_revenue
        })
        
        self.insights.append({
            'category': 'Untapped Potential',
            'insight': f"States with highest untapped customer potential: {', '.join(top_potential_states['state'].tolist())}",
            'data': top_potential_states[['state', 'untapped_customers', 'untapped_revenue_potential']].to_dict('records')
        })
        
        logger.info("Calculated untapped market potential for all states")
        return self.state_summary
    
    def evaluate_seller_distribution(self):
        """
        Evaluate seller distribution vs customer demand to identify optimization opportunities.
        Addresses Requirement 2.3
        """
        logger.info("Evaluating seller distribution vs customer demand...")
        
        # Analyze seller-customer imbalance
        self.state_summary['seller_shortage'] = np.where(
            self.state_summary['customer_to_seller_ratio'] > 50,  # Threshold for seller shortage
            True, False
        )
        
        # Calculate optimal seller count based on customer demand
        # Assume optimal ratio is 30 customers per seller (industry benchmark)
        optimal_ratio = 30
        self.state_summary['optimal_seller_count'] = np.ceil(
            self.state_summary['customer_count'] / optimal_ratio
        )
        
        self.state_summary['seller_gap'] = np.maximum(
            0,
            self.state_summary['optimal_seller_count'] - self.state_summary['seller_count']
        )
        
        # Seller distribution efficiency score
        self.state_summary['seller_efficiency_score'] = np.where(
            self.state_summary['optimal_seller_count'] > 0,
            np.minimum(1.0, self.state_summary['seller_count'] / self.state_summary['optimal_seller_count']),
            1.0
        )
        
        # Identify states with seller oversupply (too many sellers for demand)
        self.state_summary['seller_oversupply'] = np.maximum(
            0,
            self.state_summary['seller_count'] - self.state_summary['optimal_seller_count']
        )
        
        # Generate insights
        seller_shortage_states = self.state_summary[
            self.state_summary['seller_shortage'] == True
        ].sort_values('customer_to_seller_ratio', ascending=False)
        
        seller_oversupply_states = self.state_summary[
            self.state_summary['seller_oversupply'] > 0
        ].sort_values('seller_oversupply', ascending=False)
        
        total_seller_gap = self.state_summary['seller_gap'].sum()
        
        self.insights.append({
            'category': 'Seller Distribution',
            'insight': f"Total seller gap across all states: {total_seller_gap:,.0f} additional sellers needed",
            'data': total_seller_gap
        })
        
        if len(seller_shortage_states) > 0:
            self.insights.append({
                'category': 'Seller Distribution',
                'insight': f"States with severe seller shortage (>50:1 ratio): {', '.join(seller_shortage_states.head(5)['state'].tolist())}",
                'data': seller_shortage_states.head(10)[['state', 'customer_to_seller_ratio', 'seller_gap']].to_dict('records')
            })
        
        if len(seller_oversupply_states) > 0:
            self.insights.append({
                'category': 'Seller Distribution',
                'insight': f"States with seller oversupply: {', '.join(seller_oversupply_states.head(3)['state'].tolist())}",
                'data': seller_oversupply_states.head(5)[['state', 'seller_oversupply']].to_dict('records')
            })
        
        logger.info("Completed seller distribution analysis")
        return self.state_summary
    
    def analyze_delivery_performance_by_geography(self):
        """
        Analyze delivery performance by geographic distance and location.
        Addresses Requirement 2.4
        """
        logger.info("Analyzing delivery performance by geography...")
        
        # Merge orders with customer and seller location data
        orders_with_locations = self.orders_df.merge(
            self.customers_df[['customer_id', 'customer_state', 'customer_city']], 
            on='customer_id', how='left'
        )
        
        # Calculate delivery performance by customer state
        delivery_performance = orders_with_locations.groupby('customer_state').agg({
            'delivery_days': ['mean', 'median', 'std', 'count'],
            'on_time_delivery': 'mean',
            'order_id': 'count'
        }).reset_index()
        
        # Flatten column names
        delivery_performance.columns = [
            'state', 'avg_delivery_days', 'median_delivery_days', 'delivery_days_std',
            'delivery_count', 'on_time_rate', 'total_orders'
        ]
        
        # Delivery performance categories
        delivery_performance['delivery_performance_category'] = pd.cut(
            delivery_performance['avg_delivery_days'],
            bins=[0, 10, 15, 20, 25, float('inf')],
            labels=['Excellent (<10d)', 'Good (10-15d)', 'Average (15-20d)', 'Poor (20-25d)', 'Very Poor (>25d)']
        )
        
        # Merge with state summary
        self.state_summary = self.state_summary.merge(
            delivery_performance[['state', 'avg_delivery_days', 'median_delivery_days', 
                                'on_time_rate', 'delivery_performance_category']], 
            on='state', how='left', suffixes=('', '_detailed')
        )
        
        # Use detailed delivery data where available
        self.state_summary['avg_delivery_days'] = self.state_summary['avg_delivery_days_detailed'].fillna(
            self.state_summary['avg_delivery_days']
        )
        self.state_summary['on_time_rate'] = self.state_summary['on_time_rate_detailed'].fillna(
            self.state_summary['on_time_rate']
        )
        
        # Calculate delivery efficiency score (lower delivery days = higher score)
        max_delivery_days = self.state_summary['avg_delivery_days'].max()
        if max_delivery_days > 0:
            self.state_summary['delivery_efficiency_score'] = (
                1 - (self.state_summary['avg_delivery_days'] / max_delivery_days)
            ).fillna(0)
        else:
            self.state_summary['delivery_efficiency_score'] = 1.0
        
        # Generate insights
        best_delivery_states = self.state_summary.nsmallest(5, 'avg_delivery_days')
        worst_delivery_states = self.state_summary.nlargest(5, 'avg_delivery_days')
        
        avg_national_delivery = self.state_summary['avg_delivery_days'].mean()
        avg_national_ontime = self.state_summary['on_time_rate'].mean()
        
        self.insights.append({
            'category': 'Delivery Performance',
            'insight': f"National average delivery time: {avg_national_delivery:.1f} days, on-time rate: {avg_national_ontime:.1%}",
            'data': {'avg_delivery_days': avg_national_delivery, 'on_time_rate': avg_national_ontime}
        })
        
        self.insights.append({
            'category': 'Delivery Performance',
            'insight': f"Best delivery performance states: {', '.join(best_delivery_states['state'].tolist())}",
            'data': best_delivery_states[['state', 'avg_delivery_days', 'on_time_rate']].to_dict('records')
        })
        
        self.insights.append({
            'category': 'Delivery Performance',
            'insight': f"States needing delivery improvement: {', '.join(worst_delivery_states['state'].tolist())}",
            'data': worst_delivery_states[['state', 'avg_delivery_days', 'on_time_rate']].to_dict('records')
        })
        
        logger.info("Completed delivery performance analysis")
        return self.state_summary  
  
    def generate_expansion_opportunity_matrix(self):
        """
        Generate comprehensive expansion opportunity matrix with business-realistic scoring.
        Addresses Requirement 2.5
        """
        logger.info("Generating business-realistic expansion opportunity matrix...")
        
        # Calculate market size score (population + economic strength)
        max_population = self.state_summary['population'].max()
        max_gdp_per_capita = self.state_summary['gdp_per_capita'].max()
        
        self.state_summary['market_size_score'] = (
            (self.state_summary['population'] / max_population) * 0.6 +
            (self.state_summary['gdp_per_capita'] / max_gdp_per_capita) * 0.4
        )
        
        # Calculate growth potential score (untapped potential + low current penetration)
        max_untapped_revenue = self.state_summary['untapped_revenue_potential'].max()
        max_penetration = self.state_summary['penetration_rate'].max()
        
        if max_untapped_revenue > 0:
            untapped_score = self.state_summary['untapped_revenue_potential'] / max_untapped_revenue
        else:
            untapped_score = 0
            
        if max_penetration > 0:
            # Invert penetration rate - lower penetration = higher growth potential
            growth_potential_score = 1 - (self.state_summary['penetration_rate'] / max_penetration)
        else:
            growth_potential_score = 0
            
        self.state_summary['growth_potential_score'] = (
            untapped_score * 0.7 + growth_potential_score * 0.3
        )
        
        # Calculate operational feasibility score (delivery performance + infrastructure)
        max_delivery_days = self.state_summary['avg_delivery_days'].max()
        if max_delivery_days > 0:
            delivery_score = 1 - (self.state_summary['avg_delivery_days'] / max_delivery_days)
        else:
            delivery_score = 1.0
            
        # Urban rate as infrastructure proxy
        infrastructure_score = self.state_summary['urban_rate']
        
        self.state_summary['operational_feasibility_score'] = (
            delivery_score * 0.6 + infrastructure_score * 0.4
        )
        
        # Calculate competitive landscape score (seller efficiency)
        self.state_summary['competitive_score'] = self.state_summary['seller_efficiency_score'].fillna(0.5)
        
        # Combined expansion opportunity score with business-realistic weights
        weights = {
            'market_size_score': 0.35,           # Market size is crucial
            'growth_potential_score': 0.30,      # Growth potential is key
            'operational_feasibility_score': 0.20, # Operations must be feasible
            'competitive_score': 0.15            # Competition matters but less
        }
        
        self.state_summary['combined_opportunity_score'] = 0
        for metric, weight in weights.items():
            if metric in self.state_summary.columns:
                self.state_summary['combined_opportunity_score'] += (
                    self.state_summary[metric].fillna(0) * weight
                )
        
        # Expansion priority categories with business logic
        def categorize_expansion_priority(row):
            score = row['combined_opportunity_score']
            tier = row['tier']
            population = row['population']
            
            # Tier 1 states (major economic centers) - focus on optimization
            if tier == 1:
                if score >= 0.6:
                    return 'Optimization Priority'
                else:
                    return 'Maintain & Optimize'
            
            # Tier 2 states (regional capitals) - main expansion targets
            elif tier == 2:
                if score >= 0.7:
                    return 'High Priority'
                elif score >= 0.5:
                    return 'Medium Priority'
                else:
                    return 'Low Priority'
            
            # Tier 3 states (smaller markets) - selective expansion
            else:
                if score >= 0.6 and population > 2000000:  # Only larger Tier 3 states
                    return 'Medium Priority'
                elif score >= 0.4 and population > 1000000:
                    return 'Low Priority'
                else:
                    return 'Not Recommended'
        
        self.state_summary['expansion_priority'] = self.state_summary.apply(categorize_expansion_priority, axis=1)
        
        # Create expansion opportunity matrix
        self.expansion_opportunities = self.state_summary.copy()
        
        # Sort by combined opportunity score
        self.expansion_opportunities = self.expansion_opportunities.sort_values(
            'combined_opportunity_score', ascending=False
        )
        
        # Generate specific recommendations for top opportunity states
        top_opportunities = self.expansion_opportunities.head(10)
        
        recommendations = []
        for _, state_data in top_opportunities.iterrows():
            state = state_data['state']
            recommendations.append({
                'state': state,
                'priority': state_data['expansion_priority'],
                'opportunity_score': state_data['combined_opportunity_score'],
                'key_metrics': {
                    'customers': int(state_data['customer_count']),
                    'sellers': int(state_data['seller_count']),
                    'untapped_customers': int(state_data.get('untapped_customers', 0)),
                    'seller_gap': int(state_data.get('seller_gap', 0)),
                    'avg_delivery_days': state_data.get('avg_delivery_days', 0)
                },
                'recommendations': self._generate_state_recommendations(state_data)
            })
        
        self.insights.append({
            'category': 'Expansion Opportunities',
            'insight': f"Top 5 expansion priority states: {', '.join(top_opportunities.head(5)['state'].tolist())}",
            'data': recommendations[:5]
        })
        
        # Summary statistics
        priority_distribution = self.expansion_opportunities['expansion_priority'].value_counts()
        self.insights.append({
            'category': 'Expansion Opportunities',
            'insight': f"Expansion priority distribution: {dict(priority_distribution)}",
            'data': dict(priority_distribution)
        })
        
        logger.info("Generated expansion opportunity matrix")
        return self.expansion_opportunities, recommendations
    
    def _generate_state_recommendations(self, state_data):
        """Generate business-realistic recommendations for a state based on its metrics and tier."""
        recommendations = []
        state = state_data['state']
        tier = state_data.get('tier', 3)
        population = state_data.get('population', 0)
        gdp_per_capita = state_data.get('gdp_per_capita', 0)
        
        # Tier-specific recommendations
        if tier == 1:  # Major economic centers
            recommendations.append("Focus on market share optimization and premium services")
            if state_data.get('seller_gap', 0) > 50:
                recommendations.append(f"Scale seller network - recruit {int(state_data['seller_gap'])} additional premium sellers")
            if state_data.get('avg_delivery_days', 0) > 10:
                recommendations.append("Invest in same-day/next-day delivery infrastructure")
                
        elif tier == 2:  # Regional capitals - main expansion targets
            if state_data.get('untapped_revenue_potential', 0) > 5000000:  # > 5M potential
                recommendations.append("HIGH PRIORITY: Launch comprehensive market entry strategy")
                recommendations.append(f"Target market size: {population/1000000:.1f}M people, GDP per capita: R${gdp_per_capita:,.0f}")
            
            if state_data.get('seller_gap', 0) > 20:
                recommendations.append(f"Recruit {int(state_data['seller_gap'])} sellers through regional partnerships")
            
            if state_data.get('penetration_rate', 0) < 3:  # Low penetration in major market
                recommendations.append("Launch aggressive customer acquisition campaign")
                
        else:  # Tier 3 - selective expansion
            if population > 2000000 and state_data.get('untapped_revenue_potential', 0) > 2000000:
                recommendations.append("Consider selective market entry with local partnerships")
            elif population < 1000000:
                recommendations.append("NOT RECOMMENDED: Market too small for profitable expansion")
                return recommendations
        
        # Universal delivery recommendations
        if state_data.get('avg_delivery_days', 0) > 25:
            recommendations.append("CRITICAL: Establish regional distribution center")
        elif state_data.get('avg_delivery_days', 0) > 15:
            recommendations.append("Improve logistics partnerships for faster delivery")
        
        # Economic context recommendations
        if gdp_per_capita < 20000:
            recommendations.append("Focus on value-oriented products and flexible payment options")
        elif gdp_per_capita > 40000:
            recommendations.append("Opportunity for premium products and services")
        
        return recommendations
    
    def create_visualizations(self):
        """
        Create comprehensive visualizations for market expansion analysis.
        Each chart is generated individually and saved as a separate high-quality image.
        Addresses Requirements 2.3, 7.1, 7.2
        """
        logger.info("Creating individual market expansion visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create reports directory if it doesn't exist
        import os
        os.makedirs('reports', exist_ok=True)
        
        # 1. Market Penetration by State (Top 15)
        plt.figure(figsize=(14, 8))
        top_states = self.state_summary.nlargest(15, 'customer_count')
        bars = plt.bar(range(len(top_states)), top_states['customer_count'], 
                      color='steelblue', alpha=0.8, edgecolor='navy', linewidth=1)
        plt.title('Market Penetration by State (Top 15)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('States', fontsize=12)
        plt.ylabel('Number of Customers', fontsize=12)
        plt.xticks(range(len(top_states)), top_states['state'], rotation=45, ha='right')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('reports/01_market_penetration_by_state.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Expansion Opportunity Score by State (Top 15)
        plt.figure(figsize=(14, 8))
        top_opportunities = self.expansion_opportunities.head(15)
        bars = plt.bar(range(len(top_opportunities)), top_opportunities['combined_opportunity_score'], 
                      color='orange', alpha=0.8, edgecolor='darkorange', linewidth=1)
        plt.title('Expansion Opportunity Score (Top 15)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('States', fontsize=12)
        plt.ylabel('Combined Opportunity Score', fontsize=12)
        plt.xticks(range(len(top_opportunities)), top_opportunities['state'], rotation=45, ha='right')
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('reports/02_expansion_opportunity_scores.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Customer to Seller Ratio Analysis
        plt.figure(figsize=(12, 8))
        # Filter out extreme outliers for better visualization
        ratio_data = self.state_summary[self.state_summary['customer_to_seller_ratio'] <= 200]
        scatter = plt.scatter(ratio_data['customer_count'], ratio_data['customer_to_seller_ratio'], 
                            c=ratio_data['combined_opportunity_score'], cmap='viridis', 
                            alpha=0.7, s=80, edgecolors='black', linewidth=0.5)
        plt.title('Customer-Seller Ratio vs Market Size', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Number of Customers', fontsize=12)
        plt.ylabel('Customer to Seller Ratio', fontsize=12)
        plt.axhline(y=50, color='red', linestyle='--', alpha=0.8, linewidth=2, label='Seller Shortage Threshold (50:1)')
        plt.legend(fontsize=11)
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Opportunity Score', fontsize=12)
        
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('reports/03_customer_seller_ratio_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Delivery Performance vs Market Opportunity
        plt.figure(figsize=(12, 8))
        delivery_data = self.state_summary.dropna(subset=['avg_delivery_days'])
        scatter = plt.scatter(delivery_data['avg_delivery_days'], delivery_data['combined_opportunity_score'],
                            c=delivery_data['customer_count'], cmap='plasma', alpha=0.7, s=80, 
                            edgecolors='black', linewidth=0.5)
        plt.title('Delivery Performance vs Expansion Opportunity', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Average Delivery Days', fontsize=12)
        plt.ylabel('Combined Opportunity Score', fontsize=12)
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Customer Count', fontsize=12)
        
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('reports/04_delivery_vs_opportunity.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Untapped Revenue Potential (Top 10)
        if 'untapped_revenue_potential' in self.state_summary.columns:
            plt.figure(figsize=(12, 8))
            top_potential = self.state_summary.nlargest(10, 'untapped_revenue_potential')
            bars = plt.barh(range(len(top_potential)), top_potential['untapped_revenue_potential']/1000000, 
                           color='green', alpha=0.8, edgecolor='darkgreen', linewidth=1)
            plt.title('Untapped Revenue Potential (Top 10)', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Potential Revenue (Millions R$)', fontsize=12)
            plt.ylabel('States', fontsize=12)
            plt.yticks(range(len(top_potential)), top_potential['state'])
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                plt.text(width + width*0.01, bar.get_y() + bar.get_height()/2.,
                        f'R${width:.1f}M', ha='left', va='center', fontsize=11, fontweight='bold')
            
            plt.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            plt.savefig('reports/05_untapped_revenue_potential.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 6. Expansion Priority Distribution
        plt.figure(figsize=(10, 8))
        priority_counts = self.expansion_opportunities['expansion_priority'].value_counts()
        colors = ['#ff4444', '#ff8800', '#ffdd00', '#88dd88']
        wedges, texts, autotexts = plt.pie(priority_counts.values, labels=priority_counts.index, 
                                          autopct='%1.1f%%', colors=colors, startangle=90,
                                          textprops={'fontsize': 12})
        plt.title('Expansion Priority Distribution', fontsize=16, fontweight='bold', pad=20)
        
        # Enhance text visibility
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        plt.savefig('reports/06_expansion_priority_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 7. Seller Gap Analysis (Top 10)
        if 'seller_gap' in self.state_summary.columns:
            plt.figure(figsize=(12, 8))
            top_gaps = self.state_summary.nlargest(10, 'seller_gap')
            bars = plt.bar(range(len(top_gaps)), top_gaps['seller_gap'], 
                          color='purple', alpha=0.8, edgecolor='darkviolet', linewidth=1)
            plt.title('Seller Gap Analysis (Top 10)', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('States', fontsize=12)
            plt.ylabel('Additional Sellers Needed', fontsize=12)
            plt.xticks(range(len(top_gaps)), top_gaps['state'], rotation=45, ha='right')
            
            # Add value labels
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{int(height)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig('reports/07_seller_gap_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 8. Market Penetration Rate vs Population
        if 'penetration_rate' in self.state_summary.columns and 'population' in self.state_summary.columns:
            plt.figure(figsize=(12, 8))
            pop_data = self.state_summary.dropna(subset=['penetration_rate', 'population'])
            scatter = plt.scatter(pop_data['population']/1000000, pop_data['penetration_rate'],
                                c=pop_data['combined_opportunity_score'], cmap='coolwarm', 
                                alpha=0.7, s=80, edgecolors='black', linewidth=0.5)
            plt.title('Market Penetration Rate vs Population', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Population (Millions)', fontsize=12)
            plt.ylabel('Penetration Rate (customers per 1000)', fontsize=12)
            
            # Add colorbar
            cbar = plt.colorbar(scatter)
            cbar.set_label('Opportunity Score', fontsize=12)
            
            plt.grid(alpha=0.3)
            plt.tight_layout()
            plt.savefig('reports/08_penetration_vs_population.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 9. Revenue per Customer by State (Top 15)
        plt.figure(figsize=(14, 8))
        top_revenue_per_customer = self.state_summary.nlargest(15, 'revenue_per_customer')
        bars = plt.bar(range(len(top_revenue_per_customer)), top_revenue_per_customer['revenue_per_customer'], 
                      color='teal', alpha=0.8, edgecolor='darkcyan', linewidth=1)
        plt.title('Revenue per Customer by State (Top 15)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('States', fontsize=12)
        plt.ylabel('Revenue per Customer (R$)', fontsize=12)
        plt.xticks(range(len(top_revenue_per_customer)), top_revenue_per_customer['state'], rotation=45, ha='right')
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'R${height:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('reports/09_revenue_per_customer_by_state.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 10. Comprehensive Opportunity Matrix Heatmap
        plt.figure(figsize=(14, 10))
        
        # Select top 20 states for the heatmap
        top_20_states = self.expansion_opportunities.head(20)
        
        # Create matrix data for heatmap
        heatmap_data = top_20_states[['market_opportunity_score', 'market_potential_score', 
                                     'seller_efficiency_score', 'delivery_efficiency_score']].fillna(0)
        heatmap_data.index = top_20_states['state']
        heatmap_data.columns = ['Market Opportunity', 'Market Potential', 'Seller Efficiency', 'Delivery Efficiency']
        
        # Create heatmap
        sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn', center=0.5, 
                   fmt='.3f', cbar_kws={'label': 'Score'}, 
                   linewidths=0.5, square=False)
        plt.title('Market Expansion Opportunity Matrix (Top 20 States)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Opportunity Dimensions', fontsize=12)
        plt.ylabel('States', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        plt.savefig('reports/10_opportunity_matrix_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Successfully created 10 individual market expansion visualizations")
        
        return True
    
    def generate_report(self):
        """
        Generate comprehensive market expansion analysis report.
        Addresses Requirements 7.1, 7.2
        """
        logger.info("Generating market expansion analysis report...")
        
        report_content = f"""# Market Expansion Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report analyzes market expansion opportunities across Brazilian states using comprehensive 
e-commerce data. The analysis identifies underserved markets, evaluates seller distribution 
efficiency, and provides actionable recommendations for geographic expansion.

### Key Findings

"""
        
        # Add key insights
        for insight in self.insights:
            report_content += f"**{insight['category']}:** {insight['insight']}\n\n"
        
        report_content += f"""
## Detailed Analysis Results

### Market Penetration Summary
- Total states analyzed: {len(self.state_summary)}
- States with high expansion priority: {len(self.expansion_opportunities[self.expansion_opportunities['expansion_priority'] == 'Critical Priority'])}
- States with medium expansion priority: {len(self.expansion_opportunities[self.expansion_opportunities['expansion_priority'] == 'High Priority'])}

### Top 10 Expansion Opportunities

"""
        
        # Add top opportunities table
        top_10 = self.expansion_opportunities.head(10)
        report_content += "| Rank | State | Opportunity Score | Customers | Sellers | Untapped Potential |\n"
        report_content += "|------|-------|------------------|-----------|---------|-------------------|\n"
        
        for i, (_, row) in enumerate(top_10.iterrows(), 1):
            untapped = row.get('untapped_customers', 0)
            report_content += f"| {i} | {row['state']} | {row['combined_opportunity_score']:.3f} | {int(row['customer_count']):,} | {int(row['seller_count']):,} | {int(untapped):,} |\n"
        
        report_content += f"""
### Delivery Performance Analysis

Average delivery performance across states:
- National average delivery time: {self.state_summary['avg_delivery_days'].mean():.1f} days
- Best performing state: {self.state_summary.loc[self.state_summary['avg_delivery_days'].idxmin(), 'state']} ({self.state_summary['avg_delivery_days'].min():.1f} days)
- Worst performing state: {self.state_summary.loc[self.state_summary['avg_delivery_days'].idxmax(), 'state']} ({self.state_summary['avg_delivery_days'].max():.1f} days)

### Seller Distribution Analysis

"""
        
        if 'seller_gap' in self.state_summary.columns:
            total_gap = self.state_summary['seller_gap'].sum()
            report_content += f"- Total seller gap across all states: {int(total_gap):,} additional sellers needed\n"
            report_content += f"- States with largest seller gaps: {', '.join(self.state_summary.nlargest(5, 'seller_gap')['state'].tolist())}\n"
        
        report_content += f"""
## Strategic Recommendations

### Immediate Actions (Next 3 months)
1. **Priority Market Entry**: Focus on top 3 opportunity states with immediate market entry strategies
2. **Seller Recruitment**: Launch targeted seller recruitment campaigns in underserved high-potential markets
3. **Logistics Optimization**: Improve delivery infrastructure in states with poor delivery performance but high opportunity scores

### Medium-term Strategy (3-12 months)
1. **Market Development**: Develop comprehensive market entry strategies for medium-priority states
2. **Partnership Development**: Establish local partnerships to improve market penetration and delivery performance
3. **Customer Acquisition**: Launch targeted marketing campaigns in states with low penetration rates

### Long-term Vision (1-3 years)
1. **National Coverage**: Achieve balanced market coverage across all Brazilian states
2. **Logistics Excellence**: Establish world-class delivery performance standards nationwide
3. **Market Leadership**: Become the dominant e-commerce platform in underserved markets

## Methodology

This analysis used the following data sources and methods:
- **Data Sources**: Brazilian e-commerce dataset with orders, customers, sellers, and geographic information
- **Analysis Period**: {self.orders_df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} to {self.orders_df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')}
- **Geographic Scope**: All Brazilian states and major cities
- **Key Metrics**: Market penetration, seller distribution efficiency, delivery performance, untapped potential

### Limitations
- Population data based on 2020 census estimates
- Market potential calculations assume national average penetration as benchmark
- Delivery performance analysis limited to available order data
- Economic factors and regional preferences not fully incorporated

## Data Quality Notes
- Total records analyzed: {len(self.market_data):,}
- States with complete data: {len(self.state_summary.dropna()):,}
- Missing delivery data handled through interpolation and state-level aggregation

---
*This report was generated automatically by the Market Expansion Analysis module.*
"""
        
        # Save report
        with open('reports/market_expansion_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info("Market expansion analysis report saved to reports/market_expansion_report.md")
        return report_content
    
    def run_complete_analysis(self):
        """
        Run the complete market expansion analysis pipeline.
        """
        logger.info("Starting complete market expansion analysis...")
        
        # Load data
        if not self.load_data():
            logger.error("Failed to load data. Aborting analysis.")
            return False
        
        # Run analysis steps
        try:
            self.analyze_market_penetration()
            self.calculate_untapped_potential()
            self.evaluate_seller_distribution()
            self.analyze_delivery_performance_by_geography()
            self.generate_expansion_opportunity_matrix()
            
            # Create visualizations
            self.create_visualizations()
            
            # Generate report
            self.generate_report()
            
            logger.info("Market expansion analysis completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return False

def main():
    """Main function to run market expansion analysis."""
    analyzer = MarketExpansionAnalyzer()
    success = analyzer.run_complete_analysis()
    
    if success:
        print("Market Expansion Analysis completed successfully!")
        print("Check the following files for results:")
        print("- reports/market_expansion_report.md")
        print("- reports/01_market_penetration_by_state.png")
        print("- reports/02_expansion_opportunity_scores.png")
        print("- reports/03_customer_seller_ratio_analysis.png")
        print("- reports/04_delivery_vs_opportunity.png")
        print("- reports/05_untapped_revenue_potential.png")
        print("- reports/06_expansion_priority_distribution.png")
        print("- reports/07_seller_gap_analysis.png")
        print("- reports/08_penetration_vs_population.png")
        print("- reports/09_revenue_per_customer_by_state.png")
        print("- reports/10_opportunity_matrix_heatmap.png")
        
        # Display key insights
        print("\n=== KEY INSIGHTS ===")
        for insight in analyzer.insights:
            print(f"{insight['category']}: {insight['insight']}")
    else:
        print("Market expansion analysis failed. Check logs for details.")

def analyze():
    """
    Wrapper function for compatibility with testing suite.
    Runs the complete market expansion analysis.
    """
    analyzer = MarketExpansionAnalyzer()
    return analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()