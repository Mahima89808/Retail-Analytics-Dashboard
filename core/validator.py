"""
Dataset Validator

Capability-based validation model (adopted per design review — replaces
the previous binary Sales/Profit-required model).

Responsibilities:
- Verify only the absolute minimum required columns are present (Sales, order_date).
- Never mark a dataset invalid due to missing optional/recommended columns.
- Report which analysis capabilities are available or unavailable based on
  which optional columns were detected, so the rest of the app can render
  accordingly.

This module assumes column names have already been mapped to the
application's canonical schema.
"""

from typing import Iterable

# ==========================================================
# Required Columns
# ==========================================================
# Absolute minimum for the dataset to be usable at all.
# Per design review: Profit is no longer required — it becomes an
# optional capability (Profitability Analysis) instead.

REQUIRED_COLUMNS = {
    "Sales",
    "order_date",
}

# ==========================================================
# Capability Definitions
# ==========================================================
# Each capability lists the canonical column(s) needed to enable it.
# "all_of": every column listed must be present.
# "any_of": at least one column listed must be present.
# Sales Analysis / Time Trends depend only on REQUIRED_COLUMNS, so they
# are always available for any dataset that passes validate_dataset().

CAPABILITIES = {
    "Sales Analysis": {"all_of": ["Sales"]},
    "Time Trends": {"all_of": ["order_date"]},
    "Profitability Analysis": {"all_of": ["Profit"]},
    "Category Analysis": {"all_of": ["category"]},
    "Product Analysis": {"any_of": ["product_id", "product_name"]},
    "Customer Analysis": {"any_of": ["customer_id", "customer_name"]},
    "Geographic Analysis": {"any_of": ["region", "state", "city", "country"]},
    "Cost Optimization Analysis": {"all_of": ["Profit", "Discount", "cost"]},
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


def get_capability_report(columns: Iterable[str]) -> dict:
    """
    Build a capability-based report: which analysis modules are available
    or unavailable given the columns actually present in this dataset.

    A dataset can be valid (required columns present) while still having
    many unavailable capabilities — this is expected and should be
    communicated to the user, not treated as an error.

    Parameters
    ----------
    columns : Iterable[str]
        Canonical column names.

    Returns
    -------
    dict
        {
            "available": ["Sales Analysis", "Time Trends", ...],
            "unavailable": [
                {"capability": "Profitability Analysis", "missing": ["Profit"]},
                ...
            ],
        }
    """

    column_set = set(columns)

    available = []
    unavailable = []

    for capability_name, requirement in CAPABILITIES.items():
        if "all_of" in requirement:
            required = requirement["all_of"]
            missing = [col for col in required if col not in column_set]
            if not missing:
                available.append(capability_name)
            else:
                unavailable.append({"capability": capability_name, "missing": missing})

        elif "any_of" in requirement:
            options = requirement["any_of"]
            if any(col in column_set for col in options):
                available.append(capability_name)
            else:
                unavailable.append({"capability": capability_name, "missing": options})

    return {
        "available": available,
        "unavailable": unavailable,
    }