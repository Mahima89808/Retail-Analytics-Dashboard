"""
KPI Engine

Responsibilities:

- Calculate business KPIs from a validated dataset.
- Calculate capability-driven KPIs only when the required columns exist.
- Return KPIs as a dictionary.
- Do not generate insights or recommendations.

Notes:
- Sales and order_date are the required dataset fields, but order_date is
  not directly used for KPI calculation in this module.
- Profit is optional. Profit-related KPIs are omitted when Profit is absent.
- Capability KPIs are calculated only when their underlying columns exist.
- Product analysis uses product_name when available, otherwise product_id.
- Customer analysis uses customer_id as the stable customer identifier.
- Geographic analysis is calculated independently for every geographic
  column present in the dataset.
- Top-N selection and presentation are intentionally outside this module.
"""

# Third-party imports

import pandas as pd


def _grouped_sum(
    dataframe: pd.DataFrame,
    group_column: str,
    value_column: str,
) -> dict:
    """
    Calculate a sum grouped by a dataset column.

    Parameters
    ----------
    dataframe : pandas.DataFrame
    group_column : str
        Column used to group the data.
    value_column : str
        Numeric column to aggregate.

    Returns
    -------
    dict
        Mapping of group value to aggregated value.
    """

    grouped = dataframe.groupby(
        group_column,
        dropna=True,
    )[value_column].sum()

    return {
        str(group): float(value)
        for group, value in grouped.items()
    }


def _add_grouped_capability_kpis(
    kpis: dict,
    dataframe: pd.DataFrame,
    group_column: str,
    sales_kpi_name: str,
    profit_kpi_name: str,
) -> None:
    """
    Add grouped Sales and optional Profit KPIs for a capability.

    Profit KPIs are added only when the Profit column exists.
    """

    if group_column not in dataframe.columns:
        return

    kpis[sales_kpi_name] = _grouped_sum(
        dataframe,
        group_column,
        "Sales",
    )

    if "Profit" in dataframe.columns:
        kpis[profit_kpi_name] = _grouped_sum(
            dataframe,
            group_column,
            "Profit",
        )


def calculate_kpis(dataframe: pd.DataFrame) -> dict:
    """
    Calculate KPIs from the dataset.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        Validated and cleaned dataset.

    Returns
    -------
    dict
        Dictionary containing calculated KPIs. Optional and
        capability-driven KPIs are included only when the required
        source columns are present.
    """

    kpis = {}

    # -------------------------
    # Core KPIs
    # -------------------------

    total_sales = dataframe["Sales"].sum()

    kpis["total_sales"] = float(total_sales)
    kpis["total_records"] = len(dataframe)

    # -------------------------
    # Profitability KPIs
    # -------------------------

    if "Profit" in dataframe.columns:
        total_profit = dataframe["Profit"].sum()

        kpis["total_profit"] = float(total_profit)

        if total_sales != 0:
            kpis["profit_margin"] = (
                float(total_profit) / float(total_sales)
            ) * 100
        else:
            kpis["profit_margin"] = 0.0

    # -------------------------
    # Order KPIs
    # -------------------------

    if "order_id" in dataframe.columns:
        kpis["total_orders"] = int(
            dataframe["order_id"].nunique()
        )

    # -------------------------
    # Existing Optional KPIs
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
            kpis[kpi_name] = float(
                dataframe[column].mean()
            )
        else:
            kpis[kpi_name] = float(
                dataframe[column].sum()
            )

    # -------------------------
    # Existing Cost Ratios
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

            if column not in dataframe.columns:
                continue

            kpis[ratio_name] = (
                float(dataframe[column].sum())
                / float(total_sales)
            ) * 100

    # -------------------------
    # Category Analysis
    # -------------------------

    _add_grouped_capability_kpis(
        kpis=kpis,
        dataframe=dataframe,
        group_column="category",
        sales_kpi_name="category_sales",
        profit_kpi_name="category_profit",
    )

    # -------------------------
    # Subcategory Analysis
    # -------------------------

    _add_grouped_capability_kpis(
        kpis=kpis,
        dataframe=dataframe,
        group_column="subcategory",
        sales_kpi_name="subcategory_sales",
        profit_kpi_name="subcategory_profit",
    )

    # -------------------------
    # Product Analysis
    # -------------------------

    product_column = None

    if "product_name" in dataframe.columns:
        product_column = "product_name"
    elif "product_id" in dataframe.columns:
        product_column = "product_id"

    if product_column is not None:

        kpis["product_sales"] = _grouped_sum(
            dataframe,
            product_column,
            "Sales",
        )

        if "Profit" in dataframe.columns:
            kpis["product_profit"] = _grouped_sum(
                dataframe,
                product_column,
                "Profit",
            )

    # -------------------------
    # Customer Analysis
    # -------------------------

    if "customer_id" in dataframe.columns:

        kpis["unique_customers"] = int(
            dataframe["customer_id"].nunique()
        )

        kpis["customer_sales"] = _grouped_sum(
            dataframe,
            "customer_id",
            "Sales",
        )

        if "Profit" in dataframe.columns:
            kpis["customer_profit"] = _grouped_sum(
                dataframe,
                "customer_id",
                "Profit",
            )

    # -------------------------
    # Geographic Analysis
    # -------------------------

    geographic_columns = {
        "region": (
            "region_sales",
            "region_profit",
        ),
        "state": (
            "state_sales",
            "state_profit",
        ),
        "city": (
            "city_sales",
            "city_profit",
        ),
        "country": (
            "country_sales",
            "country_profit",
        ),
    }

    for column, (
        sales_kpi_name,
        profit_kpi_name,
    ) in geographic_columns.items():

        _add_grouped_capability_kpis(
            kpis=kpis,
            dataframe=dataframe,
            group_column=column,
            sales_kpi_name=sales_kpi_name,
            profit_kpi_name=profit_kpi_name,
        )

    return kpis