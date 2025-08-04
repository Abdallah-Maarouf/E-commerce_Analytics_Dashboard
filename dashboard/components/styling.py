"""
Dark theme styling and CSS components for the dashboard
"""

import streamlit as st

def get_theme_colors():
    """Return the dark theme color palette"""
    return {
        'primary_bg': '#1a1625',
        'secondary_bg': '#2a1f3d',
        'card_bg': 'rgba(61, 47, 79, 0.8)',
        'text_primary': '#ffffff',
        'text_secondary': '#e0e0e0',
        'accent_orange': '#ff9500',
        'accent_blue': '#00d4ff',
        'accent_green': '#00e676',
        'accent_pink': '#e91e63',
        'accent_purple': '#9c27b0',
        'border_color': '#3d2f4f',
        'hover_color': '#4a3a5a'
    }

def apply_dark_theme():
    """Apply dark theme CSS styling to the Streamlit app"""
    colors = get_theme_colors()
    
    st.markdown(f"""
    <style>
    /* Main app background */
    .stApp {{
        background: linear-gradient(135deg, {colors['primary_bg']} 0%, {colors['secondary_bg']} 100%);
        color: {colors['text_primary']};
    }}
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc, .css-17lntkn, section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {colors['secondary_bg']} 0%, {colors['primary_bg']} 100%);
        border-right: 2px solid {colors['border_color']};
    }}
    
    /* Sidebar navigation */
    .css-17eq0hr, .css-pkbazv {{
        background: transparent;
        color: {colors['text_primary']};
    }}
    
    /* Sidebar toggle button when sidebar is collapsed */
    [data-testid="collapsedControl"] {{
        background: {colors['card_bg']} !important;
        border: 2px solid {colors['accent_blue']} !important;
        border-radius: 12px !important;
        color: {colors['text_primary']} !important;
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        width: 3rem !important;
        height: 3rem !important;
        padding: 0.5rem !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
    }}
    
    [data-testid="collapsedControl"]:hover {{
        background: {colors['hover_color']} !important;
        border-color: {colors['accent_purple']} !important;
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
    }}
    
    /* Sidebar toggle button icon */
    [data-testid="collapsedControl"] svg {{
        color: {colors['accent_blue']} !important;
        width: 1.5rem !important;
        height: 1.5rem !important;
        filter: drop-shadow(0 0 5px {colors['accent_blue']}40) !important;
    }}
    
    [data-testid="collapsedControl"]:hover svg {{
        color: {colors['accent_purple']} !important;
    }}
    
    /* Main content area */
    .main .block-container, .css-18e3th9, .css-1d391kg .css-1lcbmhc {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: transparent;
    }}
    
    /* Fix main container */
    .css-k1vhr4, .css-18e3th9 {{
        background: transparent;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {colors['text_primary']} !important;
        font-weight: 600;
    }}
    
    h1 {{
        background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
    }}
    
    /* Text elements */
    p, div, span {{
        color: {colors['text_secondary']} !important;
    }}
    
    /* Metrics and KPI cards */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, {colors['card_bg']}, rgba(61, 47, 79, 0.6)) !important;
        border: 1px solid {colors['border_color']} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
        border-color: {colors['accent_purple']} !important;
    }}
    
    /* Metric container top accent line */
    [data-testid="metric-container"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {colors['accent_blue']}, {colors['accent_purple']});
    }}
    
    /* Metric labels */
    [data-testid="metric-container"] [data-testid="metric-label"] {{
        color: {colors['text_secondary']} !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Metric values */
    [data-testid="metric-container"] [data-testid="metric-value"] {{
        color: {colors['text_primary']} !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Metric deltas */
    [data-testid="metric-container"] [data-testid="metric-delta"] {{
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        margin-top: 0.5rem !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(45deg, {colors['accent_purple']}, {colors['accent_blue']});
        color: {colors['text_primary']};
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(156, 39, 176, 0.4);
    }}
    
    /* Selectbox and inputs */
    .stSelectbox > div > div, .stRadio > div {{
        background: {colors['card_bg']};
        border: 1px solid {colors['border_color']};
        border-radius: 8px;
        color: {colors['text_primary']};
    }}
    
    /* Radio buttons */
    .stRadio > div > label {{
        background: transparent;
        color: {colors['text_primary']} !important;
        padding: 0.5rem;
        border-radius: 6px;
        transition: all 0.3s ease;
    }}
    
    .stRadio > div > label:hover {{
        background: {colors['hover_color']};
    }}
    
    .stRadio > div > label > div[data-testid="stMarkdownContainer"] {{
        color: {colors['text_primary']} !important;
    }}
    
    /* Charts and plotly */
    .js-plotly-plot {{
        background: transparent !important;
    }}
    
    /* Loading spinner */
    .stSpinner > div {{
        border-top-color: {colors['accent_blue']} !important;
    }}
    
    /* Alert messages styling */
    .stAlert {{
        background: rgba(233, 30, 99, 0.1) !important;
        border: 1px solid {colors['accent_pink']} !important;
        border-radius: 12px !important;
        color: {colors['text_primary']} !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Success messages */
    .stSuccess {{
        background: rgba(0, 230, 118, 0.1) !important;
        border: 1px solid {colors['accent_green']} !important;
        border-radius: 12px !important;
        color: {colors['text_primary']} !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Info messages */
    .stInfo, [data-testid="stAlert"] {{
        background: linear-gradient(135deg, {colors['card_bg']}, rgba(61, 47, 79, 0.6)) !important;
        border: 1px solid {colors['border_color']} !important;
        border-radius: 12px !important;
        color: {colors['text_primary']} !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        padding: 1.5rem !important;
    }}
    
    /* Info message text */
    [data-testid="stAlert"] p {{
        color: {colors['text_secondary']} !important;
        margin: 0 !important;
    }}
    
    /* Info message icons */
    [data-testid="stAlert"] [data-testid="stAlertIcon"] {{
        color: {colors['accent_blue']} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {colors['card_bg']};
        border-radius: 8px;
        padding: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: {colors['text_secondary']};
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(45deg, {colors['accent_purple']}, {colors['accent_blue']});
        color: {colors['text_primary']} !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: {colors['card_bg']};
        border: 1px solid {colors['border_color']};
        border-radius: 8px;
        color: {colors['text_primary']};
    }}
    
    /* Custom card styling */
    .custom-card {{
        background: linear-gradient(135deg, {colors['card_bg']}, rgba(61, 47, 79, 0.6));
        border: 1px solid {colors['border_color']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }}
    
    .custom-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        border-color: {colors['accent_purple']};
    }}
    
    /* Gradient text */
    .gradient-text {{
        background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600;
    }}
    
    /* Neon accent */
    .neon-accent {{
        color: {colors['accent_blue']};
        text-shadow: 0 0 10px {colors['accent_blue']}40;
    }}
    
    /* Fix Streamlit default styles */
    .css-17lntkn {{
        background: transparent;
    }}
    
    /* Alternative selectors for sidebar toggle button */
    .css-1rs6os, button[kind="header"], button[data-testid="baseButton-header"] {{
        background: {colors['card_bg']} !important;
        border: 2px solid {colors['accent_blue']} !important;
        border-radius: 12px !important;
        color: {colors['text_primary']} !important;
        padding: 0.5rem !important;
        margin: 1rem !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        z-index: 999999 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 3rem !important;
        height: 3rem !important;
    }}
    
    .css-1rs6os:hover, button[kind="header"]:hover, button[data-testid="baseButton-header"]:hover {{
        background: {colors['hover_color']} !important;
        border-color: {colors['accent_purple']} !important;
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
    }}
    
    /* Icons in toggle buttons */
    .css-1rs6os svg, button[kind="header"] svg, button[data-testid="baseButton-header"] svg {{
        color: {colors['accent_blue']} !important;
        width: 1.5rem !important;
        height: 1.5rem !important;
        filter: drop-shadow(0 0 5px {colors['accent_blue']}40) !important;
    }}
    
    .css-1rs6os:hover svg, button[kind="header"]:hover svg, button[data-testid="baseButton-header"]:hover svg {{
        color: {colors['accent_purple']} !important;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Fix text color inheritance */
    .css-1cpxqw2, .css-16idsys p {{
        color: {colors['text_secondary']} !important;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main .block-container, .css-18e3th9 {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        
        [data-testid="metric-container"] {{
            margin-bottom: 1rem;
        }}
    }}
    </style>
    

    """, unsafe_allow_html=True)

def get_card_style(accent_color=None):
    """Get CSS style for custom cards with optional accent color"""
    colors = get_theme_colors()
    accent = accent_color or colors['accent_purple']
    
    return f"""
    background: linear-gradient(135deg, {colors['card_bg']}, rgba(61, 47, 79, 0.6));
    border: 1px solid {colors['border_color']};
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
    """

def get_gradient_text_style(color1=None, color2=None):
    """Get CSS style for gradient text"""
    colors = get_theme_colors()
    c1 = color1 or colors['accent_blue']
    c2 = color2 or colors['accent_purple']
    
    return f"""
    background: linear-gradient(45deg, {c1}, {c2});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
    """