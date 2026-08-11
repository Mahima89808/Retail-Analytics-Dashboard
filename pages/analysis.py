"""
Analysis Page

Responsibilities:

- Run the analytics pipeline on the validated, mapped dataset.
- Display calculated scalar KPIs.
- Display optional cost-ratio KPIs when available.
- Display capability-driven grouped analysis.
- Display business visualizations and Top-N breakdowns.
- Display scalar and grouped rule evaluation results.
- Display generated business insights.
- Allow saving the analysis to history.

Recommendations are displayed on the Report page.

No calculation or business-rule logic lives here. This page only
calls analytics/engine.py and presents its output.
"""

# Standard library imports

from typing import Dict, Iterable, Tuple


# Third-party imports

import pandas as pd
import plotly.express as px
import streamlit as st


# Local application imports

from analytics.engine import run_analysis
from database.models import AnalysisRecord
from database.repository import save_analysis


# ----------------------------------------------------
# Display Configuration
# ----------------------------------------------------

KPI_DISPLAY_NAMES = {
    "total_sales": "Total Sales",
    "total_records": "Total Records",
    "total_profit": "Total Profit",
    "profit_margin": "Profit Margin",
    "total_orders": "Total Orders",
    "total_quantity": "Total Quantity",
    "average_discount": "Average Discount",
}


COST_RATIO_DISPLAY_NAMES = {
    "employee_salary_ratio": "Employee Salary",
    "rent_ratio": "Rent",
    "electricity_ratio": "Electricity",
    "logistics_ratio": "Logistics",
    "marketing_ratio": "Marketing",
    "supplier_ratio": "Supplier",
    "manufacturing_ratio": "Manufacturing",
    "warehouse_ratio": "Warehouse",
}


GROUPED_DISPLAY_NAMES = {
    "category_sales": "Category Sales",
    "category_profit": "Category Profit",
    "subcategory_sales": "Subcategory Sales",
    "subcategory_profit": "Subcategory Profit",
    "product_sales": "Product Sales",
    "product_profit": "Product Profit",
    "customer_sales": "Customer Sales",
    "customer_profit": "Customer Profit",
    "region_sales": "Region Sales",
    "region_profit": "Region Profit",
    "state_sales": "State Sales",
    "state_profit": "State Profit",
    "city_sales": "City Sales",
    "city_profit": "City Profit",
    "country_sales": "Country Sales",
    "country_profit": "Country Profit",
}


GROUP_DIMENSIONS = (
    ("category_sales", "category_profit", "Category"),
    ("subcategory_sales", "subcategory_profit", "Subcategory"),
    ("product_sales", "product_profit", "Product"),
    ("customer_sales", "customer_profit", "Customer"),
    ("region_sales", "region_profit", "Region"),
    ("state_sales", "state_profit", "State"),
    ("city_sales", "city_profit", "City"),
    ("country_sales", "country_profit", "Country"),
)


STATUS_ICONS = {
    "normal": "🟢",
    "warning": "🟡",
    "critical": "🔴",
    "not_applicable": "⚪",
}


STATUS_LABELS = {
    "normal": "Normal",
    "warning": "Warning",
    "critical": "Critical",
    "not_applicable": "Not Applicable",
}

GROUP_PLURALS = {
    "category": "categories",
    "subcategory": "subcategories",
    "product": "products",
    "customer": "customers",
    "region": "regions",
    "state": "states",
    "city": "cities",
    "country": "countries",
}


# ----------------------------------------------------
# Formatting Helpers
# ----------------------------------------------------

def _display_label(name: str) -> str:
    """Convert an internal KPI/rule name into a readable label."""

    return name.replace("_", " ").title()


def _format_scalar_kpi(kpi_name: str, value) -> str:
    """Format a scalar KPI for display."""

    if kpi_name == "profit_margin":
        return f"{float(value):,.2f}%"

    if kpi_name == "average_discount":
        return f"{float(value):,.2f}"

    if isinstance(value, float):
        return f"{value:,.2f}"

    if isinstance(value, int):
        return f"{value:,}"

    return str(value)


def _format_currency(value) -> str:
    """Format a numeric business value for display."""

    return f"{float(value):,.2f}"


def _format_percentage(value) -> str:
    """Format a numeric percentage for display."""

    return f"{float(value):,.2f}%"


def _sorted_breakdown(
    breakdown: Dict[str, float],
) -> list[Tuple[str, float]]:
    """Return grouped KPI values sorted from highest to lowest."""

    return sorted(
        breakdown.items(),
        key=lambda item: item[1],
        reverse=True,
    )


def _format_threshold(
    value,
    direction: str,
) -> str:
    """Format a rule threshold for display."""

    formatted_value = _format_percentage(value)

    if direction == "lower":
        return f"below {formatted_value}"

    if direction == "higher":
        return f"above {formatted_value}"

    return formatted_value


# ----------------------------------------------------
# KPI Display
# ----------------------------------------------------

def _display_scalar_kpis(kpis: dict) -> None:
    """Display available scalar KPIs as metric cards."""

    scalar_items = [
        (name, value)
        for name, value in kpis.items()
        if not isinstance(value, dict)
    ]

    if not scalar_items:
        st.info(
            "No scalar KPIs are available for this dataset."
        )
        return

    for row_start in range(0, len(scalar_items), 4):

        row_items = scalar_items[
            row_start:row_start + 4
        ]

        columns = st.columns(len(row_items))

        for column, (kpi_name, value) in zip(
            columns,
            row_items,
        ):

            label = KPI_DISPLAY_NAMES.get(
                kpi_name,
                _display_label(kpi_name),
            )

            display_value = _format_scalar_kpi(
                kpi_name,
                value,
            )

            column.metric(
                label,
                display_value,
            )


def _display_cost_ratios(kpis: dict) -> None:
    """Display available cost ratios."""

    available_ratios = [
        (name, value)
        for name, value in COST_RATIO_DISPLAY_NAMES.items()
        if name in kpis
    ]

    if not available_ratios:
        return

    st.subheader("Cost Ratios")

    st.caption(
        "Cost ratios show each available operating cost "
        "as a percentage of total sales."
    )

    for row_start in range(0, len(available_ratios), 4):

        row_items = available_ratios[
            row_start:row_start + 4
        ]

        columns = st.columns(len(row_items))

        for column, (kpi_name, label) in zip(
            columns,
            row_items,
        ):

            column.metric(
                label,
                _format_percentage(
                    kpis[kpi_name]
                ),
            )


# ----------------------------------------------------
# Grouped Analysis
# ----------------------------------------------------

def _build_grouped_dataframe(
    sales_data: Dict[str, float],
    profit_data: Dict[str, float] | None = None,
) -> pd.DataFrame:
    """Build a presentation dataframe from grouped KPI dictionaries."""

    rows = []

    for group, sales in sales_data.items():

        row = {
            "Group": group,
            "Sales": float(sales),
        }

        if (
            profit_data is not None
            and group in profit_data
        ):

            profit = float(
                profit_data[group]
            )

            row["Profit"] = profit

            if sales != 0:
                row["Profit Margin"] = (
                    profit / float(sales)
                ) * 100

            else:
                row["Profit Margin"] = 0.0

        rows.append(row)

    return pd.DataFrame(rows)


def _display_grouped_analysis(
    dimension_name: str,
    sales_kpi_name: str,
    profit_kpi_name: str,
    kpis: dict,
) -> None:
    """Display one capability-driven grouped analysis section."""

    if sales_kpi_name not in kpis:
        return

    sales_data = kpis[sales_kpi_name]

    if (
        not isinstance(sales_data, dict)
        or not sales_data
    ):
        return

    profit_data = kpis.get(
        profit_kpi_name
    )

    if not isinstance(profit_data, dict):
        profit_data = None

    dataframe = _build_grouped_dataframe(
        sales_data=sales_data,
        profit_data=profit_data,
    )

    if dataframe.empty:
        return

    st.subheader(
        f"{dimension_name} Analysis"
    )

    # ------------------------------------------------
    # Top-N selection
    # ------------------------------------------------

    group_count = len(dataframe)

    sorted_dataframe = (
        dataframe
        .sort_values(
            "Sales",
            ascending=False,
        )
        .copy()
    )

    if group_count <= 5:

        # Small datasets do not need a slider.
        # Display every available group.
        top_sales = sorted_dataframe

    else:

        max_top_n = min(
            20,
            group_count,
        )

        default_top_n = min(
            10,
            group_count,
        )

        top_n = st.slider(
            f"Show top {dimension_name.lower()}s by sales",
            min_value=5,
            max_value=max_top_n,
            value=default_top_n,
            key=f"top_n_{sales_kpi_name}",
        )

        top_sales = (
            sorted_dataframe
            .head(top_n)
            .copy()
        )

    # ------------------------------------------------
    # Sales Chart
    # ------------------------------------------------

    st.markdown("**Sales Distribution**")

    sales_chart = px.bar(
        top_sales,
        x="Group",
        y="Sales",
        title=f"Top {dimension_name}s by Sales",
        labels={
            "Group": dimension_name,
            "Sales": "Sales",
        },
    )

    sales_chart.update_layout(
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20,
        ),
    )

    st.plotly_chart(
        sales_chart,
        use_container_width=True,
    )

    # ------------------------------------------------
    # Profit Chart
    # ------------------------------------------------

    if "Profit" in top_sales.columns:

        st.markdown("**Profit Performance**")

        profit_chart = px.bar(
            top_sales,
            x="Group",
            y="Profit",
            title=f"Top {dimension_name}s by Profit",
            labels={
                "Group": dimension_name,
                "Profit": "Profit",
            },
        )

        profit_chart.update_layout(
            showlegend=False,
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20,
            ),
        )

        st.plotly_chart(
            profit_chart,
            use_container_width=True,
        )

    # ------------------------------------------------
    # Detail Table
    # ------------------------------------------------

    display_columns = [
        "Group",
        "Sales",
    ]

    if "Profit" in top_sales.columns:
        display_columns.extend(
            [
                "Profit",
                "Profit Margin",
            ]
        )

    display_table = top_sales[
        display_columns
    ].copy()

    display_table["Sales"] = (
        display_table["Sales"]
        .map(_format_currency)
    )

    if "Profit" in display_table.columns:

        display_table["Profit"] = (
            display_table["Profit"]
            .map(_format_currency)
        )

    if "Profit Margin" in display_table.columns:

        display_table["Profit Margin"] = (
            display_table["Profit Margin"]
            .map(_format_percentage)
        )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
    )


def _display_all_grouped_analysis(
    kpis: dict,
) -> None:
    """Display all grouped capabilities available in the KPI result."""

    available_dimensions = []

    for (
        sales_kpi_name,
        profit_kpi_name,
        dimension_name,
    ) in GROUP_DIMENSIONS:

        if sales_kpi_name in kpis:

            available_dimensions.append(
                (
                    sales_kpi_name,
                    profit_kpi_name,
                    dimension_name,
                )
            )

    if not available_dimensions:

        st.info(
            "No grouped analysis is available "
            "for this dataset."
        )

        return

    tabs = st.tabs(
        [
            dimension_name
            for (
                _,
                _,
                dimension_name,
            ) in available_dimensions
        ]
    )

    for tab, (
        sales_kpi_name,
        profit_kpi_name,
        dimension_name,
    ) in zip(
        tabs,
        available_dimensions,
    ):

        with tab:

            _display_grouped_analysis(
                dimension_name=dimension_name,
                sales_kpi_name=sales_kpi_name,
                profit_kpi_name=profit_kpi_name,
                kpis=kpis,
            )


# ----------------------------------------------------
# Rule Evaluation
# ----------------------------------------------------

def _display_rule_thresholds(
    data: dict,
) -> None:
    """Display configured rule thresholds."""

    direction = data.get(
        "direction"
    )

    warning = data.get(
        "warning_threshold"
    )

    critical = data.get(
        "critical_threshold"
    )

    if warning is None or critical is None:
        return

    warning_text = _format_threshold(
        warning,
        direction,
    )

    critical_text = _format_threshold(
        critical,
        direction,
    )

    st.caption(
        f"Warning: {warning_text} | "
        f"Critical: {critical_text}"
    )

def _display_scalar_rule(
    metric: str,
    data: dict,
) -> None:
    """Display a scalar rule result."""

    status = data["status"]

    icon = STATUS_ICONS.get(
        status,
        "⚪",
    )

    status_label = STATUS_LABELS.get(
        status,
        status.replace("_", " ").title(),
    )

    label = _display_label(metric)

    value = data["value"]

    if metric == "profit_margin":
        formatted_value = _format_percentage(value)
    else:
        formatted_value = _format_percentage(value)

    st.write(
        f"{icon} **{label}** — "
        f"{formatted_value} "
        f"({status_label})"
    )

    _display_rule_thresholds(data)

def _display_grouped_rule(
    metric: str,
    data: dict,
) -> None:
    """Display a grouped rule and its individual violations."""

    status = data["status"]

    icon = STATUS_ICONS.get(
        status,
        "⚪",
    )

    status_label = STATUS_LABELS.get(
        status,
        status.replace("_", " ").title(),
    )

    label = _display_label(metric)

    warning_threshold = data.get(
        "warning_threshold"
    )

    critical_threshold = data.get(
        "critical_threshold"
    )

    direction = data.get("direction")

    # ------------------------------------------------
    # Rule Header
    # ------------------------------------------------

    st.write(
        f"{icon} **{label}** — {status_label}"
    )

    # ------------------------------------------------
    # Threshold Description
    # ------------------------------------------------

    if (
        warning_threshold is not None
        and critical_threshold is not None
    ):

        if direction == "lower":

            st.caption(
                f"Warning: below "
                f"{_format_percentage(warning_threshold)} "
                f"| Critical: below "
                f"{_format_percentage(critical_threshold)}"
            )

        elif direction == "higher":

            st.caption(
                f"Warning: above "
                f"{_format_percentage(warning_threshold)} "
                f"| Critical: above "
                f"{_format_percentage(critical_threshold)}"
            )

    # ------------------------------------------------
    # Not Applicable
    # ------------------------------------------------

    if status == "not_applicable":

        reason = data.get(
            "reason",
            "There is insufficient data to evaluate "
            "this rule meaningfully.",
        )

        st.info(
            f"Not applicable: {reason}"
        )

        return

    # ------------------------------------------------
    # Violations
    # ------------------------------------------------

    violations = data.get(
        "violations",
        [],
    )

    if not violations:

        if status == "normal":

            dimension = metric.replace(
                "_sales_concentration",
                "",
            ).replace(
                "_profit_margin",
                "",
            )

            plural = GROUP_PLURALS.get(
                dimension,
                f"{dimension}s",
            )

            if metric.endswith(
                "_sales_concentration"
            ):

                st.caption(
                    f"No {plural} exceed the configured "
                    "concentration threshold."
                )

            elif metric.endswith(
                "_profit_margin"
            ):

                st.caption(
                    f"No {plural} fall below the configured "
                    "profitability threshold."
                )

            else:

                st.caption(
                    "No groups violate the configured "
                    "thresholds."
                )

        return

    # ------------------------------------------------
    # Violation Summary
    # ------------------------------------------------

    critical_count = sum(
        1
        for violation in violations
        if violation["status"] == "critical"
    )

    warning_count = sum(
        1
        for violation in violations
        if violation["status"] == "warning"
    )

    total_violations = len(violations)

    st.write(
        f"**{total_violations} group(s) require attention** "
        f"({critical_count} critical, "
        f"{warning_count} warning)."
    )

    # ------------------------------------------------
    # Violation Table
    # ------------------------------------------------

    violation_rows = []

    for violation in violations:

                violation_status = violation["status"]

                violation_status_label = STATUS_LABELS.get(
                    violation_status,
                    violation_status.replace("_", " ").title(),
                )

                violation_rows.append(
                    {
                        "Group": violation["group"],
                        "Value": _format_percentage(
                            violation["value"]
                        ),
                        "Status": (
                            f"{STATUS_ICONS.get(violation_status, '⚪')} "
                            f"{violation_status_label}"
                        ),
                    }
                )

    st.dataframe(
        violation_rows,
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------
    # Worst / Highest
    # ------------------------------------------------

    if metric.endswith("_profit_margin"):

        worst = min(
            violations,
            key=lambda violation: violation["value"],
        )

        st.caption(
            f"**Worst performer:** "
            f"{worst['group']} "
            f"({_format_percentage(worst['value'])})"
        )

    elif metric.endswith("_sales_concentration"):

        highest = max(
            violations,
            key=lambda violation: violation["value"],
        )

        st.caption(
            f"**Highest concentration:** "
            f"{highest['group']} "
            f"({_format_percentage(highest['value'])})"
        )

def _display_rule_evaluation(
    rule_results: dict,
) -> None:
    """Display scalar and grouped rule evaluation results."""

    if not rule_results:

        st.info(
            "No rule-evaluated metrics are available "
            "for this dataset."
        )

        return

    for metric, data in rule_results.items():

        if data.get("rule_type") == "grouped":
            _display_grouped_rule(
                metric,
                data,
            )

        else:
            _display_scalar_rule(
                metric,
                data,
            )

        st.divider()


# ----------------------------------------------------
# Insights
# ----------------------------------------------------

def _display_insights(
    insights: Iterable[str],
) -> None:
    """Display generated business insights."""

    insights = list(insights)

    if not insights:

        st.success(
            "No concerning business conditions "
            "were detected by the configured rules."
        )

        return

    for insight in insights:

        st.warning(
            insight
        )


# ----------------------------------------------------
# Save Analysis
# ----------------------------------------------------

def _save_current_analysis(
    kpis: dict,
    insights: list[str],
    recommendations: list[str],
) -> None:
    """Save the current analysis using the existing repository interface."""

    st.header("Save This Analysis")

    default_name = (
        f"Analysis - "
        f"{st.session_state.uploaded_filename or 'Untitled'}"
    )

    report_name = st.text_input(
        "Report name",
        value=default_name,
    )

    if not st.button(
        "💾 Save Analysis",
        type="primary",
    ):
        return

    record = AnalysisRecord(
        report_name=(
            report_name.strip()
            or default_name
        ),
        uploaded_file=(
            st.session_state.uploaded_filename
            or "Unknown"
        ),
        total_rows=(
            st.session_state.raw_dataset.shape[0]
        ),
        total_columns=(
            st.session_state.raw_dataset.shape[1]
        ),
        mapped_columns=(
            st.session_state.column_mapping
            or {}
        ),
        validation_summary=(
            st.session_state.validation_summary
            or {}
        ),
        kpis=kpis,
        insights=insights,
        recommendations=recommendations,
    )

    try:

        saved = save_analysis(
            record
        )

    except Exception as error:

        st.error(
            f"Failed to save analysis: {error}"
        )

    else:

        st.success(
            f"Analysis '{saved.report_name}' "
            "saved successfully."
        )


# ----------------------------------------------------
# Main Page
# ----------------------------------------------------

def show_analysis_page() -> None:
    """Display the analysis page."""

    st.title("📈 Analysis")

    # ------------------------------------------------
    # Dataset Validation
    # ------------------------------------------------

    if st.session_state.mapped_dataset is None:

        st.warning(
            "No dataset uploaded yet."
        )

        st.info(
            "Please go to the **Home** page and "
            "upload a dataset first."
        )

        return

    if not st.session_state.dataset_valid:

        st.warning(
            "The uploaded dataset did not pass validation."
        )

        st.info(
            "Please go to the **Home** page and "
            "upload a valid dataset."
        )

        return

    # ------------------------------------------------
    # Run Analytics Pipeline
    # ------------------------------------------------

    result = run_analysis(
        st.session_state.mapped_dataset
    )

    st.session_state.analysis_result = result

    kpis = result["kpis"]
    rule_results = result["rule_results"]
    insights = result["insights"]
    recommendations = result["recommendations"]

    # ------------------------------------------------
    # KPI Overview
    # ------------------------------------------------

    st.header(
        "Key Performance Indicators"
    )

    _display_scalar_kpis(
        kpis
    )

    st.divider()

    # ------------------------------------------------
    # Cost Analysis
    # ------------------------------------------------

    _display_cost_ratios(
        kpis
    )

    st.divider()

    # ------------------------------------------------
    # Detailed Analysis
    # ------------------------------------------------

    st.header(
        "Detailed Analysis"
    )

    _display_all_grouped_analysis(
        kpis
    )

    st.divider()

    # ------------------------------------------------
    # Rule Evaluation
    # ------------------------------------------------

    st.header(
        "Rule Evaluation"
    )

    st.caption(
        "Rules are evaluated against the configured "
        "business thresholds. Grouped rules show the "
        "individual groups that require attention. "
        "Not Applicable means the available data is "
        "insufficient for meaningful interpretation."
    )

    _display_rule_evaluation(
        rule_results
    )

    # ------------------------------------------------
    # Business Insights
    # ------------------------------------------------

    st.header(
        "Business Insights"
    )

    _display_insights(
        insights
    )

    st.divider()

    # ------------------------------------------------
    # Save Analysis
    # ------------------------------------------------

    _save_current_analysis(
        kpis=kpis,
        insights=insights,
        recommendations=recommendations,
    )

    st.divider()

    # ------------------------------------------------
    # Report Navigation
    # ------------------------------------------------

    st.info(
        "View actionable recommendations for this "
        "dataset on the **Report** page."
    )

    if st.button(
        "➡️ Check the Report",
        type="primary",
        use_container_width=True,
    ):

        st.switch_page(
            st.session_state.pages["report"]
        )