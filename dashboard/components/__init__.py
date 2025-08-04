"""
Dashboard components package
"""

from .styling import apply_dark_theme, get_theme_colors, get_card_style, get_gradient_text_style
from .navigation import setup_sidebar_navigation, show_page_header, create_breadcrumb
from .ui_components import (
    show_loading_state, show_error_message, show_success_message,
    create_metric_card, create_info_card, create_section_divider,
    create_highlight_box, create_progress_bar
)

__all__ = [
    'apply_dark_theme', 'get_theme_colors', 'get_card_style', 'get_gradient_text_style',
    'setup_sidebar_navigation', 'show_page_header', 'create_breadcrumb',
    'show_loading_state', 'show_error_message', 'show_success_message',
    'create_metric_card', 'create_info_card', 'create_section_divider',
    'create_highlight_box', 'create_progress_bar'
]