"""
Report Page

Responsibilities:
- Display actionable recommendations generated from the current analysis.
- Provide export buttons for the full PDF report and CSV data
  (KPI summary and cleaned/mapped dataset).

No calculation logic lives here — this page only reads
st.session_state.analysis_result (produced by the Analysis page) and
st.session_state.mapped_dataset (produced by the Home page), and passes
them to reporting/exporter.py for formatting.
"""

import streamlit as st

from reporting.exporter import (
    generate_pdf_report,
    generate_kpi_csv,
    generate_dataset_csv,
)
from config.settings import DEFAULT_REPORT_NAME


def show_report_page() -> None:
    """Display the report page."""

    st.title("📋 Report")

    if st.session_state.analysis_result is None:
        st.warning("No analysis has been run yet.")
        st.info("Please go to the **Analysis** page first.")
        return

    analysis_result = st.session_state.analysis_result
    kpis = analysis_result["kpis"]
    rule_results = analysis_result["rule_results"]
    insights = analysis_result["insights"]
    recommendations = analysis_result["recommendations"]

    st.header("Recommendations")

    if not recommendations:
        st.success("No recommendations at this time. All metrics are within normal range.")
    else:
        for recommendation in recommendations:
            clean_recommendation = str(recommendation).lstrip("*- ").strip()
            st.markdown(f"- {clean_recommendation}")
    st.divider()
    st.header("Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        pdf_bytes = generate_pdf_report(
            kpis=kpis,
            rule_results=rule_results,
            insights=insights,
            recommendations=recommendations,
            report_title=DEFAULT_REPORT_NAME,
        )
        st.download_button(
            label="📄 Download Full Report (PDF)",
            data=pdf_bytes,
            file_name="retail_analysis_report.pdf",
            mime="application/pdf",
            key="download_pdf_report",
        )

    with col2:
        kpi_csv_bytes = generate_kpi_csv(kpis)
        st.download_button(
            label="📊 Download KPI Summary (CSV)",
            data=kpi_csv_bytes,
            file_name="kpi_summary.csv",
            mime="text/csv",
            key="download_kpi_csv",
        )

    with col3:
        mapped_dataset = st.session_state.get("mapped_dataset")
        if mapped_dataset is not None:
            dataset_csv_bytes = generate_dataset_csv(mapped_dataset)
            st.download_button(
                label="🗂️ Download Cleaned Dataset (CSV)",
                data=dataset_csv_bytes,
                file_name="cleaned_dataset.csv",
                mime="text/csv",
                key="download_dataset_csv",
            )
        else:
            st.caption("Dataset unavailable for export (not found in session).")

    st.info(
        "Checkout the saved Analysis "
        
    )
    if st.button(
        "➡️ History",
        type="primary",
        use_container_width=True,
    ):

        st.switch_page(
            st.session_state.pages["history"]
        )