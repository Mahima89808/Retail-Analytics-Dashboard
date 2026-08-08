"""
Overview Page

Responsibilities:
- Introduce the application
- Explain supported datasets
- Display required and optional columns
- Guide the user to available pages via the sidebar
"""

import streamlit as st


def show_landing_page() -> None:
    """Display the overview page."""

    st.title("📊 Retail Analytics Dashboard")

    st.markdown(
        """
Analyze retail and business datasets to identify cost trends,
business performance, and optimization opportunities using
rule-based analytics.

This application works entirely offline without external AI APIs,
making it free to deploy on Streamlit Community Cloud.
"""
    )

    st.divider()

    st.header("Supported Dataset")

    st.write(
        """
Upload a CSV or Excel dataset containing retail or business data.
The application automatically maps similar column names to a
standard schema.
"""
    )

    st.info("Supported file formats: CSV (.csv) and Excel (.xlsx)")

    st.divider()

    st.header("Required Columns")

    st.markdown(
        """
- Sales
- Profit
"""
    )

    st.header("Optional Columns")

    st.markdown(
        """
- Quantity
- Discount
- Employee Salaries
- Rent
- Electricity
- Logistics Cost
- Marketing Cost
- Supplier Cost
- Manufacturing Cost
- Warehouse Cost
"""
    )

    st.divider()

    st.header("Navigation")

    st.write("Use the sidebar to access the following pages:")

    with st.container(border=True):
        st.subheader("🏠 Home")
        st.write("Upload a dataset and preview it.")

    with st.container(border=True):
        st.subheader("📈 Analysis")
        st.write("View KPIs, rule-based status, and business insights.")

    with st.container(border=True):
        st.subheader("📋 Report")
        st.write("Review actionable recommendations for this analysis.")

    with st.container(border=True):
        st.subheader("🕘 History")
        st.write("View, rename, or delete previously saved analyses.")

    st.divider()

    if st.button("Enter Dashboard", type="primary", use_container_width=True):
        st.switch_page(st.session_state.pages["home"])