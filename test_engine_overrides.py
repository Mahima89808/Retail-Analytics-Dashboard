"""
Engine threshold override test — Phase 2, engine.py passthrough.
"""

import pandas as pd
from analytics.engine import run_analysis

rows = 20
df = pd.DataFrame({
    "Sales": [100 + i * 10 for i in range(rows)],
    "Profit": [10 + i for i in range(rows)],
})

# Regression: no overrides
baseline = run_analysis(df)
print("Baseline profit_margin status:", baseline["rule_results"]["profit_margin"]["status"])

# With override
overridden = run_analysis(df, threshold_overrides={"profit_margin": {"warning": 1, "critical": 0}})
print("Overridden profit_margin status:", overridden["rule_results"]["profit_margin"]["status"])

# Confirm insights/recommendations still list[str]
print("Insights OK:", all(isinstance(i, str) for i in overridden["insights"]))
print("Recs OK:", all(isinstance(r, str) for r in overridden["recommendations"]))