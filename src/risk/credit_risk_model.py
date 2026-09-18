"""
Credit Risk — Probability of Default Model
-------------------------------------------
Target: default_flag (90+ days past due) at the loan level.
Compares Logistic Regression vs Gradient Boosting; reports ROC-AUC, PR-AUC,
precision/recall/F1, confusion matrix and calibration (Brier score).
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

loans = pd.read_csv(os.path.join(RAW, "loans.csv"))
customers = pd.read_csv(os.path.join(RAW, "customers.csv"))

df = loans.merge(customers[["customer_id", "annual_income", "tenure_years", "digital_adoption",
                             "employment_status", "products_owned_count"]], on="customer_id")

df["loan_to_income"] = df["loan_amount"] / df["annual_income"].clip(lower=1000)
df["utilization_proxy"] = df["outstanding_balance"] / df["loan_amount"].clip(lower=1)
df["employed"] = (df["employment_status"] == "Employed").astype(int)
df["digital_high"] = (df["digital_adoption"] == "High").astype(int)
df["target_default"] = df["default_flag"].astype(int)

feature_cols = ["loan_amount", "interest_rate", "term_months", "loan_to_income", "utilization_proxy",
                 "annual_income", "tenure_years", "employed", "digital_high", "products_owned_count"]

X = df[feature_cols].fillna(0)
y = df["target_default"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s, X_test_s = scaler.fit_transform(X_train), scaler.transform(X_test)

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
    "n_loans": len(df), "default_rate": round(y.mean(), 4),
    "n_train": len(X_train), "n_test": len(X_test),
    "logistic_regression": eval_model(y_test, lr_proba),
    "gradient_boosting": eval_model(y_test, gbc_proba),
    "feature_importance_gbc": sorted(
        [{"feature": f, "importance": round(float(i), 4)} for f, i in zip(feature_cols, gbc.feature_importances_)],
        key=lambda x: -x["importance"]),
}

# Portfolio risk summary
risk_summary = loans.groupby("risk_bucket").agg(
    loan_count=("loan_id", "count"),
    total_exposure=("exposure_at_default", "sum"),
    avg_pd=("probability_of_default", "mean"),
    avg_lgd=("loss_given_default", "mean"),
    total_expected_loss=("expected_credit_loss", "sum"),
).reset_index()
results["portfolio_risk_summary"] = risk_summary.round(4).to_dict(orient="records")

dpd_summary = loans["dpd_bucket"].value_counts(normalize=True).round(4).to_dict()
results["dpd_distribution"] = dpd_summary
results["npl_ratio"] = round((loans["outstanding_balance"][loans["dpd_bucket"] == "90+"].sum() /
                               loans["outstanding_balance"].sum()), 4)

with open(os.path.join(OUT, "credit_risk_model_results.json"), "w") as fh:
    json.dump(results, fh, indent=2)

print(json.dumps({k: v for k, v in results.items() if k not in ("portfolio_risk_summary",)}, indent=2))
