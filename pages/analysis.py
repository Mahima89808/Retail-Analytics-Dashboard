"""
Analysis Page

Responsibilities:
- Run the analytics pipeline on the validated, mapped dataset.
- Display calculated KPIs.
- Display rule evaluation status.
- Display generated insights.
- Allow saving the analysis to history.

Recommendations are displayed on the Report page.
No calculation logic lives here — this page only calls
analytics/engine.py and displays its output.
"""

import streamlit as st

from analytics.engine import run_analysis
from database.repository import save_analysis
from database.models import AnalysisRecord


def show_analysis_page() -> None:
    """Display the analysis page."""

    st.title("📈 Analysis")

    if st.session_state.mapped_dataset is None:
        st.warning("No dataset uploaded yet.")
        st.info("Please go to the **Home** page and upload a dataset first.")
        return

    if not st.session_state.dataset_valid:
        st.warning("The uploaded dataset did not pass validation.")
        st.info("Please go to the **Home** page and upload a valid dataset.")
        return

    result = run_analysis(st.session_state.mapped_dataset)
    st.session_state.analysis_result = result

    kpis = result["kpis"]
    rule_results = result["rule_results"]
    insights = result["insights"]
    recommendations = result["recommendations"]

    # ----------------------------------------------------
    # KPIs
    # ----------------------------------------------------

    st.header("Key Performance Indicators")

    kpi_items = list(kpis.items())

    for row_start in range(0, len(kpi_items), 4):
        row_items = kpi_items[row_start:row_start + 4]
        columns = st.columns(len(row_items))

        for column, (kpi_name, value) in zip(columns, row_items):
            label = kpi_name.replace("_", " ").title()

            if isinstance(value, float):
                display_value = f"{value:,.2f}"
            else:
                display_value = f"{value:,}"

            column.metric(label, display_value)

    st.divider()

    # ----------------------------------------------------
    # Rule Evaluation
    # ----------------------------------------------------

    st.header("Rule Evaluation")

    if not rule_results:
        st.info("No rule-evaluated metrics available for this dataset.")

    else:
        status_icons = {
            "normal": "🟢",
            "warning": "🟡",
            "critical": "🔴",
        }

        for metric, data in rule_results.items():
            label = metric.replace("_", " ").title()
            icon = status_icons.get(data["status"], "⚪")

            st.write(
                f"{icon} **{label}**: {data['value']:.2f} "
                f"(status: {data['status']})"
            )

    st.divider()

    # ----------------------------------------------------
    # Insights
    # ----------------------------------------------------

    st.header("Business Insights")

    if not insights:
        st.success("No concerning trends detected. All metrics are within normal range.")

    else:
        for insight in insights:
            st.warning(insight)

    st.divider()

    # ----------------------------------------------------
    # Save Analysis
    # ----------------------------------------------------

    st.header("Save This Analysis")

    default_name = f"Analysis - {st.session_state.uploaded_filename or 'Untitled'}"

    report_name = st.text_input("Report name", value=default_name)

    if st.button("💾 Save Analysis", type="primary"):

        record = AnalysisRecord(
            report_name=report_name.strip() or default_name,
            uploaded_file=st.session_state.uploaded_filename or "Unknown",
            total_rows=st.session_state.raw_dataset.shape[0],
            total_columns=st.session_state.raw_dataset.shape[1],
            mapped_columns=st.session_state.column_mapping or {},
            validation_summary=st.session_state.validation_summary or {},
            kpis=kpis,
            insights=insights,
            recommendations=recommendations,
        )

        try:
            saved = save_analysis(record)

        except Exception as error:
            st.error(f"Failed to save analysis: {error}")

        else:
            st.success(f"Analysis '{saved.report_name}' saved successfully.")

    st.divider()

    st.info("View actionable recommendations for this dataset on the **Report** page.")