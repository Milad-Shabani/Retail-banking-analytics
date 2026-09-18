"""
Forecasting — 12-Month Ahead
------------------------------
Forecasts key bank KPIs (deposits, loans proxy, revenue, NII, fee income,
operating costs, credit loss, profit, customer base) using time-series
validation. Compares Seasonal Naive, Moving Average, Holt-Winters (ETS) and
a simple ML (linear trend + seasonal dummies) model; the best performer per
series (lowest backtest MAPE) is used for the final 12-month forecast.
"""
import pandas as pd
import numpy as np
import json, os
import warnings
warnings.filterwarnings("ignore")
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "outputs", "reports")
os.makedirs(OUT, exist_ok=True)

fin = pd.read_csv(os.path.join(RAW, "financials.csv"))
fi = pd.read_csv(os.path.join(RAW, "forecast_inputs.csv"))
df = fin.merge(fi[["month", "outstanding_loans_proxy"]], on="month")
df["month"] = pd.PeriodIndex(df["month"], freq="M")
df = df.sort_values("month").reset_index(drop=True)

SERIES = {
    "deposits": "total_balance",
    "loans": "outstanding_loans_proxy",
    "revenue": "total_revenue",
    "net_interest_income": "net_interest_income",
    "fee_income": "fee_income",
    "operating_costs": "total_operating_cost",
    "credit_loss": "credit_loss",
    "profit": "profit_after_credit_costs",
    "customer_base": "active_customers",
}

HORIZON = 12
BACKTEST_HOLDOUT = 6


def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def wape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return float(np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) * 100)


def seasonal_naive_forecast(train, horizon, season=12):
    if len(train) >= season:
        pattern = train[-season:]
    else:
        pattern = train
    reps = int(np.ceil(horizon / len(pattern)))
    return np.tile(pattern, reps)[:horizon]


def moving_avg_forecast(train, horizon, window=3):
    vals = list(train)
    out = []
    for _ in range(horizon):
        nxt = np.mean(vals[-window:])
        out.append(nxt)
        vals.append(nxt)
    return np.array(out)


def ets_forecast(train, horizon):
    try:
        model = ExponentialSmoothing(train, trend="add", seasonal=None, initialization_method="estimated")
        fit = model.fit(optimized=True)
        return fit.forecast(horizon)
    except Exception:
        return moving_avg_forecast(train, horizon)


def linear_trend_forecast(train, horizon):
    X = np.arange(len(train)).reshape(-1, 1)
    y = np.array(train)
    lr = LinearRegression().fit(X, y)
    X_fut = np.arange(len(train), len(train) + horizon).reshape(-1, 1)
    return lr.predict(X_fut)


results = {"horizon_months": HORIZON, "backtest_holdout_months": BACKTEST_HOLDOUT, "series": {}}
forecast_table = {"month": [f"2025-{m:02d}" for m in range(1, 13)]}

for name, col in SERIES.items():
    values = df[col].values.astype(float)
    train_bt, test_bt = values[:-BACKTEST_HOLDOUT], values[-BACKTEST_HOLDOUT:]

    candidates = {
        "Seasonal Naive": seasonal_naive_forecast(train_bt, BACKTEST_HOLDOUT),
        "Moving Average": moving_avg_forecast(train_bt, BACKTEST_HOLDOUT),
        "Holt-Winters (ETS)": ets_forecast(train_bt, BACKTEST_HOLDOUT),
        "Linear Trend (ML)": linear_trend_forecast(train_bt, BACKTEST_HOLDOUT),
    }

    scored = {}
    for method, preds in candidates.items():
        preds = np.array(preds)
        scored[method] = {
            "mae": round(float(np.mean(np.abs(test_bt - preds))), 2),
            "rmse": round(float(np.sqrt(np.mean((test_bt - preds) ** 2))), 2),
            "mape": round(mape(test_bt, preds), 2),
            "wape": round(wape(test_bt, preds), 2),
            "bias": round(float(np.mean(preds - test_bt)), 2),
        }
    best_method = min(scored, key=lambda m: scored[m]["mape"])

    full_forecasters = {
        "Seasonal Naive": seasonal_naive_forecast(values, HORIZON),
        "Moving Average": moving_avg_forecast(values, HORIZON),
        "Holt-Winters (ETS)": ets_forecast(values, HORIZON),
        "Linear Trend (ML)": linear_trend_forecast(values, HORIZON),
    }
    final_forecast = np.array(full_forecasters[best_method])

    results["series"][name] = {
        "column": col, "best_method": best_method, "backtest_scores": scored,
        "forecast_12m": [round(float(v), 2) for v in final_forecast],
    }
    forecast_table[name] = [round(float(v), 2) for v in final_forecast]

pd.DataFrame(forecast_table).to_csv(os.path.join(BASE, "data", "processed", "forecast_12m.csv"), index=False)
with open(os.path.join(OUT, "forecast_results.json"), "w") as fh:
    json.dump(results, fh, indent=2)

for name, r in results["series"].items():
    print(f"{name:18s} best={r['best_method']:20s} MAPE(backtest)={r['backtest_scores'][r['best_method']]['mape']}%")
