"""
Threshold override test — Phase 2.

Verifies:
1. threshold_overrides=None reproduces exact current behavior
   (regression against Phase 1 baseline).
2. A valid override changes the evaluated status as expected.
3. An override on a non-existent rule name raises ValueError.
4. An override on a non-threshold field raises ValueError.
"""

from analytics.kpi_engine import calculate_kpis
from analytics.rule_engine import evaluate_rules
import pandas as pd


rows = 20
df = pd.DataFrame({
    "Sales": [100 + i * 10 for i in range(rows)],
    "Profit": [10 + i for i in range(rows)],
})

kpis = calculate_kpis(df)
print("KPIS:", kpis)

# --- 1. None behaves identically to no overrides ---
baseline = evaluate_rules(kpis)
baseline_explicit_none = evaluate_rules(kpis, threshold_overrides=None)

print("\n=== Test 1: None regression ===")
print("MATCH:", "OK" if baseline == baseline_explicit_none else "FAIL")
print("profit_margin status (default):", baseline["profit_margin"]["status"])

# --- 2. Valid override changes status ---
print("\n=== Test 2: Valid override changes status ===")
overridden = evaluate_rules(
    kpis,
    threshold_overrides={"profit_margin": {"warning": 1, "critical": 0}},
)
print("profit_margin status (overridden, easier thresholds):", overridden["profit_margin"]["status"])
print("EXPECT: normal (since actual margin should now clear the relaxed warning bar)")

# --- 3. Unknown rule name raises ---
print("\n=== Test 3: Unknown rule name raises ValueError ===")
try:
    evaluate_rules(kpis, threshold_overrides={"not_a_real_rule": {"warning": 5}})
    print("FAIL: no exception raised")
except ValueError as error:
    print("OK - raised:", error)

# --- 4. Structural field override raises ---
print("\n=== Test 4: Structural field override raises ValueError ===")
try:
    evaluate_rules(kpis, threshold_overrides={"profit_margin": {"direction": "higher"}})
    print("FAIL: no exception raised")
except ValueError as error:
    print("OK - raised:", error)

print("\n=== DONE ===")