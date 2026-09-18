# Segmentation Methodology

Six complementary segmentation schemes are computed in
`src/data_generation/generate_all.py` (section 7) directly from simulated
customer behavior — none are randomly assigned.

## RFM (Recency / Frequency / Monetary)

Adapted for banking:
- **Recency** = months since the customer's last active month.
- **Frequency** = average monthly transaction count.
- **Monetary** = average account balance.

Each dimension is scored 1–5 by quintile (`r_score`, `f_score`, `m_score`),
combined into `rfm_score`, and mapped to a segment (Champions / Loyal
Customers / Potential Loyalist / At Risk / Lost) using score thresholds.

## Value segment

`customer_value_score` (0–100) is the average of the three RFM quintile
scores, rescaled. Value segments (Mass / Mass Affluent / Affluent / High
Value / Premium) are score bands.

## Lifecycle segment

Derived from churn status, tenure, and recent recency: New (<6 months
tenure) → Growing (6mo–2yr) → Established / Loyal (2yr+, above-median
activity) → At Risk (recent inactivity) → Churned.

## Behavioral segment

Digital First / Branch Dependent / Deposit Heavy / Transaction Heavy / Low
Engagement, assigned from digital adoption level and balance/frequency
percentiles.

## Customer Lifetime Value (CLV)

A simplified 3-year forward-looking model:

```
Contribution = (Avg Balance × 4.5% revenue yield)
             + (Monthly Txns × 12 × $0.35 fee proxy)
             + (Annual Income × 0.2% cross-sell proxy)
             − (Avg Balance × 1.2% servicing cost)
             − (Risk-adjusted expected loss proxy)

CLV = Contribution × Expected Survival Years (3 years, discounted by churn probability)
```

This is a portfolio-appropriate simplification, not a discounted-cash-flow
valuation model — it does not use a formal discount rate or model
acquisition-cost payback explicitly (acquisition cost is tracked separately
per channel in `channels.csv` and compared to CLV as an LTV:CAC ratio on
the dashboard).

## Cross-sell / product affinity

`src/customer/cross_sell_analytics.py` computes **lift** for each product
pair: `P(both) / (P(A) × P(B))`, restricted to pairs with at least 30
customers holding both products (to avoid noisy small-sample lift values).
It also compares realized retention for customers holding both products in
a high-lift pair vs. holding only the first product — this is an observed
correlation in the synthetic data's generation process, not a claimed
causal effect.
