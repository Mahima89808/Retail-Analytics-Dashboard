"""
Dataset Validator

Responsibilities:
- Verify that all required canonical columns are present.
- Raise descriptive exceptions when validation fails.
- Provide a structured validation summary (non-raising) for reporting/storage.

This module assumes that column names have already been mapped
to the application's canonical schema.
"""

from typing import Iterable

REQUIRED_COLUMNS = {
    "Sales",
    "Profit",
}


def validate_dataset(columns: Iterable[str]) -> None:
    """
    Validate that all required columns exist.

    Parameters
    ----------
    columns : Iterable[str]
        Canonical column names.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """

    column_set = set(columns)

    missing_columns = REQUIRED_COLUMNS - column_set

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Missing required column(s): {missing}"
        )


def get_validation_summary(columns: Iterable[str]) -> dict:
    """
    Build a structured validation summary without raising.

    Parameters
    ----------
    columns : Iterable[str]
        Canonical column names.

    Returns
    -------
    dict
        {
            "required_columns": [...],
            "missing_columns": [...],
            "is_valid": bool,
        }
    """

    column_set = set(columns)

    missing_columns = REQUIRED_COLUMNS - column_set

    return {
        "required_columns": sorted(REQUIRED_COLUMNS),
        "missing_columns": sorted(missing_columns),
        "is_valid": not missing_columns,
    }