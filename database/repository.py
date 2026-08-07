"""
Repository layer.

Responsibilities:
- Insert analysis records
- Read analysis records
- Update analysis records
- Delete analysis records

This is the ONLY module that communicates directly with Supabase.
"""

from typing import Any

from config.settings import ANALYSIS_TABLE
from database.db import supabase
from database.models import AnalysisRecord, SavedAnalysisRecord


def _to_saved_record(data: dict[str, Any]) -> SavedAnalysisRecord:
    """
    Convert a Supabase response dictionary into a SavedAnalysisRecord.
    """

    return SavedAnalysisRecord(
        id=data["id"],
        created_at=data["created_at"],
        report_name=data["report_name"],
        uploaded_file=data["uploaded_file"],
        total_rows=data["total_rows"],
        total_columns=data["total_columns"],
        mapped_columns=data["mapped_columns"],
        validation_summary=data["validation_summary"],
        kpis=data["kpis"],
        insights=data["insights"],
        recommendations=data["recommendations"],
    )


def save_analysis(record: AnalysisRecord) -> SavedAnalysisRecord:
    """
    Save an analysis record to Supabase.
    """

    payload = {
        "report_name": record.report_name,
        "uploaded_file": record.uploaded_file,
        "total_rows": record.total_rows,
        "total_columns": record.total_columns,
        "mapped_columns": record.mapped_columns,
        "validation_summary": record.validation_summary,
        "kpis": record.kpis,
        "insights": record.insights,
        "recommendations": record.recommendations,
    }

    response = (
        supabase
        .table(ANALYSIS_TABLE)
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to save analysis.")

    return _to_saved_record(response.data[0])


def get_all_analyses() -> list[SavedAnalysisRecord]:
    """
    Return every saved analysis ordered by newest first.
    """

    response = (
        supabase
        .table(ANALYSIS_TABLE)
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return [_to_saved_record(item) for item in response.data]


def get_analysis_by_id(record_id: str) -> SavedAnalysisRecord | None:
    """
    Return one analysis by its ID.
    """

    response = (
        supabase
        .table(ANALYSIS_TABLE)
        .select("*")
        .eq("id", record_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return _to_saved_record(response.data[0])


def rename_analysis(record_id: str, new_name: str) -> bool:
    """
    Rename a saved analysis.
    """

    response = (
        supabase
        .table(ANALYSIS_TABLE)
        .update({"report_name": new_name})
        .eq("id", record_id)
        .execute()
    )

    return len(response.data) > 0


def delete_analysis(record_id: str) -> bool:
    """
    Delete a saved analysis.
    """

    response = (
        supabase
        .table(ANALYSIS_TABLE)
        .delete()
        .eq("id", record_id)
        .execute()
    )

    return len(response.data) > 0