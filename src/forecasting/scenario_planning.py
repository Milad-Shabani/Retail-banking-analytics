"""
Scenario Planning
------------------
Projects deposits, loans, revenue, NII, credit loss, opex and profit 12
months forward under 5 scenarios (Base, Growth, Efficiency, Downside,
Stress), using the assumption set in scenario_assumptions.csv applied
compoundingly to the last actual month of financials.csv.
"""
import pandas as pd
import numpy as np
import json, os

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "outputs", "reports")
os.makedirs(OUT, exist_ok=True)

fin = pd.read_csv(os.path.join(RAW, "financials.csv"))
fi = pd.read_csv(os.path.join(RAW, "forecast_inputs.csv"))
scenarios = pd.read_csv(os.path.join(RAW, "scenario_assumptions.csv"))

last = fin.iloc[-1]
last_loans = fi.iloc[-1]["outstanding_loans_proxy"]
HORIZON = 12

all_results = {}
for _, sc in scenarios.iterrows():
    deposits = last["total_balance"]
    loans_bal = last_loans
    revenue = last["total_revenue"]
    nii = last["net_interest_income"]
    fee = last["fee_income"]
    opex = last["total_operating_cost"]
    credit_loss = last["credit_loss"]
    customers = last["active_customers"]

    path = []
    for m in range(1, HORIZON + 1):
        deposits *= (1 + sc["deposit_growth_monthly"])
        loans_bal *= (1 + sc["loan_growth_monthly"])
        fee *= (1 + sc["fee_income_growth_monthly"])
        opex *= (1 + sc["operating_cost_growth_monthly"])
        customers *= (1 + sc["customer_acquisition_growth_monthly"] - sc["churn_rate_monthly"])
        base_yield = 0.082 + sc["interest_rate_delta"]
        nii = loans_bal * base_yield / 12 + deposits * 0.10 / 12 - deposits * 0.02 / 12
        credit_loss = (last["credit_loss"] / max(last_loans, 1)) * loans_bal * sc["credit_loss_multiplier"]
        revenue = nii + fee + revenue * 0.15 * 0  # card/other revenue held roughly flat via nii+fee dominant terms
        revenue = nii + fee + last["card_revenue"] + last["other_operating_income"]
        profit = revenue - opex - credit_loss
        path.append({
            "month_ahead": m, "deposits": round(deposits, 2), "loans": round(loans_bal, 2),
            "revenue": round(revenue, 2), "net_interest_income": round(nii, 2),
            "credit_loss": round(credit_loss, 2), "operating_cost": round(opex, 2),
            "profit": round(profit, 2), "active_customers": round(customers, 0),
        })
    end = path[-1]
    roa_proxy = round(end["profit"] * 12 / (end["deposits"] + end["loans"]), 4)
    all_results[sc["scenario"]] = {
        "assumptions": sc.drop("scenario").to_dict(),
        "month_12_snapshot": end,
        "cumulative_12m_profit": round(sum(p["profit"] for p in path), 2),
        "roa_annualized_month12": roa_proxy,
        "path": path,
    }

with open(os.path.join(OUT, "scenario_results.json"), "w") as fh:
    json.dump(all_results, fh, indent=2)

print("Scenario 12-month snapshots:")
for name, r in all_results.items():
    print(f"  {name:16s} profit(m12)={r['month_12_snapshot']['profit']:>12,.0f}  "
          f"cum_12m_profit={r['cumulative_12m_profit']:>13,.0f}  ROA={r['roa_annualized_month12']:.2%}")
