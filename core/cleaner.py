"""
Data Quality Checker

Responsibilities:
- Detect missing values per column.
- Detect duplicate rows.
- Detect unexpected non-numeric values in known numeric columns.

This module only reports issues — it does not modify the dataset.
Assumes columns have already been mapped to canonical names.
"""

import pandas as pd

# Canonical columns expected to contain numeric data.
NUMERIC_COLUMNS = {
    "Sales",
    "Profit",
    "Quantity",
    "Discount",
    "Employee Salaries",
    "Rent",
    "Electricity",
    "Logistics Cost",
    "Marketing Cost",
    "Supplier Cost",
    "Manufacturing Cost",
    "Warehouse Cost",
}


def analyze_data_quality(dataframe: pd.DataFrame) -> dict:
    """
    Analyze a mapped dataset for common data-quality issues.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        Dataset with canonical column names.

    Returns
    -------
    dict
        {
            "missing_values": {column: count, ...},
            "duplicate_rows": int,
            "type_issues": {column: count, ...},
            "has_issues": bool,
        }
    """

    missing_values = {}

    for column in dataframe.columns:
        missing_count = int(dataframe[column].isna().sum())

        if missing_count > 0:
            missing_values[column] = missing_count

    duplicate_rows = int(dataframe.duplicated().sum())

    type_issues = {}

    for column in dataframe.columns:

        if column not in NUMERIC_COLUMNS:
            continue

        numeric_values = pd.to_numeric(dataframe[column], errors="coerce")
        invalid_mask = numeric_values.isna() & dataframe[column].notna()
        invalid_count = int(invalid_mask.sum())

        if invalid_count > 0:
            type_issues[column] = invalid_count

    has_issues = bool(missing_values or duplicate_rows or type_issues)

    return {
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "type_issues": type_issues,
        "has_issues": has_issues,
    }