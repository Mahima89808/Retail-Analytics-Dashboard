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


def run_analysis(dataframe):
    """
    Run the complete analytics pipeline.

    Parameters
    ----------
    dataframe : pandas.DataFrame

    Returns
    -------
    dict
    """

    kpis = calculate_kpis(dataframe)

    rule_results = evaluate_rules(kpis)

    insights = generate_insights(rule_results)

    recommendations = generate_recommendations(rule_results)

    return {
        "kpis": kpis,
        "rule_results": rule_results,
        "insights": insights,
        "recommendations": recommendations,
    }