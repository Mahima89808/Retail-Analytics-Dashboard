"""
Retail Analytics Dashboard
Application Entry Point

Responsibilities:
- Configure Streamlit application
- Initialize application session state
- Load the landing page

Business logic must NOT be implemented here.
"""

import streamlit as st

from pages.landing import show_landing_page


# ----------------------------------------------------
# Streamlit Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------
# Session State Initialization
# ----------------------------------------------------

if "dashboard_started" not in st.session_state:
    st.session_state.dashboard_started = False


# ----------------------------------------------------
# Application Entry
# ----------------------------------------------------

show_landing_page()