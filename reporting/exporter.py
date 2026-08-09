"""
reporting/exporter.py

Generates downloadable report artifacts (PDF, CSV) from analysis results.
Pure formatting/presentation layer — no business logic, no hardcoded
column names or thresholds. Consumes the same kpis/rule_results/insights/
recommendations shapes produced by analytics/engine.run_analysis() and
stored in database/models.py's AnalysisRecord / SavedAnalysisRecord.

Note: rule_results is optional. SavedAnalysisRecord (History page) does
not persist rule_results — only kpis/insights/recommendations are saved
to Supabase. When rule_results is None, the PDF omits the Rule Evaluation
section rather than failing. (Same class of gap as the data_quality
field noted in the project checkpoint — flagged, not yet persisted.)

All functions return raw bytes for use with st.download_button(data=...).
No disk I/O, no Streamlit imports.
"""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)


# ---------------------------------------------------------------------------
# Internal formatting helpers (generic — no keyword/column-name special-casing)
# ---------------------------------------------------------------------------

def _format_label(key: str) -> str:
    """Convert a snake_case/underscore key into a human-readable label."""
    return key.replace("_", " ").strip().title()


def _format_value(value: Any) -> str:
    """Generic numeric formatting: thousands separator, 2 decimal places
    for floats, plain int formatting for ints, str() fallback otherwise."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


_STATUS_COLORS = {
    "normal": colors.HexColor("#2E7D32"),
    "warning": colors.HexColor("#F9A825"),
    "critical": colors.HexColor("#C62828"),
}


def _status_color(status: str) -> colors.Color:
    return _STATUS_COLORS.get(str(status).lower(), colors.black)


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
    Builds a PDF report: KPIs + (optional) Rule Evaluation + Insights + Recommendations.

    Args:
        kpis: output of analytics.kpi_engine.calculate_kpis()
        rule_results: output of analytics.rule_engine.evaluate_rules(), or
            None if unavailable (e.g. saved History records, which don't
            persist rule_results). When None, this section is omitted.
        insights: output of analytics.insight_generator.generate_insights()
        recommendations: output of analytics.recommendation_generator.generate_recommendations()
        report_title: heading text for the PDF

    Returns:
        PDF file content as bytes.
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

    story: list = []

    # --- Title -------------------------------------------------------
    story.append(Paragraph(report_title, styles["Title"]))
    story.append(Spacer(1, 12))

    # --- KPIs section --------------------------------------------------
    story.append(Paragraph("Key Performance Indicators", section_style))
    if kpis:
        kpi_rows = [["Metric", "Value"]]
        for key, value in kpis.items():
            kpi_rows.append([_format_label(key), _format_value(value)])

        kpi_table = Table(kpi_rows, colWidths=[3 * inch, 2 * inch])
        kpi_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#37474F")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(kpi_table)
    else:
        story.append(Paragraph("No KPI data available.", body_style))

    # --- Rule Evaluation section (optional) -----------------------------
    if rule_results is not None:
        story.append(Paragraph("Rule Evaluation", section_style))
        if rule_results:
            rule_rows = [["Metric", "Value", "Status", "Warning", "Critical"]]
            row_colors = []
            for key, result in rule_results.items():
                rule_rows.append(
                    [
                        _format_label(key),
                        _format_value(result.get("value")),
                        str(result.get("status", "")).title(),
                        _format_value(result.get("warning_threshold")),
                        _format_value(result.get("critical_threshold")),
                    ]
                )
                row_colors.append(_status_color(result.get("status", "")))

            rule_table = Table(
                rule_rows,
                colWidths=[1.8 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch],
            )
            style_commands = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#37474F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
            for i, color in enumerate(row_colors, start=1):
                style_commands.append(("TEXTCOLOR", (2, i), (2, i), color))
                style_commands.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
            rule_table.setStyle(TableStyle(style_commands))
            story.append(rule_table)
        else:
            story.append(Paragraph("No rule evaluation data available.", body_style))

    # --- Insights section -------------------------------------------------
    story.append(Paragraph("Business Insights", section_style))
    if insights:
        story.append(
            ListFlowable(
                [ListItem(Paragraph(text, body_style)) for text in insights],
                bulletType="bullet",
            )
        )
    else:
        story.append(Paragraph("No notable insights — all metrics within normal range.", body_style))

    # --- Recommendations section -------------------------------------------
    story.append(Paragraph("Recommendations", section_style))
    if recommendations:
        story.append(
            ListFlowable(
                [ListItem(Paragraph(text, body_style)) for text in recommendations],
                bulletType="bullet",
            )
        )
    else:
        story.append(Paragraph("No recommendations — all metrics within normal range.", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ---------------------------------------------------------------------------
# CSV export functions
# ---------------------------------------------------------------------------

def generate_kpi_csv(kpis: dict[str, Any]) -> bytes:
    """
    Exports the KPI dict as a two-column CSV (Metric, Value).

    Args:
        kpis: output of analytics.kpi_engine.calculate_kpis()

    Returns:
        CSV file content as bytes.
    """
    df = pd.DataFrame(
        [{"Metric": _format_label(k), "Value": v} for k, v in kpis.items()]
    )
    return df.to_csv(index=False).encode("utf-8")


def generate_dataset_csv(dataframe: pd.DataFrame) -> bytes:
    """
    Exports a dataset (e.g. st.session_state.mapped_dataset) as CSV.
    Report-page-only per architecture decision — the mapped dataset is
    not persisted to Supabase, so this is unavailable on History.

    Args:
        dataframe: the cleaned/mapped dataset

    Returns:
        CSV file content as bytes.
    """
    return dataframe.to_csv(index=False).encode("utf-8")