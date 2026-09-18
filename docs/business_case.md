# Business Case

## Context

A generic retail bank's management team needs a single, connected view across
customer behavior, product performance, financial results, credit risk, and
growth planning — rather than a set of disconnected reports. This project
builds that view end-to-end: from raw (synthetic) transactional data, through
analytics and machine learning models, to an executive dashboard and a
board-ready Excel workbook.

## The business questions this project answers

1. Who are our most valuable customers, and which segments are profitable?
2. Which customers are at risk of churn, and why?
3. Which products drive customer value, and which underperform?
4. How are deposits and loans trending, and where is credit risk concentrated?
5. Where is cross-sell opportunity highest?
6. How is fee income and net interest income changing, and why?
7. Which branches and channels perform best?
8. How should the bank allocate acquisition and retention budget?
9. What will deposits, loans, revenue and profit look like over the next 12 months?
10. How can the bank grow the customer base and loan portfolio while
    controlling credit risk and protecting profitability?

## The management planning task

> **"Grow the customer base and loan portfolio while maintaining healthy
> profitability and controlling credit risk."**

This is the thread that connects every analytical layer in the project:

```
DATA → CUSTOMER INTELLIGENCE → PRODUCT ANALYTICS → FINANCE → RISK
     → FORECASTING → SCENARIO PLANNING → OPTIMIZATION → MANAGEMENT DECISIONS
```

The dashboard's **Scenario Planning** and **Optimization** sections give a
concrete, quantified answer: five scenarios (Base / Growth / Efficiency /
Downside / Stress) show the trade-offs of different growth strategies, and
the budget-allocation model shows how to get more expected profit from the
same marketing/retention spend by targeting it at the right segments.

## Why the dataset is synthetic and scaled down

All data in this repository is synthetic, generated with fixed random seeds
(see `src/data_generation/generate_all.py`). The scale (20,000 customers,
24 months, ~500K transactions) is a deliberate choice for a public GitHub
portfolio: it keeps the repository fast to regenerate and reasonably sized,
while preserving the same table structure, business logic, and statistical
correlations a much larger (500K+ customer) production-scale build would
have. See `docs/assumptions.md` for the full list of simplifications.
