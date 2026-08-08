"""
Home Page

Responsibilities:
- Allow the user to upload a retail dataset (CSV or Excel).
- Display basic file information.
- Display a preview of the uploaded dataset.
- Map uploaded columns to canonical column names.
- Display the resulting column mapping.
- Report data-quality issues (missing values, duplicates, type issues).
- Validate that required canonical columns are present.

Analytics logic is handled by later pipeline stages.
"""

import streamlit as st

from core.loader import load_dataset
from core.column_mapper import map_columns
from core.cleaner import analyze_data_quality
from core.validator import validate_dataset, get_validation_summary
from config.settings import SUPPORTED_FILE_TYPES


def show_home_page() -> None:
    """Display the home page and handle dataset upload."""

    st.title("🏠 Home")

    st.write("Upload a retail or business dataset to begin analysis.")

    allowed_types = [ext.lstrip(".") for ext in SUPPORTED_FILE_TYPES]

    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=allowed_types,
        accept_multiple_files=False,
    )

    if uploaded_file is None:
        st.info("No file uploaded yet.")
        return

    try:
        raw_dataframe = load_dataset(uploaded_file)

    except (ValueError, RuntimeError) as error:
        st.error(str(error))
        st.session_state.raw_dataset = None
        st.session_state.mapped_dataset = None
        st.session_state.uploaded_filename = None
        st.session_state.dataset_valid = False
        return

    st.session_state.raw_dataset = raw_dataframe
    st.session_state.uploaded_filename = uploaded_file.name

    mapped_dataframe = map_columns(raw_dataframe)
    st.session_state.mapped_dataset = mapped_dataframe

    st.success(f"Dataset '{uploaded_file.name}' loaded successfully.")

    st.divider()

    st.header("File Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("File Name", uploaded_file.name)

    with col2:
        st.metric("Total Rows", raw_dataframe.shape[0])

    with col3:
        st.metric("Total Columns", raw_dataframe.shape[1])

    st.divider()

    st.header("Dataset Preview")

    st.dataframe(raw_dataframe.head(10), use_container_width=True)

    st.caption("Showing the first 10 rows of the uploaded dataset.")

    st.divider()

    st.header("Column Mapping")

    original_columns = list(raw_dataframe.columns)
    mapped_columns = list(mapped_dataframe.columns)

    column_mapping = dict(zip(original_columns, mapped_columns))
    st.session_state.column_mapping = column_mapping

    mapping_rows = [
        {"Uploaded Column": original, "Mapped To": mapped}
        for original, mapped in zip(original_columns, mapped_columns)
    ]

    st.dataframe(mapping_rows, use_container_width=True, hide_index=True)

    st.caption(
        f"{len(mapped_columns)} column(s) processed. "
        "Columns not matching a known alias are kept as uploaded."
    )

    st.divider()

    st.header("Data Quality Report")

    quality = analyze_data_quality(mapped_dataframe)
    st.session_state.data_quality = quality

    if not quality["has_issues"]:
        st.success("No data quality issues detected.")

    else:
        if quality["missing_values"]:
            st.warning("Missing values detected in the following column(s):")
            st.json(quality["missing_values"])

        if quality["duplicate_rows"] > 0:
            st.warning(f"{quality['duplicate_rows']} duplicate row(s) detected.")

        if quality["type_issues"]:
            st.warning(
                "The following column(s) contain non-numeric values "
                "where numeric data was expected:"
            )
            st.json(quality["type_issues"])

        st.info(
            "These issues are currently for visibility only and are not "
            "automatically corrected. Analysis will run on the dataset as-is."
        )

    st.divider()

    st.header("Validation")

    validation_summary = get_validation_summary(mapped_dataframe.columns)
    st.session_state.validation_summary = validation_summary

    try:
        validate_dataset(mapped_dataframe.columns)

    except ValueError as error:
        st.session_state.dataset_valid = False
        st.error(str(error))
        st.warning("Please upload a dataset containing all required columns.")
        return

    st.session_state.dataset_valid = True
    st.success("Dataset validated successfully. All required columns are present.")

    st.divider()

    if st.button("➡️ Go to Analysis", type="primary", use_container_width=True):
        st.switch_page(st.session_state.pages["analysis"])