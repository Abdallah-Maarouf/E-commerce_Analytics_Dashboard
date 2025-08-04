"""
Navigation components for the dashboard
"""

import streamlit as st
from dashboard.components.styling import get_theme_colors

def setup_sidebar_navigation():
    """Setup sidebar navigation with dark theme styling"""
    colors = get_theme_colors()
    
    # Add custom toggle button that's always visible when sidebar is collapsed
    st.markdown(f"""
    <style>
    /* Custom sidebar toggle button */
    .custom-sidebar-toggle {{
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        width: 3rem !important;
        height: 3rem !important;
        background: {colors['card_bg']} !important;
        border: 2px solid {colors['accent_blue']} !important;
        border-radius: 12px !important;
        color: {colors['accent_blue']} !important;
        cursor: pointer !important;
        z-index: 999999 !important;
        display: none !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
    }}
    
    .custom-sidebar-toggle:hover {{
        background: {colors['hover_color']} !important;
        border-color: {colors['accent_purple']} !important;
        color: {colors['accent_purple']} !important;
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
    }}
    
    /* Show custom toggle when sidebar is collapsed */
    .stApp[data-sidebar-state="collapsed"] .custom-sidebar-toggle {{
        display: flex !important;
    }}
    
    /* Sidebar title styling */
    .sidebar-title {{
        color: {colors['text_primary']};
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
        background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Navigation menu styling */
    .nav-menu {{
        margin-bottom: 2rem;
    }}
    
    /* Page info styling */
    .page-info {{
        background: {colors['card_bg']};
        border: 1px solid {colors['border_color']};
        border-radius: 8px;
        padding: 1rem;
        margin-top: 2rem;
        color: {colors['text_secondary']};
    }}
    
    .page-info h4 {{
        color: {colors['accent_blue']} !important;
        margin-bottom: 0.5rem;
    }}
    </style>
    
    <!-- Custom sidebar toggle button -->
    <div class="custom-sidebar-toggle" onclick="toggleSidebar()" title="Show Sidebar">
        ☰
    </div>
    
    <script>
    function toggleSidebar() {{
        // Try multiple methods to toggle the sidebar
        const toggleSelectors = [
            '[data-testid="collapsedControl"]',
            '.css-1rs6os',
            'button[kind="header"]',
            'button[data-testid="baseButton-header"]'
        ];
        
        for (let selector of toggleSelectors) {{
            const button = document.querySelector(selector);
            if (button) {{
                button.click();
                return;
            }}
        }}
        
        // If no button found, try keyboard shortcut
        document.dispatchEvent(new KeyboardEvent('keydown', {{
            key: '[',
            ctrlKey: true
        }}));
    }}
    
    // Monitor sidebar state and show/hide custom toggle
    function monitorSidebarState() {{
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const app = document.querySelector('.stApp');
        const customToggle = document.querySelector('.custom-sidebar-toggle');
        
        if (sidebar && app && customToggle) {{
            const sidebarVisible = sidebar.offsetWidth > 0;
            if (sidebarVisible) {{
                app.setAttribute('data-sidebar-state', 'expanded');
                customToggle.style.display = 'none';
            }} else {{
                app.setAttribute('data-sidebar-state', 'collapsed');
                customToggle.style.display = 'flex';
            }}
        }}
    }}
    
    // Run monitoring
    setInterval(monitorSidebarState, 100);
    document.addEventListener('DOMContentLoaded', monitorSidebarState);
    </script>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # Dashboard title
        st.markdown('<div class="sidebar-title">📊 E-commerce Analytics</div>', unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown('<div class="nav-menu">', unsafe_allow_html=True)
        
        pages = {
            "Executive Overview": {
                "icon": "🎯",
                "description": "Key metrics and business overview"
            },
            "Market Expansion": {
                "icon": "🗺️",
                "description": "Geographic growth opportunities"
            },
            "Customer Analytics": {
                "icon": "👥",
                "description": "Customer insights and segmentation"
            },
            "Seasonal Intelligence": {
                "icon": "📈",
                "description": "Seasonal trends and forecasting"
            },
            "Payment & Operations": {
                "icon": "💳",
                "description": "Payment behavior and operations"
            }
        }
        
        # Create radio buttons for navigation
        page_options = [f"{pages[page]['icon']} {page}" for page in pages.keys()]
        selected_option = st.radio(
            "Navigate to:",
            page_options,
            key="navigation",
            label_visibility="collapsed"
        )
        
        # Extract the selected page name (remove icon)
        selected_page = selected_option.split(" ", 1)[1]
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show page information
        if selected_page in pages:
            st.markdown(f"""
            <div class="page-info">
                <h4>{pages[selected_page]['icon']} {selected_page}</h4>
                <p>{pages[selected_page]['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Add footer information
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; color: {colors['text_secondary']}; font-size: 0.8rem;">
            <p>Brazilian E-commerce Analytics</p>
            <p>Built with Streamlit</p>
        </div>
        """, unsafe_allow_html=True)
    
    return selected_page

def show_page_header(title, subtitle=None, icon=None):
    """Display a styled page header"""
    colors = get_theme_colors()
    
    # Use Streamlit's native components with custom styling
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: {colors['text_primary']};
            font-weight: 700;
        ">
            {icon + ' ' if icon else ''}{title}
        </h1>
        {f'<p style="font-size: 1.2rem; color: {colors["text_secondary"]}; margin-top: 0; font-weight: 300;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_breadcrumb(pages):
    """Create a breadcrumb navigation"""
    colors = get_theme_colors()
    
    breadcrumb_html = f"""
    <div style="
        margin-bottom: 1rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid {colors['border_color']};
    ">
    """
    
    for i, page in enumerate(pages):
        if i > 0:
            breadcrumb_html += f' <span style="color: {colors["text_secondary"]};">></span> '
        
        if i == len(pages) - 1:  # Current page
            breadcrumb_html += f'<span style="color: {colors["accent_blue"]}; font-weight: 600;">{page}</span>'
        else:
            breadcrumb_html += f'<span style="color: {colors["text_secondary"]};">{page}</span>'
    
    breadcrumb_html += "</div>"
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)