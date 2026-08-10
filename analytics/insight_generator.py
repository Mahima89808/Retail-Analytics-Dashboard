"""
Insight Generator

Responsibilities:

- Convert rule evaluation results into human-readable business insights.
"""

# Standard library imports

from typing import List


DISPLAY_NAMES = {
    "employee_salary_ratio": "Employee salary expenses",
    "rent_ratio": "Rent expenses",
    "electricity_ratio": "Electricity expenses",
    "logistics_ratio": "Logistics expenses",
    "marketing_ratio": "Marketing expenses",
    "supplier_ratio": "Supplier costs",
    "manufacturing_ratio": "Manufacturing costs",
    "warehouse_ratio": "Warehouse expenses",
    "profit_margin": "Profit margin",
    "category_profit_margin": "Category profit margin",
    "category_sales_concentration": "Category sales concentration",
    "subcategory_profit_margin": "Subcategory profit margin",
    "subcategory_sales_concentration": "Subcategory sales concentration",
    "region_profit_margin": "Region profit margin",
    "region_sales_concentration": "Region sales concentration",
    "state_profit_margin": "State profit margin",
    "state_sales_concentration": "State sales concentration",
    "city_profit_margin": "City profit margin",
    "city_sales_concentration": "City sales concentration",
    "country_profit_margin": "Country profit margin",
    "country_sales_concentration": "Country sales concentration",
}


def _format_grouped_insight(
    metric: str,
    result: dict,
) -> List[str]:
    """
    Convert grouped rule violations into human-readable insights.
    """

    insights = []

    label = DISPLAY_NAMES.get(
        metric,
        metric.replace("_", " ").title(),
    )

    for violation in result["violations"]:

        group = violation["group"]
        value = violation["value"]
        status = violation["status"]

        if metric.endswith("_profit_margin"):

            insights.append(
                f"{label} for {group} is {value:.2f}%, "
                f"below the {status} threshold."
            )

        elif metric.endswith("_sales_concentration"):

            insights.append(
                f"{label} for {group} is {value:.2f}% of total sales, "
                f"exceeding the {status} threshold."
            )

    return insights


def generate_insights(rule_results: dict) -> List[str]:
    """
    Generate business insights from evaluated rules.

    Parameters
    ----------
    rule_results : dict
        Structured rule evaluation results from rule_engine.py.

    Returns
    -------
    list[str]
        Human-readable business insights.
    """

    insights = []

    for metric, result in rule_results.items():

        status = result["status"]

        if status == "normal":
            continue

        if result.get("rule_type") == "grouped":
            insights.extend(
                _format_grouped_insight(
                    metric=metric,
                    result=result,
                )
            )
            continue

        label = DISPLAY_NAMES.get(
            metric,
            metric.replace("_", " ").title(),
        )

        value = result["value"]

        if metric == "profit_margin":
            insights.append(
                f"{label} is {value:.2f}%, "
                f"below the {status} threshold."
            )

        else:
            insights.append(
                f"{label} account for {value:.2f}% of sales, "
                f"exceeding the {status} threshold."
            )

    return insights

