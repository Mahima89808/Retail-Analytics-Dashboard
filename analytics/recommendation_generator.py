"""
Recommendation Generator

Responsibilities:
- Convert evaluated business rules into actionable recommendations.
"""

# Standard library imports
from typing import List


RECOMMENDATIONS = {
    "employee_salary_ratio":
        "Review staffing levels, overtime, and workforce allocation to optimize salary expenses.",

    "rent_ratio":
        "Evaluate lease agreements or optimize store and office space utilization to reduce rental costs.",

    "electricity_ratio":
        "Monitor energy consumption, upgrade to energy-efficient equipment, and reduce unnecessary power usage.",

    "logistics_ratio":
        "Optimize delivery routes, consolidate shipments, and negotiate with logistics providers.",

    "marketing_ratio":
        "Review campaign performance and reallocate budget toward higher-performing marketing channels.",

    "supplier_ratio":
        "Negotiate supplier contracts or identify alternative vendors to reduce procurement costs.",

    "manufacturing_ratio":
        "Improve production efficiency, reduce waste, and optimize manufacturing processes.",

    "warehouse_ratio":
        "Optimize inventory levels and warehouse operations to reduce storage costs.",

    "profit_margin":
        "Review pricing strategy, discounts, operational costs, and product mix to improve profitability.",
}


def generate_recommendations(rule_results: dict) -> List[str]:
    """
    Generate business recommendations from rule evaluation results.

    Parameters
    ----------
    rule_results : dict

    Returns
    -------
    list[str]
    """

    recommendations = []

    for metric, result in rule_results.items():

        if result["status"] == "normal":
            continue

        recommendation = RECOMMENDATIONS.get(metric)

        if recommendation:
            recommendations.append(recommendation)

    return recommendations