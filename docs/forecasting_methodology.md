# Forecasting Methodology

`src/forecasting/forecast.py` forecasts nine bank KPIs 12 months ahead:
deposits, loans, revenue, net interest income, fee income, operating costs,
credit loss, profit, and active customer base.

## Model selection via backtest

For each series, the last 6 months of the 24-month history are held out as
a backtest window. Four candidate methods are fit on the remaining 18
months and evaluated against the holdout:

| Method | Description |
|---|---|
| Seasonal Naive | Repeats the last full seasonal cycle (or all available history if shorter) |
| Moving Average | Rolling 3-month average, recursively extended |
| Holt-Winters (ETS) | Exponential smoothing with additive trend (`statsmodels`) |
| Linear Trend (ML) | Ordinary least squares on a time index (`scikit-learn`) |

The method with the lowest backtest **MAPE** is selected per series and
refit on the full 24 months to produce the final 12-month forecast. MAE,
RMSE, MAPE, WAPE, and bias are all reported for every candidate (see
`outputs/reports/forecast_results.json` and the `Forecast` sheet in the
Excel workbook) — not just the winner — so the choice is auditable.

## Why per-series model selection

Different KPIs have different dynamics: deposits show a clear seasonal
wave, while operating costs trend nearly linearly. Selecting one model for
every series would under-fit at least some of them; per-series selection
via backtest is a simple, transparent way to let the data decide.

## Scenario planning

`src/forecasting/scenario_planning.py` is a separate, deterministic
compounding model (not machine-learned) that projects deposits, loans, fee
income, operating costs, and credit loss forward under five assumption sets
(`data/raw/scenario_assumptions.csv`): Base, Growth, Efficiency, Downside,
and Stress. It answers "what if growth/rates/credit losses/costs move by
X% per month" rather than "what does the historical trend imply" — the two
tools are complementary, not competing.

## Limitations

- 24 months of history is a short base for backtesting; a production
  forecasting system would want multiple full seasonal cycles.
- The ML "Linear Trend" model is intentionally simple (no external
  regressors); it is meant to demonstrate the model-selection framework, not
  to be a state-of-the-art forecaster.
