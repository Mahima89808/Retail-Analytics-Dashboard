"""
Insight Generator

Responsibilities:

- Convert rule evaluation results into human-readable business insights.
- Aggregate grouped-rule violations into scalable business findings.
- Prioritize the most severe grouped violation when describing the
  worst-performing group.
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


def _get_worst_violation(
    violations: list[dict],
    direction: str,
) -> dict:
    """
    Return the most severe violation according to rule direction.

    For lower-is-worse metrics, the lowest value is worst.

    For higher-is-worse metrics, the highest value is worst.
    """

    if direction == "lower":
        return min(
            violations,
            key=lambda violation: violation["value"],
        )

    if direction == "higher":
        return max(
            violations,
            key=lambda violation: violation["value"],
        )

    raise ValueError(
        f"Unsupported rule direction: {direction!r}. "
        "Expected 'lower' or 'higher'."
    )


def _format_grouped_insight(
    metric: str,
    result: dict,
) -> List[str]:
    """
    Convert grouped rule violations into
    human-readable business insights.
    """

    insights = []

    label = DISPLAY_NAMES.get(
        metric,
        metric.replace("_", " ").title(),
    )

    violations = result.get(
        "violations",
        [],
    )

    if not violations:
        return insights

    critical_count = sum(
        1
        for violation in violations
        if violation["status"] == "critical"
    )

    warning_count = sum(
        1
        for violation in violations
        if violation["status"] == "warning"
    )

    total_count = len(violations)

    warning_threshold = result.get(
        "warning_threshold"
    )

    critical_threshold = result.get(
        "critical_threshold"
    )

    if metric.endswith("_profit_margin"):

        worst = min(
            violations,
            key=lambda violation: violation["value"],
        )

        worst_group = worst["group"]
        worst_value = worst["value"]

        if worst_value < 0:

            insights.append(
                f"{total_count} {label.lower()} group(s) "
                f"require attention "
                f"({critical_count} critical, "
                f"{warning_count} warning). "
                f"{worst_group} is currently unprofitable "
                f"with a profit margin of {worst_value:.2f}%. "
                f"This indicates that the group is generating "
                f"losses relative to its sales."
            )

        else:

            insights.append(
                f"{total_count} {label.lower()} group(s) "
                f"are below the configured profitability "
                f"thresholds "
                f"({critical_count} critical, "
                f"{warning_count} warning). "
                f"The worst-performing group is "
                f"{worst_group} at {worst_value:.2f}%."
            )

    elif metric.endswith("_sales_concentration"):

        highest = max(
            violations,
            key=lambda violation: violation["value"],
        )

        highest_group = highest["group"]
        highest_value = highest["value"]

        insights.append(
            f"{total_count} {label.lower()} group(s) "
            f"exceed the configured concentration "
            f"thresholds "
            f"({critical_count} critical, "
            f"{warning_count} warning). "
            f"{highest_group} represents "
            f"{highest_value:.2f}% of total sales, "
            f"indicating relatively high dependence "
            f"on this group."
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

    Notes
    -----
    Scalar rules generate one insight when they are warning or critical.

    Grouped rules generate one aggregated insight per violated rule,
    rather than one insight for every violating group.

    "normal" and "not_applicable" rules do not generate insights.
    """

    insights = []

    for metric, result in rule_results.items():

        status = result["status"]

        # A normal rule has no concerning condition.
        #
        # A not_applicable rule does not have enough meaningful data
        # to interpret the rule. It is not a business violation.
        if status in ("normal", "not_applicable"):
            continue

        if result.get("rule_type") == "grouped":

                    insight = _format_grouped_insight(
                        metric=metric,
                        result=result,
                    )

                    if insight:
                        insights.extend(insight)

                    continue

        label = DISPLAY_NAMES.get(
            metric,
            metric.replace("_", " ").title(),
        )

        value = result["value"]
        warning_threshold = result["warning_threshold"]
        critical_threshold = result["critical_threshold"]

        if metric == "profit_margin":

            if value < 0:

                insights.append(
                    f"Overall profitability is negative: "
                    f"profit margin is {value:.2f}%. "
                    f"The business is generating a loss "
                    f"relative to total sales."
                )

            else:

                insights.append(
                    f"Profit margin is {value:.2f}%, "
                    f"below the configured {status} threshold."
                )

        else:

            insights.append(
                f"{label} accounts for {value:.2f}% of sales, "
                f"exceeding the configured {status} threshold."
            )

    return insights