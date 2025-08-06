"""
Modern top horizontal navigation with responsive design
"""

import streamlit as st

def setup_sidebar_navigation():
    """Create modern top horizontal navigation using Streamlit tabs"""
    
    # Apply basic styling
    st.markdown("""
    <style>
    /* Hide default sidebar */
    .css-1d391kg {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    
    /* Main container adjustments */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: none;
    }
    
    /* Brand/Logo styling */
    .nav-brand {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        background: rgba(26, 22, 37, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .nav-brand h1 {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(45deg, #00d4ff, #9c27b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .nav-brand p {
        color: #e0e0e0;
        font-size: 0.9rem;
        margin: 0.25rem 0 0 0;
        opacity: 0.8;
    }
    
    /* Enhanced tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(26, 22, 37, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(61, 47, 79, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        color: #e0e0e0;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 212, 255, 0.1);
        border-color: #00d4ff;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff, #9c27b0) !important;
        border-color: #00d4ff !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .nav-brand h1 {
            font-size: 1.5rem;
        }
        
        .nav-brand p {
            font-size: 0.8rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.6rem 1rem;
            font-size: 0.85rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Brand/Title section
    st.markdown("""
    <div class="nav-brand">
        <h1>📊 E-commerce Analytics Dashboard</h1>
        <p>Brazilian Market Intelligence & Business Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation pages
    pages = {
        "Executive Overview": "🎯",
        "Market Expansion": "🗺️", 
        "Customer Analytics": "👥",
        "Seasonal Intelligence": "📈",
        "Payment & Operations": "💳"
    }
    
    # Create tabs with icons
    tab_labels = [f"{icon} {name}" for name, icon in pages.items()]
    
    # Initialize session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Executive Overview"
    
    # Find current tab index
    page_names = list(pages.keys())
    try:
        current_index = page_names.index(st.session_state.active_tab)
    except ValueError:
        current_index = 0
        st.session_state.active_tab = page_names[0]
    
    # Create the tabs
    selected_tab = st.selectbox(
        "Navigate to:",
        options=page_names,
        index=current_index,
        format_func=lambda x: f"{pages[x]} {x}",
        key="navigation_select",
        label_visibility="collapsed"
    )
    
    # Update session state if selection changed
    if selected_tab != st.session_state.active_tab:
        st.session_state.active_tab = selected_tab
        st.rerun()
    
    return st.session_state.active_tab

def show_page_header(title, subtitle=None, icon=None):
    """Display a styled page header"""
    header_text = f"{icon} {title}" if icon else title
    st.title(header_text)
    
    if subtitle:
        st.markdown(f"*{subtitle}*")
    
    st.markdown("---")