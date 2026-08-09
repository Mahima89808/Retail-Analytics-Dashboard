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
- Display a capability report: which analysis modules are available or
  unavailable based on which optional/recommended columns were detected.
- Before any upload, guide the user on what to upload and what each
  column category unlocks.

Analytics logic is handled by later pipeline stages.
"""

import streamlit as st

from core.loader import load_dataset
from core.column_mapper import map_columns
from core.cleaner import analyze_data_quality
from core.validator import validate_dataset, get_validation_summary, get_capability_report
from config.settings import SUPPORTED_FILE_TYPES


def _show_upload_guidance() -> None:
    """
    Pre-upload guidance: explains the minimum required columns and what
    additional columns unlock. Static content, manually cross-checked
    against core.validator.CAPABILITIES — not dynamically generated.
    """

    st.info(
        "**Minimum required:** a Sales/Revenue column and an Order/Transaction "
        "Date column. Everything else is optional — the more columns you "
        "include, the more analysis becomes available."
    )

    st.subheader("What each column unlocks")

    card_col1, card_col2, card_col3 = st.columns(3)

    with card_col1:
        with st.container(border=True):
            st.markdown("#### 🟢 Required")
            st.caption("Your dataset must include these.")
            st.markdown("**Sales / Revenue**")
            st.caption("→ Sales Analysis")
            st.divider()
            st.markdown("**Order Date / Transaction Date**")
            st.caption("→ Time Trends")

    with card_col2:
        with st.container(border=True):
            st.markdown("#### 🟡 Recommended")
            st.caption("Not required, but significantly improves the report.")
            st.markdown("**Profit / Net Profit**")
            st.caption("→ Profitability Analysis")
            st.divider()
            st.markdown("**Category / Product Category**")
            st.caption("→ Category Analysis")

    with card_col3:
        with st.container(border=True):
            st.markdown("#### 🔵 Optional")
            st.caption("Unlocks deeper, more granular analysis.")
            st.markdown("**Product ID / Product Name**")
            st.caption("→ Product Analysis")
            st.divider()
            st.markdown("**Customer ID / Customer Name**")
            st.caption("→ Customer Analysis")

    card_col4, card_col5, spacer = st.columns(3)

    with card_col4:
        with st.container(border=True):
            st.markdown("#### 🔵 Optional")
            st.markdown("**Region / State / City / Country**")
            st.caption("→ Geographic Analysis")

    with card_col5:
        with st.container(border=True):
            st.markdown("#### 🔵 Optional")
            st.markdown("**Profit + Discount + Cost**")
            st.caption("→ Cost Optimization Analysis")

    st.caption(
        "Column names don't need to match exactly — common variations "
        "(e.g. \"Revenue\", \"Net Sales\", \"orderdate\") are automatically "
        "recognized."
    )


def show_home_page() -> None:
    """Display the home page and handle dataset upload."""

    st.title("🏠 Home")

    st.write("Upload a retail or business dataset to begin analysis.")

    st.divider()

    allowed_types = [ext.lstrip(".") for ext in SUPPORTED_FILE_TYPES]

    upload_col_left, upload_col_center, upload_col_right = st.columns([1, 2, 1])

    with upload_col_center:
        uploaded_file = st.file_uploader(
            "Upload dataset",
            type=allowed_types,
            accept_multiple_files=False,
        )

    if uploaded_file is None:
        st.divider()
        _show_upload_guidance()
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

    st.header("Dataset Compatibility")

    capability_report = get_capability_report(mapped_dataframe.columns)
    st.session_state.capability_report = capability_report

    st.subheader("Available Analysis")
    if capability_report["available"]:
        for capability in capability_report["available"]:
            st.success(f"✓ {capability}")
    else:
        st.warning("No optional analysis capabilities detected.")

    st.subheader("Limited Analysis")
    if capability_report["unavailable"]:
        for entry in capability_report["unavailable"]:
            missing = ", ".join(entry["missing"])
            st.warning(f"⚠ {entry['capability']} — not detected: {missing}")
    else:
        st.success("All analysis capabilities are available for this dataset.")

    st.divider()

    if st.button("➡️ Go to Analysis", type="primary", use_container_width=True):
        st.switch_page(st.session_state.pages["analysis"])