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
    "warehouse_ratio": "Warehouse costs",
    "profit_margin": "Profit margin",
}


def generate_insights(rule_results: dict) -> List[str]:
    """
    Generate business insights from evaluated rules.

    Parameters
    ----------
    rule_results : dict

    Returns
    -------
    list[str]
    """

    insights = []

    for metric, result in rule_results.items():

        status = result["status"]

        if status == "normal":
            continue

        label = DISPLAY_NAMES.get(metric, metric.replace("_", " ").title())

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