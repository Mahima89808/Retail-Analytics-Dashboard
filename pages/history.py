"""
History Page

Responsibilities:
- List previously saved analyses.
- Allow viewing, renaming, and deleting saved analyses.

No analytics calculations happen here — this page only
reads from and writes to the repository layer.
"""

import streamlit as st

from database.repository import (
    get_all_analyses,
    rename_analysis,
    delete_analysis,
)


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

            rename_col, delete_col = st.columns(2)

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