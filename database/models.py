"""
Database models.

These models define the structure of data exchanged
between the application and the repository layer.

They are NOT ORM models.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class AnalysisRecord:
    """
    Represents one saved retail analysis report.
    """

    report_name: str
    uploaded_file: str

    total_rows: int
    total_columns: int

    mapped_columns: dict[str, str]
    validation_summary: dict[str, Any]

    kpis: dict[str, Any]
    insights: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]




@dataclass
class SavedAnalysisRecord:
    """
    Represents one saved analysis returned from Supabase.
    """

    id: str
    created_at: str

    report_name: str
    uploaded_file: str

    total_rows: int
    total_columns: int

    mapped_columns: dict[str, str]
    validation_summary: dict[str, Any]

    kpis: dict[str, Any]
    insights: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]