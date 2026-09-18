#!/usr/bin/env python3
"""
Run the full analytics & ML pipeline (after data generation):
churn model -> credit risk model -> cross-sell analytics -> forecasting
-> scenario planning -> budget optimization.
"""
import subprocess
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), "..")

STEPS = [
    ("Churn prediction model", "src/customer/churn_model.py"),
    ("Credit risk (PD) model", "src/risk/credit_risk_model.py"),
    ("Cross-sell / next-best-product analytics", "src/customer/cross_sell_analytics.py"),
    ("12-month forecasting", "src/forecasting/forecast.py"),
    ("Scenario planning", "src/forecasting/scenario_planning.py"),
    ("Marketing/retention budget optimization", "src/optimization/budget_allocation.py"),
]

if __name__ == "__main__":
    for label, rel_path in STEPS:
        print(f"\n=== {label} ===")
        rc = subprocess.call([sys.executable, os.path.join(BASE, rel_path)])
        if rc != 0:
            print(f"FAILED: {label}")
            sys.exit(rc)
    print("\nPipeline complete.")
