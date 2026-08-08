"""
Report Page

Responsibilities:
- Display actionable recommendations generated from the current analysis.

No calculation logic lives here — this page only reads
st.session_state.analysis_result, produced by the Analysis page.
"""

import streamlit as st


def show_report_page() -> None:
    """Display the report page."""

    st.title("📋 Report")

    if st.session_state.analysis_result is None:
        st.warning("No analysis has been run yet.")
        st.info("Please go to the **Analysis** page first.")
        return

    recommendations = st.session_state.analysis_result["recommendations"]

    st.header("Recommendations")

    if not recommendations:
        st.success("No recommendations at this time. All metrics are within normal range.")

    else:
        for recommendation in recommendations:
            st.write(f"- {recommendation}")