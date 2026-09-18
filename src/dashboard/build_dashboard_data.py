"""
Dashboard Data Builder
------------------------
Aggregates everything the HTML dashboard needs into one JSON payload so the
dashboard is a fully static, self-contained file (no database, no server).
"""
import pandas as pd
import numpy as np
import json, os

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "processed")
REPORTS = os.path.join(BASE, "outputs", "reports")
OUT = os.path.join(BASE, "outputs", "dashboard")
os.makedirs(OUT, exist_ok=True)

customers = pd.read_csv(os.path.join(RAW, "customers.csv"))
products = pd.read_csv(os.path.join(RAW, "products.csv"))
loans = pd.read_csv(os.path.join(RAW, "loans.csv"))
deposits = pd.read_csv(os.path.join(RAW, "deposits.csv"))
cards = pd.read_csv(os.path.join(RAW, "cards.csv"))
branches = pd.read_csv(os.path.join(RAW, "branches.csv"))
financials = pd.read_csv(os.path.join(RAW, "financials.csv"))
fraud = pd.read_csv(os.path.join(RAW, "fraud_events.csv"))
campaigns = pd.read_csv(os.path.join(RAW, "campaigns.csv"))
campaign_resp = pd.read_csv(os.path.join(RAW, "campaign_responses.csv"))
mbm = pd.read_csv(os.path.join(RAW, "monthly_branch_metrics.csv"))
mpm = pd.read_csv(os.path.join(RAW, "monthly_product_metrics.csv"))
_p = os.path.join(RAW, "monthly_customer_metrics.csv")
mcm = pd.read_csv(_p if os.path.exists(_p) else _p + ".gz")
interactions = pd.read_csv(os.path.join(RAW, "customer_interactions.csv"))
channels = pd.read_csv(os.path.join(RAW, "channels.csv"))
credit_events = pd.read_csv(os.path.join(RAW, "credit_events.csv"))

churn_results = json.load(open(os.path.join(REPORTS, "churn_model_results.json")))
credit_results = json.load(open(os.path.join(REPORTS, "credit_risk_model_results.json")))
cross_sell = json.load(open(os.path.join(REPORTS, "cross_sell_results.json")))
forecast_results = json.load(open(os.path.join(REPORTS, "forecast_results.json")))
scenario_results = json.load(open(os.path.join(REPORTS, "scenario_results.json")))
optim_results = json.load(open(os.path.join(REPORTS, "optimization_results.json")))
forecast_12m = pd.read_csv(os.path.join(PROC, "forecast_12m.csv"))

def r(x, n=2):
    if isinstance(x, (np.floating, np.integer)):
        x = x.item()
    return round(x, n) if isinstance(x, float) else x

last = financials.iloc[-1]
data = {}

# ---------------- FILTER OPTIONS ----------------
data["filters"] = {
    "regions": sorted(customers["region"].unique().tolist()),
    "digital_segments": sorted(customers["digital_adoption"].unique().tolist()),
    "value_segments": sorted(customers["value_segment"].unique().tolist()),
}

# ---------------- EXECUTIVE OVERVIEW ----------------
data["executive"] = {
    "kpis": {
        "total_customers": int(len(customers)),
        "active_customers": int((customers["customer_status"] == "Active").sum()),
        "total_deposits": r(last["total_balance"]),
        "total_loans": r(loans["outstanding_balance"].sum()),
        "monthly_revenue": r(last["total_revenue"]),
        "net_interest_income": r(last["net_interest_income"]),
        "monthly_profit": r(last["profit_after_credit_costs"]),
        "profit_margin": r(last["profit_margin"]),
        "nim": r(last["net_interest_margin"]),
        "roa": r(last["return_on_assets"]),
        "roe": r(last["return_on_equity"]),
        "cost_to_income": r(last["cost_to_income_ratio"]),
        "churn_rate": r(customers["churn_flag"].mean()),
        "digital_adoption_high": r((customers["digital_adoption"] == "High").mean()),
        "npl_ratio": r(credit_results["npl_ratio"]),
    },
    "revenue_trend": {"months": financials["month"].tolist(), "revenue": financials["total_revenue"].round(2).tolist(),
                       "profit": financials["profit_after_credit_costs"].round(2).tolist()},
    "deposit_trend": {"months": financials["month"].tolist(), "deposits": financials["total_balance"].round(2).tolist()},
    "customer_growth": {"months": financials["month"].tolist(), "customers": financials["active_customers"].tolist()},
    "profitability_by_segment": customers.groupby("value_segment")["customer_lifetime_value"].mean().round(2).to_dict(),
    "risk_overview": customers["risk_segment"].value_counts().to_dict(),
    "insights": [
        f"Deposits grew {((last['total_balance']/financials.iloc[0]['total_balance'])-1)*100:.1f}% cumulatively over the 24-month window.",
        f"Customer churn stands at {customers['churn_flag'].mean()*100:.1f}%, with digitally engaged customers (High/Medium adoption) showing markedly stronger retention than low-adoption customers.",
        f"The '{customers.groupby('value_segment')['customer_lifetime_value'].sum().idxmax()}' segment contributes the largest total lifetime value.",
        f"NPL ratio is {credit_results['npl_ratio']*100:.2f}%, concentrated in Critical/High risk-bucket loans.",
        f"Digital-first customers represent {(customers['digital_adoption']=='High').mean()*100:.1f}% of the base.",
        f"The churn model reaches {churn_results['gradient_boosting']['roc_auc']:.3f} ROC-AUC; the credit-risk PD model reaches {credit_results['gradient_boosting']['roc_auc']:.3f}.",
        f"Optimized marketing/retention allocation is projected to lift expected incremental profit by {optim_results['expected_profit_uplift_pct']:.1f}%.",
    ],
}

# ---------------- CUSTOMERS ----------------
data["customers"] = {
    "lifecycle": customers["lifecycle_segment"].value_counts().to_dict(),
    "value_segment": customers["value_segment"].value_counts().to_dict(),
    "rfm_segment": customers["rfm_segment"].value_counts().to_dict(),
    "digital_segment": customers["digital_adoption"].value_counts().to_dict(),
    "behavioral_segment": customers["behavioral_segment"].value_counts().to_dict(),
    "clv_by_segment": customers.groupby("value_segment")["customer_lifetime_value"].mean().round(2).to_dict(),
    "products_per_customer": r(customers["products_owned_count"].mean(), 3),
    "single_vs_multi": {"single_product": int((customers["products_owned_count"] <= 1).sum()),
                         "multi_product": int((customers["products_owned_count"] > 1).sum())},
    "churn_by_region": customers.groupby("region")["churn_flag"].mean().round(4).to_dict(),
    "age_band_distribution": customers["age_band"].value_counts().to_dict(),
    "cac_ltv": {
        "avg_clv": r(customers["customer_lifetime_value"].mean()),
        "avg_cac": r(channels["avg_acquisition_cost"].mean()),
        "ltv_cac_ratio": r(customers["customer_lifetime_value"].mean() / channels["avg_acquisition_cost"].mean(), 2),
    },
}
customers["signup_quarter"] = pd.PeriodIndex(pd.to_datetime(customers["signup_date"]), freq="Q").astype(str)
cohort = customers[customers["signup_quarter"] >= "2022Q1"].groupby("signup_quarter").agg(
    cohort_size=("customer_id", "count"), retained_rate=("churn_flag", lambda s: 1 - s.mean())).reset_index()
data["customers"]["cohort_retention"] = {"quarters": cohort["signup_quarter"].tolist(),
                                          "retention": cohort["retained_rate"].round(4).tolist()}

# ---------------- PRODUCTS ----------------
data["products"] = {
    "penetration_pct": cross_sell["product_penetration_pct"],
    "top_affinities": cross_sell["top_product_affinities"][:8],
    "cross_sell_retention_effect": cross_sell["cross_sell_retention_effect"],
    "nbp_recommendations": cross_sell.get("next_best_product_by_recommendation", {}),
}
last6 = mpm["month"].sort_values().unique()[-6:]
recent_pm = mpm[mpm["month"].isin(last6)]
data["products"]["revenue_by_product"] = recent_pm.groupby("product_name")["revenue"].mean().round(2).sort_values(ascending=False).to_dict()

# ---------------- LOANS & CREDIT RISK ----------------
data["credit"] = {
    "dpd_distribution": credit_results["dpd_distribution"],
    "npl_ratio": credit_results["npl_ratio"],
    "default_rate": credit_results["default_rate"],
    "model_comparison": {"logistic_regression": credit_results["logistic_regression"],
                          "gradient_boosting": credit_results["gradient_boosting"]},
    "portfolio_risk_summary": credit_results["portfolio_risk_summary"],
    "loans_by_type": loans.groupby("loan_type").agg(count=("loan_id", "count"), outstanding=("outstanding_balance", "sum"),
                                                       default_rate=("default_flag", "mean")).round(2).reset_index().to_dict(orient="records"),
    "loans_by_region": loans.groupby("region")["outstanding_balance"].sum().round(2).to_dict(),
}

# ---------------- FINANCIAL ----------------
data["financial"] = {
    "months": financials["month"].tolist(),
    "revenue_mix": {
        "net_interest_income": r(financials["net_interest_income"].iloc[-6:].mean()),
        "fee_income": r(financials["fee_income"].iloc[-6:].mean()),
        "card_revenue": r(financials["card_revenue"].iloc[-6:].mean()),
        "other_operating_income": r(financials["other_operating_income"].iloc[-6:].mean()),
    },
    "nim_trend": financials["net_interest_margin"].round(4).tolist(),
    "roa_trend": financials["return_on_assets"].round(4).tolist(),
    "roe_trend": financials["return_on_equity"].round(4).tolist(),
    "cost_to_income_trend": financials["cost_to_income_ratio"].round(4).tolist(),
    "profit_by_segment": customers.groupby("value_segment")["customer_lifetime_value"].sum().round(2).to_dict(),
}

# ---------------- FORECAST ----------------
data["forecast"] = {
    "months": forecast_12m["month"].tolist(),
    "historical_months": financials["month"].tolist()[-6:],
    "historical_revenue": financials["total_revenue"].round(2).tolist()[-6:],
    "historical_deposits": financials["total_balance"].round(2).tolist()[-6:],
    "historical_profit": financials["profit_after_credit_costs"].round(2).tolist()[-6:],
    "forecast_revenue": forecast_12m["revenue"].round(2).tolist(),
    "forecast_deposits": forecast_12m["deposits"].round(2).tolist(),
    "forecast_profit": forecast_12m["profit"].round(2).tolist(),
    "methods": {k: v["best_method"] for k, v in forecast_results["series"].items()},
    "backtest_mape": {k: v["backtest_scores"][v["best_method"]]["mape"] for k, v in forecast_results["series"].items()},
}

# ---------------- SCENARIO PLANNING ----------------
data["scenarios"] = {name: {"path": r["path"], "cumulative_12m_profit": r["cumulative_12m_profit"],
                             "roa_annualized_m12": r["roa_annualized_month12"]}
                      for name, r in scenario_results.items()}

# ---------------- DIGITAL BANKING ----------------
data["digital"] = {
    "adoption": customers["digital_adoption"].value_counts().to_dict(),
    "avg_txn_by_adoption": customers.groupby("digital_adoption")["frequency_avg_monthly_txns"].mean().round(2).to_dict(),
    "clv_by_adoption": customers.groupby("digital_adoption")["customer_lifetime_value"].mean().round(2).to_dict(),
    "churn_by_adoption": customers.groupby("digital_adoption")["churn_flag"].mean().round(4).to_dict(),
}

# ---------------- FRAUD ----------------
data["fraud"] = {
    "by_category": fraud.groupby("fraud_category").agg(events=("fraud_id", "count"), loss=("loss_amount", "sum"),
                                                          detection_rate=("detected_flag", "mean")).round(2).reset_index().to_dict(orient="records"),
    "by_channel": fraud.groupby("channel").agg(events=("fraud_id", "count"), loss=("loss_amount", "sum")).round(2).reset_index().to_dict(orient="records"),
    "total_events": int(len(fraud)), "total_loss": r(fraud["loss_amount"].sum()),
    "detection_rate": r(fraud["detected_flag"].mean(), 4), "false_positive_rate": r(fraud["false_positive_flag"].mean(), 4),
}

# ---------------- BRANCHES ----------------
last6b = mbm["month"].sort_values().unique()[-6:]
recent_bm = mbm[mbm["month"].isin(last6b)].merge(branches[["branch_id", "branch_name", "region"]], on="branch_id")
branch_perf = recent_bm.groupby(["branch_id", "branch_name", "region"]).agg(
    revenue=("revenue", "mean"), profit=("profit", "mean"), active_customers=("active_customers", "mean")).reset_index()
data["branches"] = {
    "top_by_profit": branch_perf.sort_values("profit", ascending=False).head(10).round(2).to_dict(orient="records"),
    "performance_matrix": branch_perf[["branch_name", "revenue", "profit"]].round(2).to_dict(orient="records"),
}

# ---------------- MARKETING ----------------
camp_perf = campaign_resp.groupby("campaign_id").agg(responses=("response_id", "count"), conversions=("converted_flag", "sum"),
                                                       revenue=("revenue_generated", "sum")).reset_index()
camp_perf = camp_perf.merge(campaigns[["campaign_id", "campaign_name", "budget"]], on="campaign_id")
camp_perf["roi_pct"] = ((camp_perf["revenue"] - camp_perf["budget"]) / camp_perf["budget"] * 100).round(1)
data["marketing"] = {
    "top_campaigns": camp_perf.sort_values("roi_pct", ascending=False).head(8)[["campaign_name", "responses", "conversions", "roi_pct"]].to_dict(orient="records"),
    "total_budget": r(campaigns["budget"].sum()), "total_conversions": int(camp_perf["conversions"].sum()),
    "avg_conversion_rate": r((camp_perf["conversions"].sum() / camp_perf["responses"].sum()), 4),
}

# ---------------- OPTIMIZATION ----------------
data["optimization"] = optim_results

# ---------------- CUSTOMER EXPERIENCE ----------------
data["experience"] = {
    "by_type": interactions.groupby("interaction_type").agg(count=("interaction_id", "count"),
                                                               avg_resolution_hrs=("resolution_time_hours", "mean"),
                                                               avg_satisfaction=("satisfaction_score", "mean")).round(2).reset_index().to_dict(orient="records"),
    "repeat_contact_rate": r(interactions["repeat_contact_flag"].mean(), 4),
    "avg_satisfaction": r(interactions["satisfaction_score"].mean(), 2),
}

# ---------------- ILLUSTRATIVE GEOGRAPHY: CUSTOMER DISTRIBUTION ACROSS IRAN ----------------
# Real province geometry (simplified from OpenStreetMap contributors, ODbL, via
# mrunderline/iran-geojson) combined with a standalone illustrative, self-generated
# (fixed-seed) customer-activity index. Not derived from the core customers.csv
# (which uses generic Region-01..12 labels) — a separate, clearly-labeled view.
_rng = np.random.default_rng(7)
IRAN_PROVINCE_WEIGHTS = {
    "West Azerbaijan": 55, "East Azerbaijan": 70, "Ardabil": 30, "Gilan": 58,
    "Mazandaran": 62, "Golestan": 38, "Kurdistan": 34, "Zanjan": 28, "Qazvin": 33,
    "Alborz": 68, "Tehran": 100, "Semnan": 18, "North Khorasan": 22, "Razavi Khorasan": 78,
    "Kermanshah": 40, "Hamadan": 36, "Markazi": 32, "Qom": 42, "Isfahan": 74,
    "South Khorasan": 16, "Ilam": 14, "Lorestan": 30, "Chaharmahal and Bakhtiari": 20,
    "Yazd": 35, "Khuzestan": 60, "Kohgiluyeh and Boyer-Ahmad": 15, "Fars": 66,
    "Kerman": 44, "Sistan and Baluchestan": 33, "Bushehr": 24, "Hormozgan": 30,
}
with open(os.path.join(os.path.dirname(__file__), "iran_map_paths.json")) as _f:
    _iran_geo = json.load(_f)

iran_provinces_out = []
for p in _iran_geo["provinces"]:
    w = IRAN_PROVINCE_WEIGHTS.get(p["name"])
    value = int(w * _rng.uniform(0.85, 1.15)) if w is not None else int(_rng.uniform(15, 40))
    iran_provinces_out.append({"name": p["name"], "path": p["path"], "cx": p["cx"], "cy": p["cy"], "value": value})

data["geo"] = {
    "width": _iran_geo["width"], "height": _iran_geo["height"],
    "provinces": iran_provinces_out,
    "source": _iran_geo["source"],
    "note": "Illustrative synthetic customer-activity index by province, for visualization purposes only — not derived from the core dataset's generic region labels.",
}

with open(os.path.join(OUT, "dashboard_data.json"), "w") as fh:
    json.dump(data, fh, default=str)

print(f"Dashboard data written: {os.path.join(OUT, 'dashboard_data.json')}")
print(f"Size: {os.path.getsize(os.path.join(OUT, 'dashboard_data.json')) / 1024:.1f} KB")
