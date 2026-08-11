"""
reporting/exporter.py

Generates downloadable report artifacts (PDF, CSV) from analysis results.

Responsibilities:
- Format KPIs for PDF/CSV export.
- Format scalar and grouped rule evaluation results.
- Format business insights and recommendations.
- Generate PDF reports.
- Generate KPI CSV files.
- Generate cleaned/mapped dataset CSV files.

This module contains presentation/export logic only.
No business calculations or threshold logic live here.

All functions return raw bytes for use with Streamlit's
st.download_button(data=...).
"""

from __future__ import annotations

import io
from typing import Any

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_label(key: str) -> str:
    """Convert a snake_case key into a human-readable label."""

    return str(key).replace("_", " ").strip().title()


def _format_value(value: Any) -> str:
    """
    Format a generic value for PDF display.

    Handles:
    - None
    - booleans
    - integers
    - floats
    - dictionaries/lists
    - strings
    """

    if value is None:
        return ""

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, int):
        return f"{value:,}"

    if isinstance(value, float):
        return f"{value:,.2f}"

    if isinstance(value, (dict, list, tuple)):
        return str(value)

    return str(value)


def _format_rule_value(value: Any) -> str:
    """
    Format a rule value.

    Rule values such as profit margins and concentration values are
    percentages, while grouped rules may not always expose a scalar value.
    """

    if value is None:
        return ""

    if isinstance(value, (int, float)):
        return f"{float(value):,.2f}%"

    return str(value)


def _format_threshold(value: Any) -> str:
    """Format a rule threshold for PDF display."""

    if value is None:
        return ""

    if isinstance(value, (int, float)):
        return f"{float(value):,.2f}%"

    return str(value)


def _ensure_text(value: Any) -> str:
    """
    Convert an insight/recommendation into plain text.

    The analytics layer should normally return list[str].

    This helper also handles accidental nested lists so the PDF exporter
    cannot crash with:
        AttributeError: 'list' object has no attribute 'split'
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, (list, tuple)):
        parts = []

        for item in value:
            text = _ensure_text(item)

            if text:
                parts.append(text)

        return " ".join(parts)

    return str(value)


def _normalise_text_list(values: Any) -> list[str]:
    """
    Convert a collection of insights/recommendations into list[str].

    Expected input:
        ["Insight one", "Insight two"]

    Also safely handles:
        [["Insight one"], ["Insight two"]]
    """

    if values is None:
        return []

    if isinstance(values, str):
        text = _ensure_text(values)

        return [text] if text else []

    if not isinstance(values, (list, tuple)):
        text = _ensure_text(values)

        return [text] if text else []

    result: list[str] = []

    for value in values:
        text = _ensure_text(value)

        if text:
            result.append(text)

    return result


# ---------------------------------------------------------------------------
# Status formatting
# ---------------------------------------------------------------------------

_STATUS_COLORS = {
    "normal": colors.HexColor("#2E7D32"),
    "warning": colors.HexColor("#F9A825"),
    "critical": colors.HexColor("#C62828"),
    "not_applicable": colors.grey,
}


def _status_color(status: str) -> colors.Color:
    """Return the display color for a rule status."""

    return _STATUS_COLORS.get(
        str(status).lower(),
        colors.black,
    )


def _status_label(status: Any) -> str:
    """Convert an internal status into a readable label."""

    if status is None:
        return ""

    return (
        str(status)
        .replace("_", " ")
        .strip()
        .title()
    )


# ---------------------------------------------------------------------------
# Grouped rule formatting
# ---------------------------------------------------------------------------

def _grouped_rule_summary(result: dict[str, Any]) -> str:
    """
    Create a compact textual summary for a grouped rule.

    Example:
        6 violations (6 critical, 0 warning).
    """

    violations = result.get("violations", [])

    if not isinstance(violations, list):
        return ""

    if not violations:
        return "No groups require attention."

    critical_count = sum(
        1
        for violation in violations
        if isinstance(violation, dict)
        and violation.get("status") == "critical"
    )

    warning_count = sum(
        1
        for violation in violations
        if isinstance(violation, dict)
        and violation.get("status") == "warning"
    )

    total_count = len(violations)

    return (
        f"{total_count} group(s) require attention "
        f"({critical_count} critical, "
        f"{warning_count} warning)."
    )


def _build_grouped_rule_rows(
    metric: str,
    result: dict[str, Any],
) -> list[list[str]]:
    """
    Build rows for a grouped rule's violation table.

    Grouped rule example:
        category_profit_margin
        category_sales_concentration
    """

    rows = [
        [
            "Group",
            "Value",
            "Status",
        ]
    ]

    violations = result.get("violations", [])

    if not isinstance(violations, list):
        return rows

    for violation in violations:

        if not isinstance(violation, dict):
            continue

        rows.append(
            [
                str(violation.get("group", "")),
                _format_rule_value(
                    violation.get("value")
                ),
                _status_label(
                    violation.get("status")
                ),
            ]
        )

    return rows


# ---------------------------------------------------------------------------
# PDF report generation
# ---------------------------------------------------------------------------

def generate_pdf_report(
    kpis: dict[str, Any],
    rule_results: dict[str, dict[str, Any]] | None,
    insights: list[str],
    recommendations: list[str],
    report_title: str = "Retail Analytics Report",
) -> bytes:
    """
    Build a PDF report from the supplied analytics results.

    Returns:
        PDF content as bytes.
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        spaceBefore=18,
        spaceAfter=8,
    )

    body_style = styles["Normal"]

    story = []

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            report_title,
            styles["Title"],
        )
    )

    story.append(
        Spacer(1, 12)
    )

    # ---------------------------------------------------------
    # Key Performance Indicators
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Key Performance Indicators",
            section_style,
        )
    )

    if kpis:

        kpi_rows = [
            ["Metric", "Value"]
        ]

        for key, value in kpis.items():

            # Grouped KPI dictionaries are not suitable
            # for direct table rendering.
            if isinstance(value, dict):

                kpi_rows.append(
                    [
                        _format_label(key),
                        "Grouped data",
                    ]
                )

            else:

                kpi_rows.append(
                    [
                        _format_label(key),
                        _format_value(value),
                    ]
                )

        kpi_table = Table(
            kpi_rows,
            colWidths=[
                3 * inch,
                2 * inch,
            ],
        )

        kpi_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#37474F"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#F5F5F5"),
                        ],
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                ]
            )
        )

        story.append(kpi_table)

    else:

        story.append(
            Paragraph(
                "No KPI data available.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # Rule Evaluation
    # ---------------------------------------------------------

    if rule_results is not None:

        story.append(
            Paragraph(
                "Rule Evaluation",
                section_style,
            )
        )

        if rule_results:

            rule_rows = [
                [
                    "Metric",
                    "Value",
                    "Status",
                    "Warning",
                    "Critical",
                ]
            ]

            row_colors = []

            for key, result in rule_results.items():

                status = str(
                    result.get(
                        "status",
                        "",
                    )
                )

                value = result.get(
                    "value"
                )

                # Grouped rules do not have a scalar
                # value. Show the number of violations.
                if result.get("rule_type") == "grouped":

                    violations = result.get(
                        "violations",
                        [],
                    )

                    display_value = (
                        f"{len(violations)} group(s)"
                    )

                else:

                    display_value = _format_value(
                        value
                    )

                rule_rows.append(
                    [
                        _format_label(key),
                        display_value,
                        status.replace(
                            "_",
                            " ",
                        ).title(),
                        _format_value(
                            result.get(
                                "warning_threshold"
                            )
                        ),
                        _format_value(
                            result.get(
                                "critical_threshold"
                            )
                        ),
                    ]
                )

                row_colors.append(
                    _status_color(status)
                )

            rule_table = Table(
                rule_rows,
                colWidths=[
                    1.8 * inch,
                    0.9 * inch,
                    0.9 * inch,
                    0.9 * inch,
                    0.9 * inch,
                ],
                repeatRows=1,
            )

            style_commands = [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#37474F"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
            ]

            for row_index, color in enumerate(
                row_colors,
                start=1,
            ):

                style_commands.append(
                    (
                        "TEXTCOLOR",
                        (2, row_index),
                        (2, row_index),
                        color,
                    )
                )

                style_commands.append(
                    (
                        "FONTNAME",
                        (2, row_index),
                        (2, row_index),
                        "Helvetica-Bold",
                    )
                )

            rule_table.setStyle(
                TableStyle(style_commands)
            )

            story.append(rule_table)

        else:

            story.append(
                Paragraph(
                    "No rule evaluation data available.",
                    body_style,
                )
            )

    # ---------------------------------------------------------
    # Business Insights
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Business Insights",
            section_style,
        )
    )

    if insights:

        insight_items = []

        for insight in insights:

            # Defensive protection:
            # if an accidental nested list reaches the
            # exporter, convert it into readable text.
            if isinstance(insight, (list, tuple)):

                text = " ".join(
                    str(item)
                    for item in insight
                )

            else:

                text = str(insight)

            insight_items.append(
                ListItem(
                    Paragraph(
                        text,
                        body_style,
                    )
                )
            )

        story.append(
            ListFlowable(
                insight_items,
                bulletType="bullet",
            )
        )

    else:

        story.append(
            Paragraph(
                "No notable insights — all metrics "
                "within normal range.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Recommendations",
            section_style,
        )
    )

    if recommendations:

        recommendation_items = []

        for recommendation in recommendations:

            if isinstance(
                recommendation,
                (list, tuple),
            ):

                text = " ".join(
                    str(item)
                    for item in recommendation
                )

            else:

                text = str(recommendation)

            recommendation_items.append(
                ListItem(
                    Paragraph(
                        text,
                        body_style,
                    )
                )
            )

        story.append(
            ListFlowable(
                recommendation_items,
                bulletType="bullet",
            )
        )

    else:

        story.append(
            Paragraph(
                "No recommendations — all metrics "
                "within normal range.",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # BUILD PDF
    # ---------------------------------------------------------

    doc.build(story)

    buffer.seek(0)

    pdf_bytes = buffer.read()

    return pdf_bytes



# ---------------------------------------------------------------------------
# CSV exports
# ---------------------------------------------------------------------------

def generate_kpi_csv(
    kpis: dict[str, Any],
) -> bytes:
    """
    Export KPI data as a two-column CSV.

    Columns:
        Metric
        Value
    """

    rows = []

    for key, value in kpis.items():

        rows.append(
            {
                "Metric": _format_label(key),
                "Value": value,
            }
        )

    dataframe = pd.DataFrame(
        rows,
        columns=[
            "Metric",
            "Value",
        ],
    )

    return dataframe.to_csv(
        index=False
    ).encode("utf-8")


def generate_dataset_csv(
    dataframe: pd.DataFrame,
) -> bytes:
    """
    Export the cleaned/mapped dataset as CSV.

    Parameters
    ----------
    dataframe:
        Cleaned/mapped pandas DataFrame.

    Returns
    -------
    bytes
        CSV content encoded as UTF-8.
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):
        raise TypeError(
            "generate_dataset_csv() expected a pandas DataFrame."
        )

    return dataframe.to_csv(
        index=False
    ).encode("utf-8")

