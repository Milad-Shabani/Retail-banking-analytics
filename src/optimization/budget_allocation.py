"""
Budget Allocation Optimization
--------------------------------
Allocates an annual marketing & retention budget across customer segments
using Linear Programming to maximize expected incremental contribution
profit, subject to a budget cap, a per-segment CAC ceiling, a minimum
retention-spend floor for At-Risk segments, and a minimum strategic
investment in every segment.
"""
import pandas as pd
import numpy as np
import json, os
import pulp

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "outputs", "reports")
os.makedirs(OUT, exist_ok=True)

customers = pd.read_csv(os.path.join(RAW, "customers.csv"))

seg_stats = customers.groupby("value_segment").agg(
    n_customers=("customer_id", "count"),
    avg_clv=("customer_lifetime_value", "mean"),
    churn_rate=("churn_flag", "mean"),
).reset_index()
seg_stats["segment"] = seg_stats["value_segment"]

TOTAL_BUDGET = 500_000.0
CAC_CEILING_PER_SEGMENT = 200_000.0
MIN_SPEND_PER_SEGMENT = 15_000.0
AT_RISK_MIN_SHARE = 0.15  # at least 15% of budget must target retention of at-risk-prone segments

segments = seg_stats["segment"].tolist()
# expected incremental profit per $ spent: proportional to avg CLV and inversely to churn risk cost,
# with diminishing returns modeled via a concave (sqrt) response captured through piecewise linear segments below.
response_rate = {}
for _, row in seg_stats.iterrows():
    base_response = np.clip(row["avg_clv"] / 5000, 0.05, 3.0)
    risk_penalty = 1 - row["churn_rate"] * 0.5
    response_rate[row["segment"]] = float(base_response * risk_penalty)

prob = pulp.LpProblem("Marketing_Retention_Budget_Allocation", pulp.LpMaximize)
spend = {s: pulp.LpVariable(f"spend_{s.replace(' ', '_')}", lowBound=MIN_SPEND_PER_SEGMENT, upBound=CAC_CEILING_PER_SEGMENT)
         for s in segments}

# concave response via 3-block piecewise approximation (returns taper past 60% of ceiling)
blocks = []
for s in segments:
    b1 = pulp.LpVariable(f"b1_{s.replace(' ', '_')}", lowBound=0, upBound=CAC_CEILING_PER_SEGMENT * 0.5)
    b2 = pulp.LpVariable(f"b2_{s.replace(' ', '_')}", lowBound=0, upBound=CAC_CEILING_PER_SEGMENT * 0.3)
    b3 = pulp.LpVariable(f"b3_{s.replace(' ', '_')}", lowBound=0, upBound=CAC_CEILING_PER_SEGMENT * 0.2)
    prob += spend[s] == b1 + b2 + b3 + MIN_SPEND_PER_SEGMENT * 0  # spend already lower-bounded; blocks model the variable portion
    blocks.append((s, b1, b2, b3))

objective_terms = []
for s, b1, b2, b3 in blocks:
    r = response_rate[s]
    objective_terms.append(r * 1.0 * b1 + r * 0.6 * b2 + r * 0.3 * b3)
prob += pulp.lpSum(objective_terms)

prob += pulp.lpSum(spend.values()) <= TOTAL_BUDGET
at_risk_segments = [s for s in segments if s in ("Mass", "Mass Affluent")]
if at_risk_segments:
    prob += pulp.lpSum(spend[s] for s in at_risk_segments) >= AT_RISK_MIN_SHARE * TOTAL_BUDGET

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))

optimized_alloc = {s: round(spend[s].value(), 2) for s in segments}
current_alloc = {s: round(TOTAL_BUDGET / len(segments), 2) for s in segments}  # naive even split as "current" baseline

def expected_profit(alloc):
    total = 0
    for s in segments:
        total += response_rate[s] * min(alloc[s], CAC_CEILING_PER_SEGMENT * 0.5) * 1.0
        rem = max(alloc[s] - CAC_CEILING_PER_SEGMENT * 0.5, 0)
        total += response_rate[s] * min(rem, CAC_CEILING_PER_SEGMENT * 0.3) * 0.6
        rem2 = max(rem - CAC_CEILING_PER_SEGMENT * 0.3, 0)
        total += response_rate[s] * min(rem2, CAC_CEILING_PER_SEGMENT * 0.2) * 0.3
    return total

current_profit = expected_profit(current_alloc)
optimized_profit = expected_profit(optimized_alloc)

results = {
    "status": pulp.LpStatus[status],
    "total_budget": TOTAL_BUDGET,
    "cac_ceiling_per_segment": CAC_CEILING_PER_SEGMENT,
    "min_spend_per_segment": MIN_SPEND_PER_SEGMENT,
    "response_rate_by_segment": {s: round(r, 4) for s, r in response_rate.items()},
    "current_allocation_even_split": current_alloc,
    "optimized_allocation": optimized_alloc,
    "expected_incremental_profit_current": round(current_profit, 2),
    "expected_incremental_profit_optimized": round(optimized_profit, 2),
    "expected_profit_uplift_pct": round((optimized_profit / current_profit - 1) * 100, 2) if current_profit else None,
}

with open(os.path.join(OUT, "optimization_results.json"), "w") as fh:
    json.dump(results, fh, indent=2)

print(json.dumps(results, indent=2))
