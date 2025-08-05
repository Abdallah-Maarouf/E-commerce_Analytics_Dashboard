"""
Chart Performance Optimization Utilities
Improves chart rendering and responsiveness
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def optimize_chart_data(df, max_points=1000):
    """Optimize data for chart rendering"""
    if len(df) > max_points:
        # Sample data intelligently
        return df.sample(n=max_points).sort_index()
    return df

def create_responsive_chart(fig, height=400):
    """Make charts responsive"""
    fig.update_layout(
        autosize=True,
        height=height,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def disable_chart_animations(fig):
    """Disable animations for better performance"""
    fig.update_layout(transition_duration=0)
    return fig

def optimize_plotly_config():
    """Return optimized Plotly config"""
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'responsive': True
    }
