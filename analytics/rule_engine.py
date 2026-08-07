"""
Rule Engine

Responsibilities:
- Load business rules from config/rules.yaml.
- Compare KPI values against configured thresholds.
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

        if kpi_name not in kpis:
            continue

        value = kpis[kpi_name]

        warning = thresholds["warning_threshold"]
        critical = thresholds["critical_threshold"]

        # Profit margin: lower is worse
        if kpi_name == "profit_margin":

            if value <= critical:
                status = "critical"

            elif value <= warning:
                status = "warning"

            else:
                status = "normal"

        # Cost ratios: higher is worse
        else:

            if value >= critical:
                status = "critical"

            elif value >= warning:
                status = "warning"

            else:
                status = "normal"

        results[kpi_name] = {
            "value": round(value, 2),
            "status": status,
            "warning_threshold": warning,
            "critical_threshold": critical,
        }

    return results