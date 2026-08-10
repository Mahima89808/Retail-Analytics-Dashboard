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

    "category_profit_margin":
        "Review pricing, discounts, product mix, and category-level costs for underperforming categories to improve category profitability.",

    "category_sales_concentration":
        "Reduce dependence on highly concentrated categories by broadening the product mix and developing opportunities in lower-concentration categories.",

    "subcategory_profit_margin":
        "Review pricing, discounts, product mix, and subcategory-level costs for underperforming subcategories to improve profitability.",

    "subcategory_sales_concentration":
        "Reduce dependence on highly concentrated subcategories by diversifying the product mix and strengthening lower-concentration opportunities.",

    "region_profit_margin":
        "Review pricing, operating costs, and sales performance in underperforming regions to improve regional profitability.",

    "region_sales_concentration":
        "Reduce dependence on highly concentrated regions by diversifying sales across geographic markets.",

    "state_profit_margin":
        "Review pricing, operating costs, and sales performance in underperforming states to improve state-level profitability.",

    "state_sales_concentration":
        "Reduce dependence on highly concentrated states by diversifying sales across geographic markets.",

    "city_profit_margin":
        "Review pricing, operating costs, and sales performance in underperforming cities to improve city-level profitability.",

    "city_sales_concentration":
        "Reduce dependence on highly concentrated cities by diversifying sales across geographic markets.",

    "country_profit_margin":
        "Review pricing, operating costs, and sales performance in underperforming countries to improve country-level profitability.",

    "country_sales_concentration":
        "Reduce dependence on highly concentrated countries by diversifying sales across geographic markets.",
}


def generate_recommendations(rule_results: dict) -> List[str]:
    """
    Generate business recommendations from evaluated rules.

    Parameters
    ----------
    rule_results : dict
        Structured rule evaluation results from rule_engine.py.

    Returns
    -------
    list[str]
        Actionable business recommendations.
    """

    recommendations = []

    for metric, result in rule_results.items():

        if result["status"] == "normal":
            continue

        recommendation = RECOMMENDATIONS.get(metric)

        if recommendation:
            recommendations.append(recommendation)

    return recommendations

