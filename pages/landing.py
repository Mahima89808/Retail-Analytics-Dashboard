"""
Landing Page

Responsibilities:
- Introduce the application
- Explain supported datasets
- Display required and optional columns
- Show application workflow
"""

import streamlit as st


def show_landing_page() -> None:
    """Display the landing page."""

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

    st.info(
        "Supported file formats: CSV (.csv) and Excel (.xlsx)"
    )

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

    st.header("Workflow")

    st.markdown(
        """
1. Upload dataset
2. Validate dataset
3. Map columns
4. Generate KPIs
5. Generate insights
6. Generate recommendations
7. Export report
8. Save analysis history
"""
    )

    st.divider()

    if st.button(
        "Enter Dashboard",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.dashboard_started = True
        st.success("Dashboard will be available after implementing the Home page.")