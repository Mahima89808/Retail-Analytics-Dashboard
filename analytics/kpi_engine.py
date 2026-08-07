"""
KPI Engine

Responsibilities:
- Calculate business KPIs from a validated dataset.
- Return KPIs as a dictionary.
- Do not generate insights or recommendations.
"""

# Third-party imports
import pandas as pd


def calculate_kpis(dataframe: pd.DataFrame) -> dict:
    """
    Calculate KPIs from the dataset.

    Parameters
    ----------
    dataframe : pandas.DataFrame

    Returns
    -------
    dict
        Dictionary containing calculated KPIs.
    """

    kpis = {}

    # -------------------------
    # Core KPIs
    # -------------------------

    total_sales = dataframe["Sales"].sum()
    total_profit = dataframe["Profit"].sum()

    kpis["total_sales"] = float(total_sales)
    kpis["total_profit"] = float(total_profit)

    kpis["total_records"] = len(dataframe)

    if "Order ID" in dataframe.columns:
        kpis["total_orders"] = dataframe["Order ID"].nunique()

    if total_sales != 0:
        kpis["profit_margin"] = (total_profit / total_sales) * 100
    else:
        kpis["profit_margin"] = 0.0

    # -------------------------
    # Optional KPIs
    # -------------------------

    optional_columns = {
        "Quantity": "total_quantity",
        "Discount": "average_discount",
        "Employee Salaries": "total_employee_salaries",
        "Rent": "total_rent",
        "Electricity": "total_electricity",
        "Logistics Cost": "total_logistics_cost",
        "Marketing Cost": "total_marketing_cost",
        "Supplier Cost": "total_supplier_cost",
        "Manufacturing Cost": "total_manufacturing_cost",
        "Warehouse Cost": "total_warehouse_cost",
    }

    for column, kpi_name in optional_columns.items():

        if column not in dataframe.columns:
            continue

        if column == "Discount":
            kpis[kpi_name] = float(dataframe[column].mean())
        else:
            kpis[kpi_name] = float(dataframe[column].sum())

    # -------------------------
    # Cost Ratios
    # -------------------------

    if total_sales != 0:

        ratio_columns = {
            "Employee Salaries": "employee_salary_ratio",
            "Rent": "rent_ratio",
            "Electricity": "electricity_ratio",
            "Logistics Cost": "logistics_ratio",
            "Marketing Cost": "marketing_ratio",
            "Supplier Cost": "supplier_ratio",
            "Manufacturing Cost": "manufacturing_ratio",
            "Warehouse Cost": "warehouse_ratio",
        }

        for column, ratio_name in ratio_columns.items():

            if column in dataframe.columns:
                kpis[ratio_name] = (
                    dataframe[column].sum() / total_sales
                ) * 100

    return kpis