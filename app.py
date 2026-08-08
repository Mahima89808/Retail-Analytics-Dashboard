"""
Retail Analytics Dashboard
Application Entry Point

Responsibilities:
- Configure Streamlit application
- Initialize application session state
- Register sidebar navigation pages

Business logic must NOT be implemented here.
"""

import streamlit as st

from pages.landing import show_landing_page
from pages.home import show_home_page
from pages.analysis import show_analysis_page
from pages.report import show_report_page
from pages.history import show_history_page


# ----------------------------------------------------
# Streamlit Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------
# Session State Initialization
# ----------------------------------------------------

if "raw_dataset" not in st.session_state:
    st.session_state.raw_dataset = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "mapped_dataset" not in st.session_state:
    st.session_state.mapped_dataset = None

if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = None

if "validation_summary" not in st.session_state:
    st.session_state.validation_summary = None

if "dataset_valid" not in st.session_state:
    st.session_state.dataset_valid = False

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "data_quality" not in st.session_state:
    st.session_state.data_quality = None


# ----------------------------------------------------
# Sidebar Navigation
# ----------------------------------------------------

overview_page = st.Page(show_landing_page, title="Overview", icon="⚡", default=True)
home_page = st.Page(show_home_page, title="Home", icon="🏠")
analysis_page = st.Page(show_analysis_page, title="Analysis", icon="📈")
report_page = st.Page(show_report_page, title="Report", icon="📋")
history_page = st.Page(show_history_page, title="History", icon="🕘")

# Store page references so other pages (e.g. Overview) can switch to them.
st.session_state.pages = {
    "overview": overview_page,
    "home": home_page,
    "analysis": analysis_page,
    "report": report_page,
    "history": history_page,
}

pg = st.navigation([overview_page, home_page, analysis_page, report_page, history_page])
pg.run()