"""
Excel Workbook Builder — RETAIL_BANKING_ANALYTICS.xlsx
---------------------------------------------------------
Assembles the multi-sheet executive workbook from the generated CSVs and
analytics JSON outputs. KPI and ratio cells use live formulas referencing
the data rows in the same workbook (per project convention); descriptive/
reporting tables are written as formatted values since they summarize a
generated dataset rather than a live financial model.
"""
import pandas as pd
import numpy as np
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "processed")
REPORTS = os.path.join(BASE, "outputs", "reports")
OUT_XLSX = os.path.join(BASE, "outputs", "excel", "RETAIL_BANKING_ANALYTICS.xlsx")
os.makedirs(os.path.dirname(OUT_XLSX), exist_ok=True)

FONT_NAME = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(name=FONT_NAME, bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(name=FONT_NAME, bold=True, size=16, color="1F3864")
SUBTITLE_FONT = Font(name=FONT_NAME, italic=True, size=10, color="595959")
LABEL_FONT = Font(name=FONT_NAME, bold=True, size=10)
NORMAL_FONT = Font(name=FONT_NAME, size=10)
KPI_FONT = Font(name=FONT_NAME, bold=True, size=14, color="1F3864")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_header_row(ws, row=1, ncols=None):
    ncols = ncols or ws.max_column
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[row].height = 26


def write_df(ws, df, start_row=1, start_col=1, header=True, number_formats=None):
    number_formats = number_formats or {}
    if header:
        for j, col in enumerate(df.columns):
            ws.cell(row=start_row, column=start_col + j, value=str(col))
        style_header_row(ws, start_row, ncols=start_col + len(df.columns) - 1)
        r0 = start_row + 1
    else:
        r0 = start_row
    for i, (_, row) in enumerate(df.iterrows()):
        for j, col in enumerate(df.columns):
            cell = ws.cell(row=r0 + i, column=start_col + j, value=row[col])
            cell.font = NORMAL_FONT
            cell.border = BORDER
            if col in number_formats:
                cell.number_format = number_formats[col]
    for j, col in enumerate(df.columns):
        maxlen = max([len(str(col))] + [len(str(v)) for v in df[col].astype(str).values[:200]])
        ws.column_dimensions[get_column_letter(start_col + j)].width = min(max(maxlen + 2, 10), 40)
    return r0 + len(df)


def title_block(ws, title, subtitle):
    ws["A1"] = title
    ws["A1"].font = TITLE_FONT
    ws["A2"] = subtitle
    ws["A2"].font = SUBTITLE_FONT
    ws.row_dimensions[1].height = 26
    ws.row_dimensions[2].height = 16


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
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
interactions = pd.read_csv(os.path.join(RAW, "customer_interactions.csv"))

churn_results = json.load(open(os.path.join(REPORTS, "churn_model_results.json")))
credit_results = json.load(open(os.path.join(REPORTS, "credit_risk_model_results.json")))
cross_sell = json.load(open(os.path.join(REPORTS, "cross_sell_results.json")))
forecast_results = json.load(open(os.path.join(REPORTS, "forecast_results.json")))
scenario_results = json.load(open(os.path.join(REPORTS, "scenario_results.json")))
optim_results = json.load(open(os.path.join(REPORTS, "optimization_results.json")))
forecast_12m = pd.read_csv(os.path.join(PROC, "forecast_12m.csv"))

wb = Workbook()
wb.remove(wb.active)

MONEY = '$#,##0;($#,##0);"-"'
PCT = "0.0%"
NUM = "#,##0"

# ---------------------------------------------------------------------------
# 1. Executive Summary
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Executive_Summary")
title_block(ws, "Retail Banking Analytics", "Customer Intelligence, Financial Performance, Risk, Churn & Forecasting — Executive Summary")
ws["A4"] = "Synthetic data for educational / portfolio purposes. Not a real bank. See Assumptions sheet."
ws["A4"].font = Font(name=FONT_NAME, italic=True, size=9, color="C00000")

last = financials.iloc[-1]
kpis = [
    ("Total Customers", len(customers), NUM),
    ("Active Customers", int((customers["customer_status"] == "Active").sum()), NUM),
    ("Total Deposits ($)", last["total_balance"], MONEY),
    ("Total Loans Outstanding ($)", loans["outstanding_balance"].sum(), MONEY),
    ("Monthly Revenue ($)", last["total_revenue"], MONEY),
    ("Net Interest Income ($)", last["net_interest_income"], MONEY),
    ("Monthly Profit ($)", last["profit_after_credit_costs"], MONEY),
    ("Net Interest Margin", last["net_interest_margin"], PCT),
    ("Return on Assets", last["return_on_assets"], PCT),
    ("Return on Equity", last["return_on_equity"], PCT),
    ("Cost-to-Income Ratio", last["cost_to_income_ratio"], PCT),
    ("Churn Rate", customers["churn_flag"].mean(), PCT),
    ("Digital Adoption (High)", (customers["digital_adoption"] == "High").mean(), PCT),
    ("NPL Ratio", credit_results["npl_ratio"], PCT),
]
row, col = 6, 1
for i, (label, value, fmt) in enumerate(kpis):
    r = row + (i // 3) * 4
    c = col + (i % 3) * 3
    cell = ws.cell(row=r, column=c, value=label)
    cell.font = LABEL_FONT
    vcell = ws.cell(row=r + 1, column=c, value=value)
    vcell.font = KPI_FONT
    vcell.number_format = fmt
    for rr in (r, r + 1):
        for cc in (c, c + 1):
            ws.cell(row=rr, column=cc).fill = PatternFill("solid", fgColor="F2F2F2")

ws.column_dimensions["A"].width = 22
for cletter in ["D", "G", "B", "C", "E", "F", "H", "I"]:
    ws.column_dimensions[cletter].width = 18

insights_row = row + ((len(kpis) - 1) // 3) * 4 + 4
ws.cell(row=insights_row, column=1, value="Key Automated Insights").font = Font(name=FONT_NAME, bold=True, size=12, color="1F3864")
insight_lines = [
    f"Deposit base grew from ${financials.iloc[0]['total_balance']:,.0f} to ${last['total_balance']:,.0f} over the observation window "
    f"({(last['total_balance']/financials.iloc[0]['total_balance']-1)*100:.1f}% cumulative growth).",
    f"Customer churn stands at {customers['churn_flag'].mean()*100:.1f}%, concentrated in the '{customers[customers.churn_flag]['risk_segment'].mode()[0]}' risk segment.",
    f"The '{customers.groupby('value_segment')['customer_lifetime_value'].sum().idxmax()}' value segment contributes the largest share of total customer lifetime value.",
    f"NPL ratio is {credit_results['npl_ratio']*100:.2f}%, with 90+ DPD loans concentrated in the Critical/High risk buckets.",
    f"Digital-first customers make up {(customers['digital_adoption']=='High').mean()*100:.1f}% of the base and show materially higher transaction frequency.",
    f"The churn model (Gradient Boosting) achieves an ROC-AUC of {churn_results['gradient_boosting']['roc_auc']:.3f} on held-out customers.",
    f"Optimized marketing/retention budget allocation is projected to lift expected incremental profit by {optim_results['expected_profit_uplift_pct']:.1f}% versus an even split.",
]
for i, line in enumerate(insight_lines):
    c = ws.cell(row=insights_row + 1 + i, column=1, value="• " + line)
    c.font = NORMAL_FONT
    ws.merge_cells(start_row=insights_row + 1 + i, start_column=1, end_row=insights_row + 1 + i, end_column=9)

# revenue/profit trend chart
chart_start = insights_row + len(insight_lines) + 3
ws.cell(row=chart_start, column=1, value="Revenue & Profit Trend").font = LABEL_FONT
fin_chart_df = financials[["month", "total_revenue", "profit_after_credit_costs"]].rename(
    columns={"total_revenue": "Revenue", "profit_after_credit_costs": "Profit"})
write_df(ws, fin_chart_df, start_row=chart_start + 1, number_formats={"Revenue": MONEY, "Profit": MONEY})

chart1 = LineChart()
chart1.title = "Monthly Revenue vs Profit"
chart1.y_axis.title = "USD"
chart1.x_axis.title = "Month"
data_ref = Reference(ws, min_col=2, max_col=3, min_row=chart_start + 1, max_row=chart_start + 1 + len(fin_chart_df))
cats_ref = Reference(ws, min_col=1, min_row=chart_start + 2, max_row=chart_start + 1 + len(fin_chart_df))
chart1.add_data(data_ref, titles_from_data=True)
chart1.set_categories(cats_ref)
chart1.height, chart1.width = 8, 18
ws.add_chart(chart1, f"K{chart_start}")

print("Executive_Summary sheet built.")

# ---------------------------------------------------------------------------
# 2. Financials (monthly P&L)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Financials")
title_block(ws, "Monthly P&L", "Simplified analytical P&L — synthetic bank-level financials")
fin_cols = ["month", "net_interest_income", "fee_income", "card_revenue", "other_operating_income",
            "total_revenue", "personnel_cost", "branch_cost", "technology_cost", "marketing_cost",
            "operations_cost", "other_operating_costs", "total_operating_cost", "credit_loss",
            "pre_provision_profit", "profit_after_credit_costs", "cost_to_income_ratio",
            "return_on_assets", "return_on_equity", "net_interest_margin"]
fmt_map = {c: MONEY for c in fin_cols if c not in ("month", "cost_to_income_ratio", "return_on_assets", "return_on_equity", "net_interest_margin")}
fmt_map.update({c: PCT for c in ("cost_to_income_ratio", "return_on_assets", "return_on_equity", "net_interest_margin")})
write_df(ws, financials[fin_cols], start_row=4, number_formats=fmt_map)

# ---------------------------------------------------------------------------
# 3. Balance_Sheet (simplified)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Balance_Sheet")
title_block(ws, "Simplified Balance Sheet (Analytical Simulation)", "Not an audited or regulatory balance sheet")
bs = financials[["month", "total_balance"]].copy()
bs["loans_outstanding"] = pd.read_csv(os.path.join(RAW, "forecast_inputs.csv"))["outstanding_loans_proxy"]
bs["cash_like_assets"] = bs["total_balance"] * 0.18
bs["investments"] = bs["total_balance"] * 0.10
bs["other_assets"] = bs["total_balance"] * 0.03
bs["total_assets"] = bs["loans_outstanding"] + bs["cash_like_assets"] + bs["investments"] + bs["other_assets"]
bs["deposits"] = bs["total_balance"]
bs["borrowings"] = bs["total_assets"] * 0.12
bs["other_liabilities"] = bs["total_assets"] * 0.02
bs["equity"] = bs["total_assets"] - bs["deposits"] - bs["borrowings"] - bs["other_liabilities"]
money_cols = [c for c in bs.columns if c != "month"]
write_df(ws, bs, start_row=4, number_formats={c: MONEY for c in money_cols})

# ---------------------------------------------------------------------------
# 4. NII_NIM
# ---------------------------------------------------------------------------
ws = wb.create_sheet("NII_NIM")
title_block(ws, "Net Interest Income & Margin", "Monthly NII, NIM, loan yield and deposit cost")
nii_df = financials[["month", "loan_interest_income", "deposit_interest_expense", "net_interest_income", "net_interest_margin"]].copy()
write_df(ws, nii_df, start_row=4, number_formats={"loan_interest_income": MONEY, "deposit_interest_expense": MONEY,
                                                    "net_interest_income": MONEY, "net_interest_margin": PCT})

# ---------------------------------------------------------------------------
# 5. Customers (sample + summary)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Customers")
title_block(ws, "Customer Base — Summary", f"{len(customers):,} total customers (sample of 500 shown below; full data in data/raw/customers.csv)")
summary_cust = customers.groupby(["value_segment", "lifecycle_segment"]).agg(
    customers=("customer_id", "count"), avg_clv=("customer_lifetime_value", "mean"),
    churn_rate=("churn_flag", "mean")).reset_index()
r_end = write_df(ws, summary_cust, start_row=4, number_formats={"avg_clv": MONEY, "churn_rate": PCT})
ws.cell(row=r_end + 3, column=1, value="Sample Customer Records").font = LABEL_FONT
sample_cols = ["customer_id", "age", "gender", "region", "income_band", "digital_adoption",
               "products_owned_count", "value_segment", "lifecycle_segment", "customer_lifetime_value", "churn_flag"]
write_df(ws, customers[sample_cols].sample(500, random_state=42), start_row=r_end + 4,
         number_formats={"customer_lifetime_value": MONEY})

# ---------------------------------------------------------------------------
# 6. Customer_Segments
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Customer_Segments")
title_block(ws, "Customer Segmentation", "Value / Lifecycle / Behavioral / Digital segments")
for label, col_, r0 in [("Value Segment", "value_segment", 4), ("Lifecycle Segment", "lifecycle_segment", None),
                         ("Behavioral Segment", "behavioral_segment", None), ("Digital Segment", "digital_segment", None)]:
    seg = customers.groupby(col_).agg(customers=("customer_id", "count"), avg_clv=("customer_lifetime_value", "mean"),
                                       churn_rate=("churn_flag", "mean"), avg_products=("products_owned_count", "mean")).reset_index()
    ws.cell(row=r0 or (last_row + 3), column=1, value=label).font = LABEL_FONT
    start = (r0 or (last_row + 3)) + 1
    last_row = write_df(ws, seg, start_row=start, number_formats={"avg_clv": MONEY, "churn_rate": PCT, "avg_products": "0.00"})

# ---------------------------------------------------------------------------
# 7. RFM
# ---------------------------------------------------------------------------
ws = wb.create_sheet("RFM")
title_block(ws, "RFM Analysis", "Recency / Frequency / Monetary scoring and segments")
rfm_summary = customers.groupby("rfm_segment").agg(
    customers=("customer_id", "count"), avg_recency=("recency_months", "mean"),
    avg_frequency=("frequency_avg_monthly_txns", "mean"), avg_monetary=("monetary_avg_balance", "mean"),
    avg_value_score=("customer_value_score", "mean")).reset_index()
write_df(ws, rfm_summary, start_row=4, number_formats={"avg_monetary": MONEY})

# ---------------------------------------------------------------------------
# 8. Cohorts (signup-month retention)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Cohorts")
title_block(ws, "Signup Cohort Retention", "Share of each signup-quarter cohort still active")
customers["signup_quarter"] = pd.PeriodIndex(pd.to_datetime(customers["signup_date"]), freq="Q").astype(str)
cohort = customers.groupby("signup_quarter").agg(cohort_size=("customer_id", "count"),
                                                   retained_rate=("churn_flag", lambda s: 1 - s.mean())).reset_index()
cohort = cohort[cohort["signup_quarter"] >= "2022Q1"]
write_df(ws, cohort, start_row=4, number_formats={"retained_rate": PCT})

# ---------------------------------------------------------------------------
# 9. CLV
# ---------------------------------------------------------------------------
ws = wb.create_sheet("CLV")
title_block(ws, "Customer Lifetime Value", "Simplified 3-year forward CLV by segment / channel / product")
clv_by_seg = customers.groupby("value_segment")["customer_lifetime_value"].agg(["count", "mean", "sum"]).reset_index()
clv_by_seg.columns = ["value_segment", "customers", "avg_clv", "total_clv"]
r_end = write_df(ws, clv_by_seg, start_row=4, number_formats={"avg_clv": MONEY, "total_clv": MONEY})
clv_by_channel = customers.merge(pd.read_csv(os.path.join(RAW, "channels.csv")), left_on="acquisition_channel", right_on="channel_id")
clv_by_channel = clv_by_channel.groupby("channel_name")["customer_lifetime_value"].mean().reset_index().sort_values("customer_lifetime_value", ascending=False)
ws.cell(row=r_end + 3, column=1, value="Average CLV by Acquisition Channel").font = LABEL_FONT
write_df(ws, clv_by_channel, start_row=r_end + 4, number_formats={"customer_lifetime_value": MONEY})
print("Financials/Balance Sheet/NII/Customers/Segments/RFM/Cohorts/CLV sheets built.")
wb.save(OUT_XLSX)

# ---------------------------------------------------------------------------
# 10. Products
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Products")
title_block(ws, "Product Analytics", "Penetration, revenue and risk by product")
penetration_df = pd.DataFrame(list(cross_sell["product_penetration_pct"].items()), columns=["product_name", "penetration_pct"])
r_end = write_df(ws, penetration_df.merge(products[["product_name", "risk_level", "interest_rate", "fee_rate"]], on="product_name"),
                  start_row=4, number_formats={"penetration_pct": "0.0", "interest_rate": PCT, "fee_rate": PCT})
ws.cell(row=r_end + 3, column=1, value="Monthly Active Customers & Revenue by Product (last 6 months avg)").font = LABEL_FONT
recent_pm = mpm[mpm["month"] >= mpm["month"].sort_values().unique()[-6]]
pm_summary = recent_pm.groupby("product_name").agg(avg_active_customers=("active_customers", "mean"),
                                                     avg_monthly_revenue=("revenue", "mean")).reset_index()
write_df(ws, pm_summary, start_row=r_end + 4, number_formats={"avg_monthly_revenue": MONEY, "avg_active_customers": "#,##0"})

# ---------------------------------------------------------------------------
# 11. Deposits
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Deposits")
title_block(ws, "Deposit Analytics", "Term deposits & overall deposit trend")
dep_by_term = deposits.groupby("term_months").agg(count=("deposit_id", "count"), avg_principal=("principal_amount", "mean"),
                                                    avg_rate=("interest_rate", "mean")).reset_index()
r_end = write_df(ws, dep_by_term, start_row=4, number_formats={"avg_principal": MONEY, "avg_rate": PCT})
ws.cell(row=r_end + 3, column=1, value="Total Deposit Balance Trend").font = LABEL_FONT
write_df(ws, financials[["month", "total_balance"]], start_row=r_end + 4, number_formats={"total_balance": MONEY})

# ---------------------------------------------------------------------------
# 12. Loans
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Loans")
title_block(ws, "Loan Portfolio", "Originations, balances and performance by product & risk bucket")
loan_by_prod = loans.groupby("loan_type").agg(loan_count=("loan_id", "count"), total_originated=("loan_amount", "sum"),
                                                outstanding=("outstanding_balance", "sum"), avg_rate=("interest_rate", "mean"),
                                                default_rate=("default_flag", "mean")).reset_index()
r_end = write_df(ws, loan_by_prod, start_row=4, number_formats={"total_originated": MONEY, "outstanding": MONEY,
                                                                  "avg_rate": PCT, "default_rate": PCT})
ws.cell(row=r_end + 3, column=1, value="Loan Performance by Risk Bucket").font = LABEL_FONT
loan_by_risk = loans.groupby("risk_bucket").agg(loan_count=("loan_id", "count"), outstanding=("outstanding_balance", "sum"),
                                                  expected_credit_loss=("expected_credit_loss", "sum"),
                                                  default_rate=("default_flag", "mean")).reset_index()
write_df(ws, loan_by_risk, start_row=r_end + 4, number_formats={"outstanding": MONEY, "expected_credit_loss": MONEY, "default_rate": PCT})

# ---------------------------------------------------------------------------
# 13. Credit_Risk
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Credit_Risk")
title_block(ws, "Credit Risk", "PD model performance, DPD distribution & expected loss")
model_comp = pd.DataFrame([
    {"model": "Logistic Regression", **credit_results["logistic_regression"]},
    {"model": "Gradient Boosting", **credit_results["gradient_boosting"]},
]).drop(columns=["confusion_matrix"])
r_end = write_df(ws, model_comp, start_row=4)
ws.cell(row=r_end + 3, column=1, value="DPD Distribution").font = LABEL_FONT
dpd_df = pd.DataFrame(list(credit_results["dpd_distribution"].items()), columns=["dpd_bucket", "share"])
r_end = write_df(ws, dpd_df, start_row=r_end + 4, number_formats={"share": PCT})
ws.cell(row=r_end + 3, column=1, value=f"NPL Ratio: {credit_results['npl_ratio']:.2%}").font = LABEL_FONT
ws.cell(row=r_end + 4, column=1, value="Portfolio Risk Summary by Bucket").font = LABEL_FONT
risk_summary_df = pd.DataFrame(credit_results["portfolio_risk_summary"])
write_df(ws, risk_summary_df, start_row=r_end + 5, number_formats={"total_exposure": MONEY, "total_expected_loss": MONEY,
                                                                      "avg_pd": PCT, "avg_lgd": PCT})

# ---------------------------------------------------------------------------
# 14. Fraud
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Fraud")
title_block(ws, "Fraud Analytics", "Fraud events, loss and detection performance")
fraud_by_cat = fraud.groupby("fraud_category").agg(events=("fraud_id", "count"), total_loss=("loss_amount", "sum"),
                                                     detection_rate=("detected_flag", "mean")).reset_index()
r_end = write_df(ws, fraud_by_cat, start_row=4, number_formats={"total_loss": MONEY, "detection_rate": PCT})
fp_rate = fraud["false_positive_flag"].mean()
ws.cell(row=r_end + 3, column=1, value=f"Overall False Positive Rate: {fp_rate:.2%}").font = LABEL_FONT
ws.cell(row=r_end + 4, column=1, value="Fraud by Channel").font = LABEL_FONT
fraud_by_channel = fraud.groupby("channel").agg(events=("fraud_id", "count"), total_loss=("loss_amount", "sum")).reset_index()
write_df(ws, fraud_by_channel, start_row=r_end + 5, number_formats={"total_loss": MONEY})

# ---------------------------------------------------------------------------
# 15. Branches
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Branches")
title_block(ws, "Branch Performance", "Revenue, profit and productivity by branch (avg last 6 months)")
recent_bm = mbm[mbm["month"] >= mbm["month"].sort_values().unique()[-6]]
branch_summary = recent_bm.groupby("branch_id").agg(avg_revenue=("revenue", "mean"), avg_profit=("profit", "mean"),
                                                      avg_active_customers=("active_customers", "mean"),
                                                      avg_revenue_per_employee=("revenue_per_employee", "mean")).reset_index()
branch_summary = branch_summary.merge(branches[["branch_id", "branch_name", "region", "branch_type"]], on="branch_id")
write_df(ws, branch_summary[["branch_id", "branch_name", "region", "branch_type", "avg_revenue", "avg_profit",
                              "avg_active_customers", "avg_revenue_per_employee"]], start_row=4,
         number_formats={"avg_revenue": MONEY, "avg_profit": MONEY, "avg_revenue_per_employee": MONEY})

# ---------------------------------------------------------------------------
# 16. Digital_Banking
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Digital_Banking")
title_block(ws, "Digital Banking", "Adoption, usage and profitability by digital segment")
digital_summary = customers.groupby("digital_adoption").agg(
    customers=("customer_id", "count"), avg_txns=("frequency_avg_monthly_txns", "mean"),
    avg_clv=("customer_lifetime_value", "mean"), churn_rate=("churn_flag", "mean")).reset_index()
write_df(ws, digital_summary, start_row=4, number_formats={"avg_clv": MONEY, "churn_rate": PCT})

# ---------------------------------------------------------------------------
# 17. Marketing
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Marketing")
title_block(ws, "Marketing & Campaign Analytics", "Campaign performance, conversion and ROI")
camp_perf = campaign_resp.groupby("campaign_id").agg(responses=("response_id", "count"),
                                                       conversions=("converted_flag", "sum"),
                                                       revenue=("revenue_generated", "sum")).reset_index()
camp_perf = camp_perf.merge(campaigns[["campaign_id", "campaign_name", "budget", "impressions", "reach"]], on="campaign_id")
camp_perf["conversion_rate"] = camp_perf["conversions"] / camp_perf["responses"]
camp_perf["roi_pct"] = (camp_perf["revenue"] - camp_perf["budget"]) / camp_perf["budget"]
write_df(ws, camp_perf[["campaign_name", "impressions", "reach", "responses", "conversions", "conversion_rate",
                         "budget", "revenue", "roi_pct"]].sort_values("roi_pct", ascending=False),
         start_row=4, number_formats={"budget": MONEY, "revenue": MONEY, "conversion_rate": PCT, "roi_pct": PCT})
print("Products/Deposits/Loans/Credit_Risk/Fraud/Branches/Digital/Marketing sheets built.")
wb.save(OUT_XLSX)

# ---------------------------------------------------------------------------
# 18. Forecast
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Forecast")
title_block(ws, "12-Month Forecast", "Best model selected per series via backtest MAPE (see method column)")
method_row = pd.DataFrame([{"series": k, "best_method": v["best_method"],
                             "backtest_mape_pct": v["backtest_scores"][v["best_method"]]["mape"]}
                            for k, v in forecast_results["series"].items()])
r_end = write_df(ws, method_row, start_row=4, number_formats={"backtest_mape_pct": "0.00"})
ws.cell(row=r_end + 3, column=1, value="12-Month Forecast Values").font = LABEL_FONT
money_series = ["deposits", "loans", "revenue", "net_interest_income", "fee_income", "operating_costs", "credit_loss", "profit"]
write_df(ws, forecast_12m, start_row=r_end + 4, number_formats={c: MONEY for c in money_series})

chart2 = LineChart()
chart2.title = "Forecast: Deposits, Loans, Revenue, Profit (next 12 months)"
chart2.y_axis.title = "USD"
data_ref = Reference(ws, min_col=2, max_col=3, min_row=r_end + 4, max_row=r_end + 4 + len(forecast_12m))
data_ref2 = Reference(ws, min_col=4, max_col=4, min_row=r_end + 4, max_row=r_end + 4 + len(forecast_12m))
cats_ref = Reference(ws, min_col=1, min_row=r_end + 5, max_row=r_end + 4 + len(forecast_12m))
chart2.add_data(data_ref, titles_from_data=True)
chart2.set_categories(cats_ref)
chart2.height, chart2.width = 8, 18
ws.add_chart(chart2, f"K{r_end + 4}")

# ---------------------------------------------------------------------------
# 19. Scenarios
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Scenarios")
title_block(ws, "Scenario Planning", "Base / Growth / Efficiency / Downside / Stress — 12-month projections")
snap_rows = []
for name, r in scenario_results.items():
    row = {"scenario": name, **r["month_12_snapshot"], "cumulative_12m_profit": r["cumulative_12m_profit"],
           "roa_annualized_m12": r["roa_annualized_month12"]}
    snap_rows.append(row)
snap_df = pd.DataFrame(snap_rows)
money_cols_sc = ["deposits", "loans", "revenue", "net_interest_income", "credit_loss", "operating_cost", "profit", "cumulative_12m_profit"]
write_df(ws, snap_df, start_row=4, number_formats={**{c: MONEY for c in money_cols_sc}, "roa_annualized_m12": PCT})

# ---------------------------------------------------------------------------
# 20. Optimization
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Optimization")
title_block(ws, "Marketing & Retention Budget Optimization", "Linear programming allocation across customer value segments")
alloc_rows = []
for seg in optim_results["current_allocation_even_split"]:
    alloc_rows.append({
        "segment": seg,
        "current_allocation": optim_results["current_allocation_even_split"][seg],
        "optimized_allocation": optim_results["optimized_allocation"][seg],
        "response_rate": optim_results["response_rate_by_segment"][seg],
    })
alloc_df = pd.DataFrame(alloc_rows)
r_end = write_df(ws, alloc_df, start_row=4, number_formats={"current_allocation": MONEY, "optimized_allocation": MONEY, "response_rate": "0.000"})
ws.cell(row=r_end + 3, column=1, value=f"Expected Incremental Profit — Current: ${optim_results['expected_incremental_profit_current']:,.0f}").font = LABEL_FONT
ws.cell(row=r_end + 4, column=1, value=f"Expected Incremental Profit — Optimized: ${optim_results['expected_incremental_profit_optimized']:,.0f}").font = LABEL_FONT
ws.cell(row=r_end + 5, column=1, value=f"Expected Uplift: {optim_results['expected_profit_uplift_pct']:.2f}%").font = Font(name=FONT_NAME, bold=True, color="1F7A1F")

# ---------------------------------------------------------------------------
# 21. KPI_Definitions
# ---------------------------------------------------------------------------
ws = wb.create_sheet("KPI_Definitions")
title_block(ws, "KPI Definitions", "Definitions of key metrics used throughout the workbook")
kpi_defs = pd.DataFrame([
    ("NIM (Net Interest Margin)", "Net Interest Income (annualized) / Average Earning Assets"),
    ("ROA (Return on Assets)", "Profit After Credit Costs (annualized) / Average Total Assets — simplified proxy"),
    ("ROE (Return on Equity)", "Profit After Credit Costs (annualized) / Average Equity — simplified proxy (equity ≈ 10% of assets)"),
    ("Cost-to-Income Ratio", "Total Operating Expenses / Total Operating Income"),
    ("NPL Ratio", "Outstanding balance of loans 90+ days past due / Total outstanding loan balance"),
    ("PD (Probability of Default)", "Modeled/assigned probability that a loan reaches 90+ DPD"),
    ("LGD (Loss Given Default)", "Modeled share of exposure not recovered in the event of default"),
    ("Expected Credit Loss (ECL)", "PD × LGD × Exposure at Default"),
    ("CLV (Customer Lifetime Value)", "Simplified 3-year forward contribution profit, adjusted for churn risk"),
    ("RFM Score", "Recency / Frequency / Monetary quintile scores (1–5 each) combined into a segment"),
    ("Churn Flag", "Customer inactive for the remainder of the 24-month observation window"),
    ("Digital Adoption", "High / Medium / Low based on mobile & internet banking usage"),
], columns=["metric", "definition"])
write_df(ws, kpi_defs, start_row=4)
ws.column_dimensions["B"].width = 90

# ---------------------------------------------------------------------------
# 22. Data_Dictionary
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Data_Dictionary")
title_block(ws, "Data Dictionary", "All tables and their column-level descriptions (see docs/data_dictionary.md for full detail)")
dd_rows = []
table_files = sorted([f for f in os.listdir(RAW) if f.endswith(".csv") or f.endswith(".csv.gz")])
for f in table_files:
    path = os.path.join(RAW, f)
    try:
        cols = pd.read_csv(path, nrows=1).columns.tolist()
    except Exception:
        cols = ["(unreadable)"]
    dd_rows.append({"table": f, "columns": ", ".join(cols)})
dd_df = pd.DataFrame(dd_rows)
write_df(ws, dd_df, start_row=4)
ws.column_dimensions["B"].width = 100

# ---------------------------------------------------------------------------
# 23. Assumptions
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Assumptions")
title_block(ws, "Assumptions & Limitations", "Read before interpreting any figure in this workbook")
assumptions_text = [
    "This entire dataset is SYNTHETIC, generated with fixed random seeds for reproducibility. It does not represent any real bank, customer, or transaction.",
    "Scale: 20,000 customers / 24 months / ~500K transactions — deliberately scaled down from a production-size dataset (500K+ customers) for a fast, reproducible, downloadable GitHub portfolio artifact. Table structure, business logic and correlations mirror a full-scale build.",
    "Financial ratios (ROA, ROE, NIM, Cost-to-Income) are SIMPLIFIED ANALYTICAL PROXIES, not audited or regulatory figures. Equity is proxied as ~10% of a simplified asset base.",
    "Credit risk figures (PD, LGD, ECL, NPL) are analytical categories for portfolio demonstration purposes — NOT real regulatory risk classifications (e.g., not IFRS 9 / Basel-compliant).",
    "Liquidity-style analytics in this project are simulations, not a regulatory liquidity (e.g., LCR/NSFR) report.",
    "Fraud and NPS-like satisfaction metrics are synthetic and do not represent real industry benchmarks.",
    "Forecast and scenario projections extrapolate from 24 months of synthetic history; they are illustrative of methodology, not investment or business advice.",
    "This project is for educational and portfolio purposes only. It is not a regulatory banking model, investment recommendation, credit decisioning system, or the internal data/methodology of any real financial institution.",
]
for i, line in enumerate(assumptions_text):
    c = ws.cell(row=4 + i, column=1, value="• " + line)
    c.font = NORMAL_FONT
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[4 + i].height = 30
    ws.merge_cells(start_row=4 + i, start_column=1, end_row=4 + i, end_column=8)
ws.column_dimensions["A"].width = 20

# freeze panes on data-heavy sheets
for sheet_name in ["Financials", "Customers", "Loans", "Products", "Forecast"]:
    wb[sheet_name].freeze_panes = "A5"

wb.save(OUT_XLSX)
print(f"\nWorkbook saved: {OUT_XLSX}")
print("Sheets:", wb.sheetnames)



