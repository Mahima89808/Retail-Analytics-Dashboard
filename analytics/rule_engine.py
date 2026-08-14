"""
Rule Engine

Responsibilities:

- Load business rules from config/rules.yaml.
- Compare scalar KPI values against configured thresholds.
- Evaluate grouped KPI rules using configured source KPIs.
- Return structured rule evaluation results.
- Accept optional per-session threshold overrides supplied by the UI
  layer, without ever modifying config/rules.yaml.
"""

# Standard library imports

from config.settings import RULES_FILE

# Third-party imports

import yaml


# Fields that describe what a rule IS, not a business threshold choice.
# These can never be changed by an override.
_STRUCTURAL_FIELDS = {
    "type",
    "numerator",
    "denominator",
    "direction",
    "min_groups",
}

# Fields an override is permitted to change.
_OVERRIDABLE_FIELDS = {
    "warning",
    "critical",
}


def _load_rules() -> dict:
    """Load business rules from rules.yaml."""

    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_applicable_rules(kpis: dict) -> dict:
    """
    Return configured rules that are applicable to the supplied KPIs.

    Applicability is determined by whether the KPIs required by the
    rule definition are available.

    This function does not evaluate rules and does not apply threshold
    overrides.

    Parameters
    ----------
    kpis : dict
        KPI dictionary produced by kpi_engine.py.

    Returns
    -------
    dict
        Mapping of applicable rule names to their rule definitions.

    Notes
    -----
    For scalar rules, the rule is applicable when its rule name exists
    in the KPI dictionary.

    For grouped_ratio rules, the rule is applicable when both its
    numerator and denominator KPI sources exist.

    The rule's min_groups value does not determine configurability.
    A rule may be configurable while its evaluation result is
    "not_applicable" because the dataset contains too few groups.
    """

    rules = _load_rules()
    applicable_rules = {}

    for rule_name, thresholds in rules.items():

        rule_type = thresholds.get("type")

        if rule_type == "grouped_ratio":

            numerator_name = thresholds.get("numerator")
            denominator_name = thresholds.get("denominator")

            if (
                numerator_name in kpis
                and denominator_name in kpis
            ):
                applicable_rules[rule_name] = thresholds

            continue

        if rule_name in kpis:
            applicable_rules[rule_name] = thresholds

    return applicable_rules

def _apply_overrides(
    rules: dict,
    threshold_overrides: dict | None,
) -> dict:
    """
    Apply optional per-session threshold overrides on top of the
    rules loaded from rules.yaml.

    rules.yaml remains the source of truth for which rules exist and
    for every structural field (type, numerator, denominator,
    direction, min_groups). Overrides may only change "warning" and
    "critical" values, and only for rules that already exist in
    rules.yaml.

    Parameters
    ----------
    rules : dict
        Rules dictionary as loaded from rules.yaml.
    threshold_overrides : dict | None
        Optional mapping of rule name to a dict containing "warning"
        and/or "critical" override values.

    Returns
    -------
    dict
        A new rules dictionary with overrides applied. The original
        `rules` dictionary is not mutated.

    Raises
    ------
    ValueError
        If an override references a rule name that does not exist
        in rules.yaml, or attempts to change a field other than
        "warning"/"critical".
    """

    if not threshold_overrides:
        return rules

    merged_rules = {
        rule_name: dict(thresholds)
        for rule_name, thresholds in rules.items()
    }

    for rule_name, override_fields in threshold_overrides.items():

        if rule_name not in merged_rules:
            raise ValueError(
                f"Unknown rule name in threshold_overrides: "
                f"{rule_name!r}. This rule does not exist in "
                "rules.yaml. Overrides may only target existing "
                "rules."
            )

        invalid_fields = (
            set(override_fields.keys()) - _OVERRIDABLE_FIELDS
        )

        if invalid_fields:
            raise ValueError(
                f"Invalid override field(s) for rule "
                f"{rule_name!r}: {sorted(invalid_fields)}. "
                f"Overrides may only change "
                f"{sorted(_OVERRIDABLE_FIELDS)}. Fields such as "
                f"type, numerator, denominator, direction, and "
                f"min_groups are defined by rules.yaml and cannot "
                "be overridden."
            )

        merged_rules[rule_name].update(override_fields)

    return merged_rules


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

    Rules must explicitly define their direction in rules.yaml.
    """

    warning = thresholds["warning"]
    critical = thresholds["critical"]
    direction = thresholds["direction"]

    status = _evaluate_status(
        value=value,
        warning=warning,
        critical=critical,
        direction=direction,
    )

    return {
        "rule_type": "scalar",
        "value": round(value, 2),
        "status": status,
        "direction": direction,
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

    Examples
    --------
    category_profit_margin
        category_profit / category_sales

    category_sales_concentration
        category_sales / total_sales

    Applicability is controlled by the configured "min_groups"
    threshold. Concentration rules use min_groups: 2 so that a
    single-group dataset is reported as "not_applicable".

    Profit-margin rules do not require multiple groups and therefore
    remain meaningful when only one group exists.

    Returns
    -------
    dict | None
        Structured grouped-rule result, or None when the required
        KPI sources are unavailable.
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

    min_groups = thresholds.get("min_groups", 1)

    if len(numerator) < min_groups:
        return {
            "rule_type": "grouped",
            "status": "not_applicable",
            "direction": direction,
            "reason": (
                f"Only {len(numerator)} group(s) are present; "
                f"at least {min_groups} group(s) are required "
                "for this rule to have a meaningful business "
                "interpretation."
            ),
            "warning_threshold": warning,
            "critical_threshold": critical,
            "violations": [],
        }

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

            value = (
                numerator[group]
                / denominator_value
            ) * 100

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

            value = (
                numerator_value
                / denominator
            ) * 100

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
        "direction": direction,
        "warning_threshold": warning,
        "critical_threshold": critical,
        "violations": violations,
    }


def evaluate_rules(
    kpis: dict,
    threshold_overrides: dict | None = None,
) -> dict:
    """
    Evaluate KPIs against configured rules.

    Parameters
    ----------
    kpis : dict
        KPI dictionary from kpi_engine.py.
    threshold_overrides : dict | None, optional
        Optional per-session override of "warning" and/or "critical"
        threshold values, keyed by rule name, e.g.:

            {
                "profit_margin": {"warning": 12, "critical": 6},
                "category_sales_concentration": {"warning": 35},
            }

        rules.yaml remains the source of truth for which rules
        exist and for all structural fields (type, numerator,
        denominator, direction, min_groups) — those cannot be
        overridden. rules.yaml itself is never modified; overrides
        apply only in memory for this evaluation call. When None
        (the default), behavior is identical to having no overrides
        at all.

    Returns
    -------
    dict
        Structured rule evaluation results.

    Raises
    ------
    ValueError
        If threshold_overrides references a rule name that does not
        exist in rules.yaml, or attempts to override a field other
        than "warning"/"critical".
    """

    rules = _load_rules()

    rules = _apply_overrides(
        rules=rules,
        threshold_overrides=threshold_overrides,
    )

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