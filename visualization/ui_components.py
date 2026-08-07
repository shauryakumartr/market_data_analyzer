"""UI Components & Theme Loader Module.

This module provides helper utilities for loading custom CSS stylesheets from the .streamlit
directory and rendering reusable UI components (header banner, metric cards, container wrappers)
so app.py remains decoupled from HTML/CSS string implementations.
"""

import os
import logging
from typing import Optional
import streamlit as st

logger: logging.Logger = logging.getLogger(__name__)

# Path to the custom CSS stylesheet in the .streamlit directory
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE_CSS_PATH: str = os.path.join(PROJECT_ROOT, ".streamlit", "style.css")


def load_custom_css(css_file_path: Optional[str] = None) -> None:
    """Inject custom executive CSS stylesheet into the Streamlit app context.

    Parameters
    ----------
    css_file_path : Optional[str]
        Path to the custom CSS file. Defaults to .streamlit/style.css.
    """
    target_path: str = css_file_path or STYLE_CSS_PATH
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                css_content: str = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            logger.info("Successfully loaded custom CSS stylesheet from '%s'", target_path)
        except Exception as exc:
            logger.error("Failed to read CSS stylesheet from '%s': %s", target_path, exc)
    else:
        logger.warning("Custom CSS file not found at '%s'. Skipping custom CSS injection.", target_path)


def render_header_banner(
    title: str = "Instagram Campaign Analyzer",
    subtitle: str = "Optimize your Instagram marketing campaigns with precision metrics and AI-driven consultant advice"
) -> None:
    """Render top hero header banner.

    Parameters
    ----------
    title : str
        Main headline title text.
    subtitle : str
        Subheading description text.
    """
    banner_html: str = f"""
<div class="header-banner">
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
"""
    st.markdown(banner_html, unsafe_allow_html=True)


def open_metric_primary() -> None:
    """Open container wrapper for primary highlighted metric cards."""
    st.markdown('<div class="metric-primary">', unsafe_allow_html=True)


def close_metric_primary() -> None:
    """Close container wrapper for primary highlighted metric cards."""
    st.markdown('</div>', unsafe_allow_html=True)


def open_metric_secondary() -> None:
    """Open container wrapper for secondary operational metric cards."""
    st.markdown('<div class="metric-secondary">', unsafe_allow_html=True)


def close_metric_secondary() -> None:
    """Close container wrapper for secondary operational metric cards."""
    st.markdown('</div>', unsafe_allow_html=True)


def render_vertical_spacer() -> None:
    """Render a clean vertical spacing divider."""
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
