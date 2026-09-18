# Assumptions &amp; Limitations

Read this before interpreting any number in this repository.

## What this project is

A **synthetic, reproducible** (seed = 42) retail banking analytics case
study built for a public GitHub portfolio. It is not a real bank, does not
use real customer data, and is not a regulatory, investment, or credit
decisioning system.

## Scale

| | This project | A production-scale build |
|---|---|---|
| Customers | 20,000 | 500,000+ |
| History | 24 months | 24–36 months |
| Transactions | ~500,000 | 5,000,000+ |
| Branches | 25 | 20–30 |

The table structure, column set, and business logic (segmentation formulas,
PD/LGD/ECL calculation, NII/NIM composition, forecasting framework,
optimization formulation) are identical in spirit to what a full-scale
build would use — only the row counts are scaled down, specifically so the
repository stays fast to regenerate (~2 minutes end-to-end) and reasonably
sized for GitHub (data files are gzip-compressed where large).

## Financial model

- ROA, ROE, NIM, and Cost-to-Income are **simplified analytical proxies**
  (see `docs/financial_model.md`), not audited or regulatory figures.
  Equity is proxied as ~10% of a simplified asset base; there is no modeled
  regulatory capital, RWA, or liquidity ratio.
- The synthetic loan book skews toward higher-yielding personal/consumer/
  credit-card lending, which pushes NIM/ROA/ROE somewhat above a typical
  mature-market, mortgage-heavy retail bank. This is disclosed rather than
  smoothed away.

## Risk

- PD, LGD, EAD, ECL, NPL, and risk buckets are **analytical categories for
  portfolio demonstration** — not IFRS 9, Basel, or any other regulatory
  credit-risk framework (see `docs/risk_methodology.md`).
- Liquidity-style analytics (deposit inflow/outflow trend) are a simulation,
  not a regulatory liquidity report (e.g., not LCR/NSFR).

## Fraud &amp; customer experience

- Fraud events, detection rates, and NPS-like satisfaction scores are
  synthetic and do not represent real industry benchmarks.

## Iran province map (dashboard)

- Province boundary geometry on the "Customer Activity Index by Province"
  map (Branch Performance section) is real, simplified from OpenStreetMap
  contributors via the `mrunderline/iran-geojson` dataset, licensed under
  the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).
  Boundaries are simplified (Ramer-Douglas-Peucker) for lightweight display.
- The **customer-activity index values** shown on that map are illustrative
  and self-generated (fixed random seed) — they are not derived from the
  core `customers.csv` dataset (which uses generic `Region-01..12` labels)
  and do not represent real population, revenue, or customer counts.

## Forecasting &amp; scenarios

- 24 months of history is a short base for time-series backtesting.
  Forecasts and scenario projections are illustrative of methodology, not
  investment or business advice.

## General

This project is for **educational and portfolio purposes only**. It is not
a regulatory banking model, investment recommendation, credit decisioning
system, or the internal data/methodology of any real financial institution.
