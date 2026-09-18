"""
Customer Churn Prediction
-------------------------
Target: whether a customer has churned by month 24 (end of observation window),
predicted using only behavior observed through month 18 (temporal cutoff) to
avoid leakage. Compares a baseline Logistic Regression against a Gradient
Boosting model, with ROC-AUC / PR-AUC / Precision / Recall / F1 / calibration.
"""
import pandas as pd
import numpy as np
import json, os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (roc_auc_score, average_precision_score, precision_score,
                              recall_score, f1_score, confusion_matrix, brier_score_loss)

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "outputs", "reports")
os.makedirs(OUT, exist_ok=True)

CUTOFF_MONTH = "2024-06"  # features computed through this month; target = churn by 2024-12

customers = pd.read_csv(os.path.join(RAW, "customers.csv"))
_p = os.path.join(RAW, "monthly_customer_metrics.csv")
mcm = pd.read_csv(_p if os.path.exists(_p) else _p + ".gz")

pre_cutoff = mcm[mcm["month"] <= CUTOFF_MONTH]
feat = pre_cutoff.groupby("customer_id").agg(
    avg_balance=("balance", "mean"),
    balance_trend=("balance", lambda s: (s.iloc[-3:].mean() - s.iloc[:3].mean()) if len(s) >= 6 else 0),
    avg_txn=("transaction_count", "mean"),
    recent_txn=("transaction_count", lambda s: s.iloc[-3:].mean()),
    months_observed=("month", "count"),
    inactive_months=("is_active", lambda s: (~s.astype(bool)).sum()),
).reset_index()

df = feat.merge(customers[["customer_id", "age", "tenure_years", "annual_income", "digital_adoption",
                            "employment_status", "products_owned_count", "premium_customer_flag",
                            "salary_customer_flag", "churn_flag"]], on="customer_id")

df["digital_high"] = (df["digital_adoption"] == "High").astype(int)
df["unemployed"] = (df["employment_status"] == "Unemployed").astype(int)
df["premium_customer_flag"] = df["premium_customer_flag"].astype(int)
df["salary_customer_flag"] = df["salary_customer_flag"].astype(int)
df["target_churn"] = df["churn_flag"].astype(int)

feature_cols = ["avg_balance", "balance_trend", "avg_txn", "recent_txn", "inactive_months",
                 "age", "tenure_years", "annual_income", "digital_high", "unemployed",
                 "products_owned_count", "premium_customer_flag", "salary_customer_flag"]

X = df[feature_cols].fillna(0)
y = df["target_churn"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

log_reg = LogisticRegression(max_iter=1000, class_weight="balanced")
log_reg.fit(X_train_s, y_train)
lr_proba = log_reg.predict_proba(X_test_s)[:, 1]

gbc = GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.08, random_state=42)
gbc.fit(X_train, y_train)
gbc_proba = gbc.predict_proba(X_test)[:, 1]

def eval_model(y_true, proba, thresh=0.5):
    pred = (proba >= thresh).astype(int)
    return {
        "roc_auc": round(roc_auc_score(y_true, proba), 4),
        "pr_auc": round(average_precision_score(y_true, proba), 4),
        "precision": round(precision_score(y_true, pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, pred, zero_division=0), 4),
        "brier_score": round(brier_score_loss(y_true, proba), 4),
        "confusion_matrix": confusion_matrix(y_true, pred).tolist(),
    }

results = {
    "cutoff_month": CUTOFF_MONTH,
    "n_train": len(X_train), "n_test": len(X_test),
    "churn_rate_test": round(y_test.mean(), 4),
    "logistic_regression": eval_model(y_test, lr_proba),
    "gradient_boosting": eval_model(y_test, gbc_proba),
    "feature_importance_gbc": sorted(
        [{"feature": f, "importance": round(float(i), 4)} for f, i in zip(feature_cols, gbc.feature_importances_)],
        key=lambda x: -x["importance"]),
}

with open(os.path.join(OUT, "churn_model_results.json"), "w") as fh:
    json.dump(results, fh, indent=2)

# score full customer base with the better model for downstream use (next-best-action, dashboard)
best_proba_full = gbc.predict_proba(X[feature_cols])[:, 1] if results["gradient_boosting"]["roc_auc"] >= results["logistic_regression"]["roc_auc"] else log_reg.predict_proba(scaler.transform(X))[:, 1]
df["churn_probability_90d"] = np.round(best_proba_full, 4)
df[["customer_id", "churn_probability_90d"]].to_csv(os.path.join(BASE, "data", "processed", "churn_scores.csv"), index=False)

print(json.dumps(results, indent=2))
print("\nBest model:", "Gradient Boosting" if results["gradient_boosting"]["roc_auc"] >= results["logistic_regression"]["roc_auc"] else "Logistic Regression")
