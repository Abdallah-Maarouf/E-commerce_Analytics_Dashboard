"""
Modern responsive styling with glass morphism effects
"""

import streamlit as st

def get_theme_colors():
    """Enhanced color palette for modern design"""
    return {
        # Base colors
        'primary_bg': '#1a1625',
        'secondary_bg': '#2a1f3d',
        'surface_bg': 'rgba(61, 47, 79, 0.6)',
        'card_bg': 'rgba(61, 47, 79, 0.6)',  # Alias for surface_bg
        'glass_bg': 'rgba(255, 255, 255, 0.05)',
        
        # Text colors
        'text_primary': '#ffffff',
        'text_secondary': '#e0e0e0',
        'text_muted': '#b0b0b0',
        
        # Accent colors
        'accent_blue': '#00d4ff',
        'accent_purple': '#9c27b0',
        'accent_orange': '#ff9500',
        'accent_green': '#00e676',
        'accent_pink': '#e91e63',
        
        # Functional colors
        'success': '#00e676',
        'warning': '#ff9500',
        'error': '#ff5252',
        'info': '#00d4ff',
        
        # Border and shadow
        'border_light': 'rgba(255, 255, 255, 0.1)',
        'border_color': 'rgba(255, 255, 255, 0.1)',  # Alias for border_light
        'border_accent': 'rgba(0, 212, 255, 0.3)',
        'shadow_light': 'rgba(0, 0, 0, 0.1)',
        'shadow_medium': 'rgba(0, 0, 0, 0.2)',
        'shadow_heavy': 'rgba(0, 0, 0, 0.4)'
    }

def apply_dark_theme():
    """Apply modern responsive theme with glass morphism"""
    colors = get_theme_colors()
    
    st.markdown(f"""
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Main app container */
    .stApp {{
        background: linear-gradient(135deg, {colors['primary_bg']} 0%, {colors['secondary_bg']} 100%);
        color: {colors['text_primary']};
        min-height: 100vh;
    }}
    
    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Typography system */
    h1 {{
        font-size: clamp(1.8rem, 4vw, 2.5rem);
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 1.5rem;
        background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    h2 {{
        font-size: clamp(1.4rem, 3vw, 2rem);
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: 1.25rem;
        color: {colors['text_primary']};
    }}
    
    h3 {{
        font-size: clamp(1.2rem, 2.5vw, 1.5rem);
        font-weight: 600;
        line-height: 1.4;
        margin-bottom: 1rem;
        color: {colors['text_primary']};
    }}
    
    p, div, span {{
        font-size: clamp(0.9rem, 2vw, 1rem);
        line-height: 1.6;
        color: {colors['text_secondary']};
    }}
    
    /* Glass morphism cards */
    .glass-card {{
        background: {colors['glass_bg']};
        backdrop-filter: blur(20px);
        border: 1px solid {colors['border_light']};
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px {colors['shadow_medium']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .glass-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, {colors['accent_blue']}, transparent);
        opacity: 0.5;
    }}
    
    .glass-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px {colors['shadow_heavy']};
        border-color: {colors['border_accent']};
    }}
    
    /* Metric cards enhancement */
    [data-testid="metric-container"] {{
        background: {colors['glass_bg']} !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid {colors['border_light']} !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px {colors['shadow_medium']} !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    [data-testid="metric-container"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {colors['accent_blue']}, {colors['accent_purple']});
        border-radius: 16px 16px 0 0;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 40px {colors['shadow_heavy']} !important;
        border-color: {colors['border_accent']} !important;
    }}
    
    /* Metric values styling */
    [data-testid="metric-container"] [data-testid="metric-value"] {{
        font-size: clamp(1.5rem, 4vw, 2.5rem) !important;
        font-weight: 700 !important;
        color: {colors['text_primary']} !important;
    }}
    
    [data-testid="metric-container"] [data-testid="metric-label"] {{
        font-size: clamp(0.8rem, 2vw, 1rem) !important;
        font-weight: 500 !important;
        color: {colors['text_secondary']} !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Chart containers */
    .js-plotly-plot {{
        background: {colors['glass_bg']} !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid {colors['border_light']} !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 32px {colors['shadow_medium']} !important;
    }}
    
    /* Mobile optimizations */
    @media (max-width: 768px) {{
        .glass-card {{
            padding: 1rem;
            border-radius: 12px;
        }}
        
        [data-testid="metric-container"] {{
            padding: 1rem !important;
            border-radius: 12px !important;
        }}
    }}
    
    @media (max-width: 480px) {{
        .glass-card {{
            padding: 0.75rem;
            border-radius: 8px;
        }}
        
        [data-testid="metric-container"] {{
            padding: 0.75rem !important;
            border-radius: 8px !important;
        }}
        
        h1 {{
            margin-bottom: 1rem;
        }}
        
        h2 {{
            margin-bottom: 0.75rem;
        }}
    }}
    
    /* Animations */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .fade-in-up {{
        animation: fadeInUp 0.6s ease-out;
    }}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {colors['surface_bg']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(45deg, {colors['accent_purple']}, {colors['accent_blue']});
    }}
    </style>
    """, unsafe_allow_html=True)