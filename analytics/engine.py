"""
Analytics Engine

Responsibilities:
- Coordinate the analytics pipeline.
- Execute KPI calculation, rule evaluation, insight generation,
  and recommendation generation.
- Return all analytics results in a structured format.
"""

from analytics.kpi_engine import calculate_kpis
from analytics.rule_engine import evaluate_rules
from analytics.insight_generator import generate_insights
from analytics.recommendation_generator import generate_recommendations


def run_analysis(dataframe, threshold_overrides=None):
    """
    Run the complete analytics pipeline.

    Parameters
    ----------
    dataframe : pandas.DataFrame
    threshold_overrides : dict | None, optional
        Optional per-session threshold overrides forwarded directly
        to analytics.rule_engine.evaluate_rules(). See that function's
        docstring for the accepted shape and validation rules. When
        None (the default), behavior is identical to the pipeline
        before this parameter existed.

    Returns
    -------
    dict
    """

    kpis = calculate_kpis(dataframe)

    rule_results = evaluate_rules(kpis, threshold_overrides=threshold_overrides)

    insights = generate_insights(rule_results)

    recommendations = generate_recommendations(rule_results)

    return {
        "kpis": kpis,
        "rule_results": rule_results,
        "insights": insights,
        "recommendations": recommendations,
    }