# Risk Methodology

## Credit risk (loans)

Each loan carries a simulated `probability_of_default` (PD) driven by the
borrower's risk segment and loan-to-income ratio, a `loss_given_default`
(LGD) drawn from a Normal(0.45, 0.10) distribution, and
`exposure_at_default` (EAD) as a fraction of the loan amount.

```
Expected Credit Loss (ECL) = PD × LGD × EAD
```

Delinquency buckets (`dpd_bucket`: Current / 30-59 / 60-89 / 90+) are drawn
from a single uniform random number per loan against cumulative thresholds
based on PD, so buckets are mutually exclusive and internally consistent.
`default_flag` = 1 when `dpd_bucket == "90+"`.

**These are analytical risk categories built for portfolio demonstration —
not IFRS 9, Basel, or any other regulatory credit-risk framework.**

### PD model

`src/risk/credit_risk_model.py` trains Logistic Regression and Gradient
Boosting classifiers on loan-level features (loan-to-income, utilization
proxy, interest rate, term, borrower tenure/income/employment/digital
engagement) to predict `default_flag`, with a 75/25 train/test split.
Reported metrics: ROC-AUC, PR-AUC, precision/recall/F1, confusion matrix,
and Brier score (calibration). Because default is rare (~2.5%), PR-AUC and
recall are more informative than raw accuracy — the model explicitly is not
tuned to maximize accuracy alone.

## Customer churn

`churn_flag` = the customer had zero activity for the remainder of the
24-month observation window. `src/customer/churn_model.py` predicts churn
using only features observable through month 18 (a temporal cutoff), to
avoid leaking information from the churn event itself into the features —
predicting the future using only the past, as any real deployment would
need to.

## Fraud

Fraud events (`fraud_events.csv`) are synthetic and independent of the
credit-risk model. Detection and false-positive rates are simulated
directly rather than modeled, since building a full fraud-detection
classifier was out of scope for this iteration — the dashboard reports
category/channel breakdowns and detection-rate KPIs from the simulated
events as an anomaly-monitoring view.

## Limitations

- Risk buckets (Low/Moderate/Elevated/High/Critical) are relative
  percentile-based categories over the synthetic population, not absolute
  regulatory ratings.
- LGD and recovery assumptions are illustrative, not calibrated to any real
  collections/recovery process.
- The credit and churn models are trained once on the full synthetic
  history; a production deployment would retrain on a rolling window and
  monitor for drift.
