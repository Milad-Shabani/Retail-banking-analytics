# Optimization Methodology

`src/optimization/budget_allocation.py` allocates a fixed annual marketing
and retention budget ($500,000) across the five customer value segments
(Mass / Mass Affluent / Affluent / High Value / Premium) to maximize
expected incremental contribution profit.

## Formulation (Linear Program, solved with PuLP / CBC)

**Decision variables:** spend per segment, split into three concave-response
blocks per segment (piecewise-linear approximation of diminishing returns —
the first dollars spent on a segment convert better than the last).

**Objective:** maximize `Σ (segment response rate × spend in each block ×
block multiplier)`, where block multipliers (1.0 / 0.6 / 0.3) approximate
diminishing marginal returns as spend increases.

**Constraints:**
- Total spend ≤ $500,000 (budget cap).
- Spend per segment ≤ $200,000 (CAC/concentration ceiling — no single
  segment absorbs the whole budget).
- Spend per segment ≥ $15,000 (minimum strategic investment — every segment
  gets some retention coverage).
- Mass + Mass Affluent segments together receive ≥ 15% of the budget (a
  retention floor for higher-churn-risk segments).

**Response rate per segment** is proportional to average CLV in that
segment, discounted by the segment's churn rate (spend on a
higher-churn segment converts to less durable profit).

## Output

The model reports the current (even-split) allocation vs. the optimized
allocation, and the expected incremental profit uplift — surfaced on the
dashboard's Optimization panel and the Excel `Optimization` sheet.

## Limitations

This is a **stylized allocation model** for demonstrating the optimization
workflow (formulate → constrain → solve → compare to baseline), not a
calibrated marketing-mix model. The response-rate function and piecewise
diminishing-returns blocks are reasonable assumptions, not estimated from
real campaign elasticity data.
