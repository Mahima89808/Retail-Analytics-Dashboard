"""
History Page

Responsibilities:
- List previously saved analyses.
- Allow viewing, renaming, and deleting saved analyses.
- Provide export buttons per record: PDF report and KPI CSV.
  (Dataset CSV is not available here — the mapped dataset isn't
  persisted to Supabase, per architecture decision. PDF omits the
  Rule Evaluation section — rule_results isn't persisted either;
  see reporting/exporter.py docstring.)

No analytics calculations happen here — this page only
reads from and writes to the repository layer, and passes
saved record data to reporting/exporter.py for formatting.
"""

import streamlit as st

from database.repository import (
    get_all_analyses,
    rename_analysis,
    delete_analysis,
)
from reporting.exporter import generate_pdf_report, generate_kpi_csv


def show_history_page() -> None:
    """Display the history page."""

    st.title("🕘 History")

    try:
        records = get_all_analyses()

    except Exception as error:
        st.error(f"Failed to load history: {error}")
        return

    if not records:
        st.info("No saved analyses yet. Save one from the Analysis page.")
        return

    st.write(f"{len(records)} saved analysis record(s).")

    st.divider()

    for record in records:

        with st.container(border=True):

            st.subheader(record.report_name)
            st.caption(
                f"File: {record.uploaded_file} • "
                f"Rows: {record.total_rows} • "
                f"Columns: {record.total_columns} • "
                f"Saved: {record.created_at}"
            )

            with st.expander("View Details"):

                st.write("**KPIs**")
                st.json(record.kpis)

                st.write("**Insights**")
                if record.insights:
                    for insight in record.insights:
                        st.warning(insight)
                else:
                    st.success("No concerning trends were found for this analysis.")

                st.write("**Recommendations**")
                if record.recommendations:
                    for recommendation in record.recommendations:
                        st.write(f"- {recommendation}")
                else:
                    st.info("No recommendations were generated for this analysis.")

            export_col, rename_col, delete_col = st.columns(3)

            with export_col:
                pdf_bytes = generate_pdf_report(
                    kpis=record.kpis,
                    rule_results=None,
                    insights=record.insights,
                    recommendations=record.recommendations,
                    report_title=record.report_name,
                )
                st.download_button(
                    label="📄 PDF",
                    data=pdf_bytes,
                    file_name=f"{record.report_name}.pdf",
                    mime="application/pdf",
                    key=f"download_pdf_{record.id}",
                )

                kpi_csv_bytes = generate_kpi_csv(record.kpis)
                st.download_button(
                    label="📊 KPI CSV",
                    data=kpi_csv_bytes,
                    file_name=f"{record.report_name}_kpis.csv",
                    mime="text/csv",
                    key=f"download_kpi_csv_{record.id}",
                )

            with rename_col:
                new_name = st.text_input(
                    "Rename",
                    value=record.report_name,
                    key=f"rename_input_{record.id}",
                    label_visibility="collapsed",
                )

                if st.button("Rename", key=f"rename_button_{record.id}"):
                    success = rename_analysis(record.id, new_name.strip())

                    if success:
                        st.success("Renamed successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to rename analysis.")

            with delete_col:
                if st.button("🗑️ Delete", key=f"delete_button_{record.id}"):
                    success = delete_analysis(record.id)

                    if success:
                        st.success("Deleted successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to delete analysis.")