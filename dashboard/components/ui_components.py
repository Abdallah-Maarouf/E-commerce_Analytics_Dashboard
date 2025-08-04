"""
Reusable UI components for the dashboard
"""

import streamlit as st
import time
from dashboard.components.styling import get_theme_colors, get_card_style, get_gradient_text_style

def show_loading_state(message="Loading data..."):
    """Display a loading state with spinner"""
    colors = get_theme_colors()
    
    with st.spinner(message):
        # Add a small delay to show the spinner
        time.sleep(0.5)
        
    st.markdown(f"""
    <div style="
        text-align: center;
        color: {colors['accent_blue']};
        font-style: italic;
        margin: 1rem 0;
    ">
        {message}
    </div>
    """, unsafe_allow_html=True)

def show_error_message(message, details=None):
    """Display an error message with optional details"""
    colors = get_theme_colors()
    
    st.markdown(f"""
    <div style="
        background: rgba(233, 30, 99, 0.1);
        border: 1px solid {colors['accent_pink']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: {colors['text_primary']};
    ">
        <h4 style="color: {colors['accent_pink']} !important; margin-bottom: 0.5rem;">
            ⚠️ Error
        </h4>
        <p style="margin-bottom: 0;">{message}</p>
        {f'<details><summary>Details</summary><p style="font-family: monospace; font-size: 0.9rem;">{details}</p></details>' if details else ''}
    </div>
    """, unsafe_allow_html=True)

def show_success_message(message):
    """Display a success message"""
    colors = get_theme_colors()
    
    st.markdown(f"""
    <div style="
        background: rgba(0, 230, 118, 0.1);
        border: 1px solid {colors['accent_green']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: {colors['text_primary']};
    ">
        <h4 style="color: {colors['accent_green']} !important; margin-bottom: 0.5rem;">
            ✅ Success
        </h4>
        <p style="margin-bottom: 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color=None, icon=None, accent_color=None):
    """Create a styled metric card with optional delta and icon"""
    colors = get_theme_colors()
    
    # Format the value if it's a number
    if isinstance(value, (int, float)):
        if value >= 1000000:
            formatted_value = f"{value/1000000:.1f}M"
        elif value >= 1000:
            formatted_value = f"{value/1000:.1f}K"
        else:
            formatted_value = f"{value:,.0f}" if isinstance(value, int) else f"{value:.2f}"
    else:
        formatted_value = str(value)
    
    # Format delta for Streamlit metric
    delta_value = None
    if delta is not None:
        delta_value = f"{delta:+.1f}%"
    
    # Create the metric with icon in label
    label_with_icon = f"{icon} {title}" if icon else title
    
    # Use Streamlit's native metric component
    st.metric(
        label=label_with_icon,
        value=formatted_value,
        delta=delta_value
    )

def create_info_card(title, content, icon=None, accent_color=None):
    """Create an information card with title and content"""
    # Use Streamlit's native info component
    title_with_icon = f"{icon} {title}" if icon else title
    st.info(f"**{title_with_icon}**\n\n{content}")

def create_section_divider(title=None):
    """Create a styled section divider"""
    colors = get_theme_colors()
    
    if title:
        divider_html = f"""
        <div style="
            display: flex;
            align-items: center;
            margin: 2rem 0 1rem 0;
        ">
            <div style="
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, transparent, {colors['border_color']}, transparent);
            "></div>
            <div style="
                padding: 0 1rem;
                color: {colors['accent_blue']};
                font-weight: 600;
                font-size: 1.1rem;
            ">
                {title}
            </div>
            <div style="
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, transparent, {colors['border_color']}, transparent);
            "></div>
        </div>
        """
    else:
        divider_html = f"""
        <div style="
            height: 1px;
            background: linear-gradient(90deg, transparent, {colors['border_color']}, transparent);
            margin: 2rem 0;
        "></div>
        """
    
    st.markdown(divider_html, unsafe_allow_html=True)

def create_highlight_box(content, type="info"):
    """Create a highlighted content box"""
    colors = get_theme_colors()
    
    type_config = {
        "info": {"color": colors['accent_blue'], "icon": "ℹ️"},
        "warning": {"color": colors['accent_orange'], "icon": "⚠️"},
        "success": {"color": colors['accent_green'], "icon": "✅"},
        "error": {"color": colors['accent_pink'], "icon": "❌"}
    }
    
    config = type_config.get(type, type_config["info"])
    
    box_html = f"""
    <div style="
        background: rgba({config['color'][1:3]}, {config['color'][3:5]}, {config['color'][5:7]}, 0.1);
        border-left: 4px solid {config['color']};
        border-radius: 0 8px 8px 0;
        padding: 1rem;
        margin: 1rem 0;
        color: {colors['text_primary']};
    ">
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
        ">
            <span style="font-size: 1.2rem;">{config['icon']}</span>
            <div>{content}</div>
        </div>
    </div>
    """
    
    st.markdown(box_html, unsafe_allow_html=True)

def create_progress_bar(value, max_value=100, label=None, color=None):
    """Create a styled progress bar"""
    colors = get_theme_colors()
    progress_color = color or colors['accent_blue']
    
    percentage = (value / max_value) * 100
    
    progress_html = f"""
    <div style="margin: 1rem 0;">
        {f'<div style="color: {colors["text_secondary"]}; margin-bottom: 0.5rem; font-size: 0.9rem;">{label}</div>' if label else ''}
        <div style="
            background: {colors['card_bg']};
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            position: relative;
        ">
            <div style="
                background: linear-gradient(90deg, {progress_color}, {colors['accent_purple']});
                height: 100%;
                width: {percentage}%;
                border-radius: 10px;
                transition: width 0.3s ease;
                position: relative;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                    animation: shimmer 2s infinite;
                "></div>
            </div>
        </div>
        <div style="
            text-align: right;
            color: {colors['text_secondary']};
            font-size: 0.8rem;
            margin-top: 0.25rem;
        ">
            {value}/{max_value} ({percentage:.1f}%)
        </div>
    </div>
    
    <style>
    @keyframes shimmer {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    </style>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)