"""
Modern responsive UI components with glass morphism
"""

import streamlit as st
import plotly.graph_objects as go
from dashboard.components.styling import get_theme_colors

def create_kpi_card(title, value, delta=None, delta_color="normal"):
    """Create a modern KPI card using Streamlit's metric component"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def format_metric_value(value, title):
    """Format metric values based on the title/context"""
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    # Format based on title keywords
    title_lower = title.lower()
    
    if "revenue" in title_lower or "value" in title_lower:
        # Currency formatting
        if value >= 1_000_000:
            return f"R$ {value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"R$ {value/1_000:.1f}K"
        else:
            return f"R$ {value:,.0f}"
    
    elif "rate" in title_lower or "reliability" in title_lower or "%" in title_lower:
        # Percentage formatting
        return f"{value:.1f}%"
    
    elif "days" in title_lower or "time" in title_lower:
        # Days formatting
        return f"{value:.1f} days"
    
    elif "customers" in title_lower or "states" in title_lower or "opportunities" in title_lower:
        # Large number formatting
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.0f}K"
        else:
            return f"{value:,.0f}"
    
    else:
        # Default number formatting
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.0f}K"
        else:
            return f"{value:.1f}"

def create_metric_card(title, value, delta=None, delta_color="normal", icon=None, **kwargs):
    """Create a metric card (enhanced for backward compatibility)"""
    # Format the value automatically
    formatted_value = format_metric_value(value, title)
    
    if icon:
        # If icon is provided, use the modern version
        create_modern_kpi_card(title, formatted_value, delta, delta_color, icon, **kwargs)
    else:
        # Otherwise use the simple version
        create_kpi_card(title, formatted_value, delta, delta_color)

def create_modern_kpi_card(title, value, delta=None, delta_color="normal", icon=None, description=None):
    """Create a modern KPI card with glass morphism"""
    colors = get_theme_colors()
    
    # Determine delta color
    if delta and delta_color == "normal":
        if "+" in str(delta) or (isinstance(delta, (int, float)) and delta > 0):
            delta_color_hex = colors['success']
        else:
            delta_color_hex = colors['error']
    else:
        delta_color_hex = colors['text_secondary']
    
    # Create the card HTML
    card_html = f"""
    <div class="modern-kpi-card glass-card fade-in-up">
        <div class="kpi-header">
            {f'<div class="kpi-icon">{icon}</div>' if icon else ''}
            <div class="kpi-title">{title}</div>
        </div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-delta" style="color: {delta_color_hex};">{delta}</div>' if delta else ''}
        {f'<div class="kpi-description">{description}</div>' if description else ''}
    </div>
    
    <style>
    .modern-kpi-card {{
        text-align: center;
        position: relative;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    
    .kpi-header {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }}
    
    .kpi-icon {{
        font-size: 1.5rem;
        opacity: 0.8;
    }}
    
    .kpi-title {{
        font-size: clamp(0.8rem, 2vw, 0.95rem);
        font-weight: 500;
        color: {colors['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .kpi-value {{
        font-size: clamp(1.8rem, 5vw, 2.5rem);
        font-weight: 700;
        color: {colors['text_primary']};
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .kpi-delta {{
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    
    .kpi-description {{
        font-size: clamp(0.75rem, 1.8vw, 0.85rem);
        color: {colors['text_muted']};
        opacity: 0.8;
    }}
    </style>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def create_info_card(title, content, icon=None, **kwargs):
    """Create a simple info card with glass morphism"""
    colors = get_theme_colors()
    
    # Add icon to title if provided
    title_with_icon = f"{icon} {title}" if icon else title
    
    card_html = f"""
    <div class="glass-card fade-in-up">
        <h3 style="color: {colors['text_primary']}; margin-bottom: 1rem;">{title_with_icon}</h3>
        <div style="color: {colors['text_secondary']};">{content}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def show_loading_state(message="Loading..."):
    """Show loading state"""
    with st.spinner(message):
        st.empty()

def show_error_message(message):
    """Show error message"""
    st.error(message)

def show_success_message(message):
    """Show success message"""
    st.success(message)

def create_chart_container():
    """Create a container for charts"""
    return st.container()

def apply_chart_theme(fig):
    """Apply dark theme to plotly charts with better responsiveness"""
    colors = get_theme_colors()
    
    fig.update_layout(
        # Background and paper
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        
        # Fonts
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            size=12,
            color=colors['text_primary']
        ),
        
        # Legend
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(color=colors['text_secondary'])
        ),
        
        # Margins for responsiveness
        margin=dict(l=40, r=40, t=60, b=40),
        
        # Responsive height
        autosize=True,
        
        # Grid and axes
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.2)',
            tickcolor='rgba(255,255,255,0.2)',
            tickfont=dict(color=colors['text_secondary']),
            titlefont=dict(color=colors['text_primary'])
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.2)',
            tickcolor='rgba(255,255,255,0.2)',
            tickfont=dict(color=colors['text_secondary']),
            titlefont=dict(color=colors['text_primary'])
        ),
        
        # Hover
        hoverlabel=dict(
            bgcolor='rgba(61, 47, 79, 0.9)',
            bordercolor=colors['accent_blue'],
            font=dict(color=colors['text_primary'])
        )
    )
    
    # Update traces for better visibility
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        textfont=dict(color=colors['text_primary'])
    )
    
    return fig

def create_info_banner(message, type="info", dismissible=False):
    """Create modern info banner"""
    colors = get_theme_colors()
    
    type_colors = {
        "info": colors['info'],
        "success": colors['success'],
        "warning": colors['warning'],
        "error": colors['error']
    }
    
    type_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    banner_color = type_colors.get(type, colors['info'])
    banner_icon = type_icons.get(type, "ℹ️")
    
    banner_html = f"""
    <div class="info-banner {type}-banner glass-card fade-in-up">
        <div class="banner-content">
            <span class="banner-icon">{banner_icon}</span>
            <span class="banner-message">{message}</span>
        </div>
    </div>
    
    <style>
    .info-banner {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid {banner_color};
        background: rgba(255, 255, 255, 0.02);
    }}
    
    .banner-content {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex: 1;
    }}
    
    .banner-icon {{
        font-size: 1.2rem;
    }}
    
    .banner-message {{
        font-size: clamp(0.9rem, 2vw, 1rem);
        color: {colors['text_primary']};
        font-weight: 500;
    }}
    </style>
    """
    
    st.markdown(banner_html, unsafe_allow_html=True)

def create_section_divider(title):
    """Create a section divider with title"""
    colors = get_theme_colors()
    
    divider_html = f"""
    <div class="section-divider" style="margin: 2rem 0 1.5rem 0;">
        <h2 style="
            color: {colors['text_primary']};
            font-size: clamp(1.4rem, 3vw, 1.8rem);
            font-weight: 600;
            text-align: center;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, {colors['accent_blue']}, {colors['accent_purple']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">{title}</h2>
        <div style="
            height: 2px;
            background: linear-gradient(90deg, transparent, {colors['accent_blue']}, {colors['accent_purple']}, transparent);
            margin: 0 auto;
            width: 60%;
            border-radius: 1px;
        "></div>
    </div>
    """
    
    st.markdown(divider_html, unsafe_allow_html=True)

def create_highlight_box(content, type="info"):
    """Create a highlight box with colored border"""
    colors = get_theme_colors()
    
    type_colors = {
        "info": colors['info'],
        "success": colors['success'],
        "warning": colors['warning'],
        "error": colors['error']
    }
    
    box_color = type_colors.get(type, colors['info'])
    
    box_html = f"""
    <div class="highlight-box glass-card fade-in-up" style="
        border-left: 4px solid {box_color};
        background: rgba(255, 255, 255, 0.02);
        margin: 1rem 0;
    ">
        <div style="color: {colors['text_primary']};">
            {content}
        </div>
    </div>
    """
    
    st.markdown(box_html, unsafe_allow_html=True)

def create_progress_bar(value, max_value, label, color=None):
    """Create a progress bar with label"""
    colors = get_theme_colors()
    
    if color is None:
        color = colors['accent_blue']
    
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    
    progress_html = f"""
    <div class="progress-container" style="margin: 1rem 0;">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        ">
            <span style="color: {colors['text_primary']}; font-weight: 500;">{label}</span>
            <span style="color: {colors['text_secondary']}; font-size: 0.9rem;">{value}/{max_value}</span>
        </div>
        <div style="
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, {color}, {colors['accent_purple']});
                height: 100%;
                width: {percentage}%;
                border-radius: 10px;
                transition: width 0.3s ease;
            "></div>
        </div>
    </div>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)