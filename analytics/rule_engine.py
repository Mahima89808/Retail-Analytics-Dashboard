"""
Rule Engine

Responsibilities:

- Load business rules from config/rules.yaml.
- Compare scalar KPI values against configured thresholds.
- Evaluate grouped KPI rules using configured source KPIs.
- Return structured rule evaluation results.
"""

# Standard library imports

from config.settings import RULES_FILE

# Third-party imports

import yaml


def _load_rules() -> dict:
    """Load business rules from rules.yaml."""

    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _evaluate_status(
    value: float,
    warning: float,
    critical: float,
    direction: str,
) -> str:
    """
    Determine rule status from a value and configured thresholds.

    Parameters
    ----------
    value : float
        Calculated KPI or derived metric value.
    warning : float
        Warning threshold.
    critical : float
        Critical threshold.
    direction : str
        "lower" when lower values are worse.
        "higher" when higher values are worse.

    Returns
    -------
    str
        "normal", "warning", or "critical".
    """

    if direction == "lower":

        if value <= critical:
            return "critical"

        if value <= warning:
            return "warning"

        return "normal"

    if direction == "higher":

        if value >= critical:
            return "critical"

        if value >= warning:
            return "warning"

        return "normal"

    raise ValueError(
        f"Unsupported rule direction: {direction!r}. "
        "Expected 'lower' or 'higher'."
    )


def _evaluate_scalar_rule(
    kpi_name: str,
    value: float,
    thresholds: dict,
) -> dict:
    """
    Evaluate a scalar KPI rule.

    Existing scalar rules default to "higher is worse" for backward
    compatibility. Rules can explicitly provide a direction in YAML.
    """

    warning = thresholds["warning"]
    critical = thresholds["critical"]

    direction = thresholds.get("direction")

    if direction is None:
        direction = "lower" if kpi_name == "profit_margin" else "higher"

    status = _evaluate_status(
        value=value,
        warning=warning,
        critical=critical,
        direction=direction,
    )

    return {
        "value": round(value, 2),
        "status": status,
        "warning_threshold": warning,
        "critical_threshold": critical,
    }


def _evaluate_grouped_rule(
    thresholds: dict,
    kpis: dict,
) -> dict | None:
    """
    Evaluate a grouped rule against dictionary-valued KPI data.

    A grouped rule derives one value per group from configured source KPIs.

    For example:

    category_profit_margin
        category_profit / category_sales

    category_sales_concentration
        category_sales / total_sales

    Only groups that violate the configured rule are returned.

    Concentration rules are evaluated only when at least two groups
    are present. A single-group dataset represents complete coverage
    of that dimension rather than meaningful concentration.

    Returns
    -------
    dict | None
        Structured grouped-rule result, or None when the required KPI
        sources are unavailable or the rule cannot be meaningfully
        evaluated.
    """

    numerator_name = thresholds["numerator"]
    denominator_name = thresholds["denominator"]

    if numerator_name not in kpis or denominator_name not in kpis:
        return None

    numerator = kpis[numerator_name]
    denominator = kpis[denominator_name]

    if not isinstance(numerator, dict):
        return None

    direction = thresholds["direction"]
    warning = thresholds["warning"]
    critical = thresholds["critical"]

    is_concentration_rule = (
        numerator_name.endswith("_sales")
        and denominator_name == "total_sales"
    )

    if is_concentration_rule and len(numerator) < 2:
        return None

    violations = []

    if isinstance(denominator, dict):

        groups = [
            group
            for group in numerator
            if group in denominator
        ]

        for group in groups:

            denominator_value = denominator[group]

            if denominator_value == 0:
                continue

            value = (numerator[group] / denominator_value) * 100

            status = _evaluate_status(
                value=value,
                warning=warning,
                critical=critical,
                direction=direction,
            )

            if status != "normal":
                violations.append(
                    {
                        "group": group,
                        "value": round(value, 2),
                        "status": status,
                    }
                )

    else:

        if denominator == 0:
            return None

        for group, numerator_value in numerator.items():

            value = (numerator_value / denominator) * 100

            status = _evaluate_status(
                value=value,
                warning=warning,
                critical=critical,
                direction=direction,
            )

            if status != "normal":
                violations.append(
                    {
                        "group": group,
                        "value": round(value, 2),
                        "status": status,
                    }
                )

    if not violations:
        status = "normal"

    elif any(
        violation["status"] == "critical"
        for violation in violations
    ):
        status = "critical"

    else:
        status = "warning"

    return {
        "rule_type": "grouped",
        "status": status,
        "warning_threshold": warning,
        "critical_threshold": critical,
        "violations": violations,
    }


def evaluate_rules(kpis: dict) -> dict:
    """
    Evaluate KPIs against configured rules.

    Parameters
    ----------
    kpis : dict
        KPI dictionary from kpi_engine.py.

    Returns
    -------
    dict
        Structured rule evaluation results.
    """

    rules = _load_rules()

    results = {}

    for kpi_name, thresholds in rules.items():

        rule_type = thresholds.get("type")

        if rule_type == "grouped_ratio":

            grouped_result = _evaluate_grouped_rule(
                thresholds=thresholds,
                kpis=kpis,
            )

            if grouped_result is not None:
                results[kpi_name] = grouped_result

            continue

        if kpi_name not in kpis:
            continue

        value = kpis[kpi_name]

        if not isinstance(value, (int, float)):
            continue

        results[kpi_name] = _evaluate_scalar_rule(
            kpi_name=kpi_name,
            value=value,
            thresholds=thresholds,
        )

    return results

