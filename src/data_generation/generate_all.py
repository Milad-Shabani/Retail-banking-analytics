"""
Retail Banking Analytics — Synthetic Data Generator
-----------------------------------------------------
Generates an internally-consistent synthetic dataset for a generic retail
bank. Scale is deliberately calibrated for a public GitHub portfolio
repository (fast to regenerate, reasonable repo size) while preserving the
full table structure, business logic and correlations of a much larger
production-scale dataset. See README.md / docs/assumptions.md for the
scaling rationale.

Deterministic: everything is derived from SEED = 42.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

SEED = 42
rng = np.random.default_rng(SEED)

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
os.makedirs(OUT, exist_ok=True)

N_CUSTOMERS = 20_000
N_MONTHS = 24
START_MONTH = pd.Period("2023-01", freq="M")
MONTHS = pd.period_range(START_MONTH, periods=N_MONTHS, freq="M")
MONTH_DATES = [m.to_timestamp(how="end").normalize() for m in MONTHS]

N_BRANCHES = 25
N_REGIONS = 12
N_CHANNELS = 12
N_PRODUCTS = 12

REGIONS = [f"Region-{i+1:02d}" for i in range(N_REGIONS)]
CITIES_PER_REGION = 3
CITIES = [f"{r}-City-{c+1}" for r in REGIONS for c in range(CITIES_PER_REGION)]

def save(df, name):
    path = os.path.join(OUT, name)
    df.to_csv(path, index=False)
    print(f"  wrote {name:35s} {len(df):>10,} rows  {df.shape[1]:>3} cols")

print("== Retail Banking Analytics: synthetic data generation ==")
print(f"Seed={SEED}  Customers={N_CUSTOMERS:,}  Months={N_MONTHS}  Branches={N_BRANCHES}")

# ---------------------------------------------------------------------------
# 1. BRANCHES
# ---------------------------------------------------------------------------
branch_region = rng.choice(REGIONS, N_BRANCHES)
branch_city = [rng.choice([c for c in CITIES if c.startswith(r)]) for r in branch_region]
branches = pd.DataFrame({
    "branch_id": [f"BR{i+1:03d}" for i in range(N_BRANCHES)],
    "branch_name": [f"Branch {i+1:03d}" for i in range(N_BRANCHES)],
    "region": branch_region,
    "city": branch_city,
    "branch_type": rng.choice(["Flagship", "Standard", "Digital-Light", "Rural"], N_BRANCHES, p=[0.08, 0.62, 0.2, 0.1]),
    "open_date": pd.to_datetime("2010-01-01") + pd.to_timedelta(rng.integers(0, 4000, N_BRANCHES), unit="D"),
    "employee_count": rng.integers(6, 40, N_BRANCHES),
})
save(branches, "branches.csv")

# ---------------------------------------------------------------------------
# 2. EMPLOYEES
# ---------------------------------------------------------------------------
emp_rows = []
eid = 1
for _, b in branches.iterrows():
    for _ in range(int(b["employee_count"])):
        emp_rows.append({
            "employee_id": f"EMP{eid:05d}",
            "branch_id": b["branch_id"],
            "role": rng.choice(["Teller", "Personal Banker", "Relationship Manager", "Branch Manager", "Credit Officer"],
                                p=[0.35, 0.30, 0.18, 0.07, 0.10]),
            "hire_date": pd.to_datetime("2012-01-01") + pd.to_timedelta(rng.integers(0, 4500), unit="D"),
            "performance_score": np.round(rng.normal(75, 12), 1),
        })
        eid += 1
employees = pd.DataFrame(emp_rows)
save(employees, "employees.csv")

# ---------------------------------------------------------------------------
# 3. CHANNELS
# ---------------------------------------------------------------------------
channel_names = ["Branch Walk-in", "Digital Onboarding", "Mobile App Referral", "Call Center",
                  "Partner Referral", "Employer Payroll Program", "Online Ad Campaign",
                  "Social Media Campaign", "Aggregator Website", "Existing Customer Referral",
                  "Student Program", "ATM Kiosk Sign-up"]
channels = pd.DataFrame({
    "channel_id": [f"CH{i+1:02d}" for i in range(N_CHANNELS)],
    "channel_name": channel_names,
    "channel_type": ["Physical", "Digital", "Digital", "Physical", "Partner", "Partner",
                      "Digital", "Digital", "Digital", "Referral", "Partner", "Physical"],
    "avg_acquisition_cost": np.round(rng.uniform(15, 120, N_CHANNELS), 2),
})
save(channels, "channels.csv")

# ---------------------------------------------------------------------------
# 4. PRODUCTS
# ---------------------------------------------------------------------------
products_def = [
    ("PRD01", "Checking Account", "Transaction", 0.001, 0.0, 3.0, 8, 6, "Low"),
    ("PRD02", "Savings Account", "Deposit", 0.015, 0.0, 0.0, 6, 4, "Low"),
    ("PRD03", "Credit Card", "Card", 0.24, 0.02, 0.0, 45, 20, "High"),
    ("PRD04", "Debit Card", "Card", 0.0, 0.005, 0.0, 5, 3, "Low"),
    ("PRD05", "Personal Loan", "Loan", 0.16, 0.01, 0.0, 60, 15, "High"),
    ("PRD06", "Auto Loan", "Loan", 0.11, 0.008, 0.0, 70, 18, "Medium"),
    ("PRD07", "Mortgage", "Loan", 0.085, 0.005, 0.0, 150, 30, "Medium"),
    ("PRD08", "Consumer Loan", "Loan", 0.18, 0.01, 0.0, 40, 14, "High"),
    ("PRD09", "Term Deposit", "Deposit", 0.06, 0.0, 0.0, 10, 5, "Low"),
    ("PRD10", "Investment Account", "Investment", 0.0, 0.012, 0.0, 55, 12, "Medium"),
    ("PRD11", "Overdraft Facility", "Credit", 0.20, 0.015, 2.0, 20, 8, "High"),
    ("PRD12", "Bancassurance", "Insurance", 0.0, 0.10, 0.0, 30, 10, "Low"),
]
products = pd.DataFrame(products_def, columns=[
    "product_id", "product_name", "product_category", "interest_rate", "fee_rate",
    "monthly_fee", "acquisition_cost", "operating_cost", "risk_level"])
save(products, "products.csv")

print("Base reference tables complete.")

# ---------------------------------------------------------------------------
# 5. CUSTOMERS
# ---------------------------------------------------------------------------
cid = np.array([f"CUST{i+1:06d}" for i in range(N_CUSTOMERS)])

signup_days_ago = rng.integers(30, 365 * 9, N_CUSTOMERS)  # up to 9 years tenure
signup_date = pd.to_datetime("2024-12-31") - pd.to_timedelta(signup_days_ago, unit="D")
signup_date = pd.Series(signup_date).clip(upper=pd.to_datetime("2024-11-30"))

birth_year = rng.integers(1950, 2005, N_CUSTOMERS)
age = 2026 - birth_year
age_band = pd.cut(age, bins=[17, 25, 35, 45, 55, 65, 120],
                   labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66+"])

gender = rng.choice(["Male", "Female"], N_CUSTOMERS, p=[0.52, 0.48])
region = rng.choice(REGIONS, N_CUSTOMERS)
city = np.array([rng.choice([c for c in CITIES if c.startswith(r)]) for r in region])
branch_id = rng.choice(branches["branch_id"], N_CUSTOMERS)

employment_status = rng.choice(
    ["Employed", "Self-Employed", "Unemployed", "Retired", "Student"],
    N_CUSTOMERS, p=[0.58, 0.18, 0.06, 0.11, 0.07])
occupation_group = rng.choice(
    ["Professional", "Manager", "Clerical", "Manual Labor", "Public Sector", "Business Owner", "Other"],
    N_CUSTOMERS, p=[0.22, 0.13, 0.18, 0.17, 0.12, 0.10, 0.08])

# income correlated with age, employment & occupation
base_income = rng.lognormal(mean=8.6, sigma=0.55, size=N_CUSTOMERS)  # ~ thousands / year
income_mult = np.select(
    [employment_status == "Unemployed", employment_status == "Student", employment_status == "Retired",
     occupation_group.astype(str) == "Professional", occupation_group.astype(str) == "Business Owner"],
    [0.15, 0.2, 0.55, 1.5, 1.7], default=1.0)
age_mult = np.clip((age - 18) / 25, 0.4, 1.6)
annual_income = np.round(base_income * income_mult * age_mult, -2)
annual_income = np.clip(annual_income, 1200, 400_000)
income_band = pd.cut(annual_income, bins=[0, 15000, 30000, 55000, 90000, 150000, np.inf],
                      labels=["<15K", "15K-30K", "30K-55K", "55K-90K", "90K-150K", "150K+"])

education_level = rng.choice(["High School", "Diploma", "Bachelor", "Master", "PhD"],
                              N_CUSTOMERS, p=[0.30, 0.20, 0.32, 0.15, 0.03])
marital_status = rng.choice(["Single", "Married", "Divorced", "Widowed"], N_CUSTOMERS, p=[0.38, 0.48, 0.10, 0.04])
customer_type = rng.choice(["Individual", "Small Business", "Corporate"], N_CUSTOMERS, p=[0.90, 0.08, 0.02])

acquisition_channel = rng.choice(channels["channel_id"], N_CUSTOMERS)
acquisition_campaign_flag = rng.random(N_CUSTOMERS) < 0.35

tenure_years = (pd.to_datetime("2024-12-31") - signup_date).dt.days / 365.25

# digital adoption correlated with age (younger => higher) and tenure
digital_prop = np.clip(0.95 - (age - 18) * 0.008 + rng.normal(0, 0.08, N_CUSTOMERS), 0.03, 0.97)
mobile_banking_user = rng.random(N_CUSTOMERS) < digital_prop
internet_banking_user = rng.random(N_CUSTOMERS) < np.clip(digital_prop + 0.05, 0, 0.98)
digital_adoption = np.where(mobile_banking_user & internet_banking_user, "High",
                     np.where(mobile_banking_user | internet_banking_user, "Medium", "Low"))

premium_customer_flag = (annual_income > 90000) & (rng.random(N_CUSTOMERS) < 0.6)
salary_customer_flag = (employment_status == "Employed") & (rng.random(N_CUSTOMERS) < 0.55)

# churn probability driver (used to assign churn later after behavioral sim);
# placeholder status for now, finalized after monthly simulation
customer_status = np.full(N_CUSTOMERS, "Active", dtype=object)

customers = pd.DataFrame({
    "customer_id": cid,
    "signup_date": signup_date.values,
    "birth_year": birth_year,
    "age": age,
    "age_band": age_band.astype(str),
    "gender": gender,
    "region": region,
    "city": city,
    "branch_id": branch_id,
    "employment_status": employment_status,
    "occupation_group": occupation_group,
    "income_band": income_band.astype(str),
    "annual_income": annual_income,
    "education_level": education_level,
    "marital_status": marital_status,
    "customer_type": customer_type,
    "acquisition_channel": acquisition_channel,
    "acquisition_campaign_flag": acquisition_campaign_flag,
    "relationship_start_date": signup_date.values,
    "tenure_years": np.round(tenure_years, 2),
    "digital_adoption": digital_adoption,
    "mobile_banking_user": mobile_banking_user,
    "internet_banking_user": internet_banking_user,
    "premium_customer_flag": premium_customer_flag,
    "salary_customer_flag": salary_customer_flag,
    "customer_status": customer_status,
})
print("Customers frame constructed (pre-behavioral fields).")

# ---------------------------------------------------------------------------
# 6. BEHAVIORAL SIMULATION (monthly balance / activity / churn) — vectorized
# ---------------------------------------------------------------------------
N, M = N_CUSTOMERS, N_MONTHS

# Baseline monthly balance driven by income (deposit-heavy customers keep more)
base_balance = np.clip(annual_income / 12 * rng.uniform(0.8, 3.2, N), 50, 60000)
balance_trend = rng.normal(0.004, 0.02, N)          # slight growth/decline per month
balance_season = 0.05 * np.sin(np.linspace(0, 4 * np.pi, M))  # seasonal deposit pattern

# activity level (transactions/month) correlated with digital adoption
digital_score = np.select([digital_adoption == "High", digital_adoption == "Medium"], [1.0, 0.6], default=0.25)
base_txn_rate = np.clip(rng.normal(0.9, 0.6, N) * (0.6 + 0.8 * digital_score), 0.1, 5)

# churn: ~16% of customers churn at some point during the window, hazard increases
# for low-engagement / low-tenure / unemployed customers
churn_risk_score = (
    0.30 * (employment_status == "Unemployed").astype(float)
    + 0.15 * (digital_adoption == "Low").astype(float)
    + 0.20 * (tenure_years.values < 1).astype(float)
    + 0.10 * (age_band.astype(str) == "18-25").astype(float)
    + rng.normal(0, 0.12, N)
)
churn_prob_total = np.clip(0.16 + 0.35 * (churn_risk_score - churn_risk_score.mean()), 0.02, 0.85)
will_churn = rng.random(N) < churn_prob_total
churn_month_idx = np.where(will_churn, rng.integers(6, M, N), M + 5)  # month index (0-based) of churn; non-churners far beyond range

balance_matrix = np.zeros((N, M))
txn_count_matrix = np.zeros((N, M), dtype=int)
active_matrix = np.ones((N, M), dtype=bool)

for m in range(M):
    months_since_start = m
    growth = (1 + balance_trend) ** months_since_start
    season = 1 + balance_season[m]
    noise = rng.normal(1, 0.06, N)
    bal = base_balance * growth * season * noise

    # pre-churn decay: balances taper down over the 4 months before churn
    months_to_churn = churn_month_idx - m
    decay = np.where((months_to_churn >= 0) & (months_to_churn <= 4), np.clip(months_to_churn / 4, 0.05, 1), 1.0)
    bal = bal * decay
    bal = np.where(m >= churn_month_idx, 0.0, bal)
    bal = np.clip(bal, 0, None)
    balance_matrix[:, m] = bal

    txns = rng.poisson(np.clip(base_txn_rate * season * decay, 0.05, None))
    txns = np.where(m >= churn_month_idx, 0, txns)
    txn_count_matrix[:, m] = txns

    active_matrix[:, m] = (m < churn_month_idx)

churned_final = ~active_matrix[:, -1]
customers["churn_flag"] = churned_final
customers["customer_status"] = np.where(churned_final, "Churned",
                                  np.where(txn_count_matrix[:, -3:].sum(axis=1) == 0, "Dormant", "Active"))

# risk segment from churn_risk_score + income (used later refined by credit risk model too)
risk_pct = pd.Series(churn_risk_score).rank(pct=True).values
risk_segment = np.select(
    [risk_pct < 0.4, risk_pct < 0.7, risk_pct < 0.88, risk_pct < 0.97],
    ["Low", "Moderate", "Elevated", "High"], default="Critical")
customers["risk_segment"] = risk_segment

avg_balance_overall = balance_matrix.mean(axis=1)
avg_txn_overall = txn_count_matrix.mean(axis=1)

print("Behavioral simulation complete (balance & activity matrices built).")

# ---------------------------------------------------------------------------
# 7. VALUE / LIFECYCLE / RFM SEGMENTATION
# ---------------------------------------------------------------------------
# Recency: months since last activity (0 = active this month)
last_active_month = np.array([np.max(np.where(active_matrix[i])[0]) if active_matrix[i].any() else -1
                               for i in range(N)])
recency_months = (M - 1) - last_active_month

frequency = avg_txn_overall
monetary = avg_balance_overall

def score_quantile(arr, ascending=True):
    ranks = pd.Series(arr).rank(pct=True).values
    q = np.digitize(ranks, [0.2, 0.4, 0.6, 0.8]) + 1
    return q if ascending else (6 - q)

r_score = score_quantile(-recency_months)  # lower recency (more recent) => higher score
f_score = score_quantile(frequency)
m_score = score_quantile(monetary)
rfm_score = r_score * 100 + f_score * 10 + m_score
customer_value_score = np.round((r_score + f_score + m_score) / 15 * 100, 1)

rfm_segment = np.select(
    [(r_score >= 4) & (f_score >= 4) & (m_score >= 4),
     (r_score >= 4) & (f_score >= 3),
     (r_score <= 2) & (f_score <= 2) & (m_score <= 2),
     (r_score <= 2),
     ],
    ["Champions", "Loyal Customers", "Lost", "At Risk"],
    default="Potential Loyalist")

value_segment = pd.cut(customer_value_score, bins=[-1, 20, 40, 60, 80, 101],
                        labels=["Mass", "Mass Affluent", "Affluent", "High Value", "Premium"]).astype(str)

lifecycle_segment = np.select(
    [customers["churn_flag"].values,
     (tenure_years.values < 0.5),
     (recency_months >= 3) & (~customers["churn_flag"].values),
     (tenure_years.values >= 0.5) & (tenure_years.values < 2),
     (tenure_years.values >= 2) & (frequency > np.median(frequency)),
     ],
    ["Churned", "New", "At Risk", "Growing", "Loyal"],
    default="Established")

behavioral_segment = np.select(
    [digital_adoption == "High",
     (digital_adoption == "Low"),
     monetary > np.quantile(monetary, 0.75),
     frequency > np.quantile(frequency, 0.75),
     ],
    ["Digital First", "Branch Dependent", "Deposit Heavy", "Transaction Heavy"],
    default="Low Engagement")

digital_segment = digital_adoption.copy()

# CLV: simplified 3-year forward NPV based on avg balance, activity, income, risk
revenue_proxy = (monetary * 0.045) + (frequency * 12 * 0.35) + (annual_income * 0.002)
cost_proxy = (monetary * 0.012) + np.select([risk_segment == "Critical", risk_segment == "High",
                                              risk_segment == "Elevated"], [0.05, 0.03, 0.015], default=0.005) * (monetary + 1000)
contribution = np.clip(revenue_proxy - cost_proxy, -500, None)
survival_years = np.clip(3 - churn_prob_total * 2.2, 0.4, 3)
clv = np.round(contribution * survival_years, 2)

customers["recency_months"] = recency_months
customers["frequency_avg_monthly_txns"] = np.round(frequency, 2)
customers["monetary_avg_balance"] = np.round(monetary, 2)
customers["r_score"] = r_score
customers["f_score"] = f_score
customers["m_score"] = m_score
customers["rfm_score"] = rfm_score
customers["rfm_segment"] = rfm_segment
customers["customer_value_score"] = customer_value_score
customers["value_segment"] = value_segment
customers["lifecycle_segment"] = lifecycle_segment
customers["behavioral_segment"] = behavioral_segment
customers["digital_segment"] = digital_segment
customers["customer_lifetime_value"] = clv

save(customers, "customers.csv")
print("Customer segmentation complete.")

# ---------------------------------------------------------------------------
# 8. CUSTOMER_PRODUCTS (product ownership) + ACCOUNTS
# ---------------------------------------------------------------------------
DEPOSIT_PRODUCTS = ["PRD01", "PRD02", "PRD09"]
CARD_PRODUCTS = ["PRD03", "PRD04"]
LOAN_PRODUCTS = ["PRD05", "PRD06", "PRD07", "PRD08", "PRD11"]
OTHER_PRODUCTS = ["PRD10", "PRD12"]

everyone_has = ["PRD01"]  # checking account is universal
cp_rows = []
n_products_owned = np.clip(rng.poisson(1.6 + digital_score * 0.8 + premium_customer_flag * 0.8, N), 0, 7)

for i in range(N):
    owned = set(everyone_has)
    k = int(n_products_owned[i])
    pool = [p for p in products["product_id"] if p not in owned]
    weights = np.array([3 if p == "PRD02" else 2 if p in CARD_PRODUCTS else 1 for p in pool], dtype=float)
    weights = weights / weights.sum()
    extra = rng.choice(pool, size=min(k, len(pool)), replace=False, p=weights)
    owned.update(extra)
    for p in owned:
        adopt_offset_days = int(rng.integers(0, max((pd.Timestamp("2024-12-31") - customers.loc[i, "signup_date"]).days, 1) + 1))
        cp_rows.append((cid[i], p, customers.loc[i, "signup_date"] + pd.Timedelta(days=adopt_offset_days)))

customer_products = pd.DataFrame(cp_rows, columns=["customer_id", "product_id", "adoption_date"])
customer_products = customer_products.merge(products[["product_id", "product_name", "product_category"]], on="product_id")
save(customer_products, "customer_products.csv")

products_per_customer = customer_products.groupby("customer_id")["product_id"].nunique()
customers["products_owned_count"] = customers["customer_id"].map(products_per_customer).fillna(1).astype(int)
customers["multi_product_flag"] = customers["products_owned_count"] > 1
save(customers, "customers.csv")  # re-save with product-ownership fields added

# ACCOUNTS: derived from deposit-type product ownership (checking/savings/term deposit)
acc_rows = []
aid = 1
for _, row in customer_products[customer_products["product_id"].isin(DEPOSIT_PRODUCTS)].iterrows():
    acc_rows.append({
        "account_id": f"ACC{aid:07d}",
        "customer_id": row["customer_id"],
        "product_id": row["product_id"],
        "account_type": row["product_name"],
        "open_date": row["adoption_date"],
        "status": "Open",
    })
    aid += 1
accounts = pd.DataFrame(acc_rows)
# mark some accounts closed for churned customers
churn_map = customers.set_index("customer_id")["churn_flag"]
accounts["status"] = np.where(accounts["customer_id"].map(churn_map).fillna(False), "Closed", "Open")
save(accounts, "accounts.csv")
print(f"Accounts created: {len(accounts):,}")

# ---------------------------------------------------------------------------
# 9. MONTHLY_CUSTOMER_METRICS (from behavioral matrices)
# ---------------------------------------------------------------------------
month_labels = [str(m) for m in MONTHS]
mcm_rows = {
    "customer_id": np.repeat(cid, M),
    "month": np.tile(month_labels, N),
    "month_end_date": np.tile(MONTH_DATES, N),
    "balance": balance_matrix.flatten(),
    "transaction_count": txn_count_matrix.flatten(),
    "is_active": active_matrix.flatten(),
}
monthly_customer_metrics = pd.DataFrame(mcm_rows)
# fee & interest income approximations per customer-month
monthly_customer_metrics["fee_income"] = np.round(
    np.clip(monthly_customer_metrics["transaction_count"] * rng.uniform(0.15, 0.6, len(monthly_customer_metrics)), 0, None), 2)
monthly_customer_metrics["interest_income"] = np.round(monthly_customer_metrics["balance"] * (0.10 / 12), 2)
save(monthly_customer_metrics, "monthly_customer_metrics.csv")
monthly_customer_metrics.to_csv(os.path.join(OUT, "monthly_customer_metrics.csv.gz"), index=False, compression="gzip")
os.remove(os.path.join(OUT, "monthly_customer_metrics.csv"))
print("  (monthly_customer_metrics stored gzip-compressed for repo size)")

# ---------------------------------------------------------------------------
# 10. MONTHLY_ACCOUNT_METRICS (split customer balance across their accounts)
# ---------------------------------------------------------------------------
acc_by_cust = accounts.groupby("customer_id")["account_id"].apply(list).to_dict()
acc_weight_rows = []
for c, accs in acc_by_cust.items():
    w = rng.dirichlet(np.ones(len(accs)))
    for a, wi in zip(accs, w):
        acc_weight_rows.append((c, a, wi))
acc_weights = pd.DataFrame(acc_weight_rows, columns=["customer_id", "account_id", "weight"])

mam = monthly_customer_metrics.merge(acc_weights, on="customer_id")
mam["balance"] = np.round(mam["balance"] * mam["weight"], 2)
mam["transaction_count"] = np.round(mam["transaction_count"] * mam["weight"]).astype(int)
monthly_account_metrics = mam[["account_id", "customer_id", "month", "month_end_date",
                                "balance", "transaction_count", "is_active"]].copy()
monthly_account_metrics["avg_daily_balance"] = np.round(
    monthly_account_metrics["balance"] * rng.uniform(0.85, 1.05, len(monthly_account_metrics)), 2)
save(monthly_account_metrics, "monthly_account_metrics.csv")
monthly_account_metrics.to_csv(os.path.join(OUT, "monthly_account_metrics.csv.gz"), index=False, compression="gzip")
os.remove(os.path.join(OUT, "monthly_account_metrics.csv"))
print("  (monthly_account_metrics stored gzip-compressed for repo size)")
del mam, acc_weights
print("Monthly customer & account metrics complete.")

# ---------------------------------------------------------------------------
# 11. TRANSACTIONS (sampled individual events, target ~500K-700K rows)
# ---------------------------------------------------------------------------
TXN_TYPES = ["POS", "ATM Withdrawal", "ATM Deposit", "Transfer", "Bill Payment", "Salary",
             "Direct Debit", "Card Purchase", "Online Payment", "Branch Transaction",
             "Mobile Payment", "Interest Credit", "Fee", "Refund", "Loan Payment",
             "Cash Deposit", "Cash Withdrawal"]
TXN_WEIGHTS = np.array([18, 9, 3, 10, 8, 4, 7, 14, 10, 4, 9, 2, 3, 1.5, 4, 2.5, 4])
TXN_WEIGHTS = TXN_WEIGHTS / TXN_WEIGHTS.sum()

MERCHANT_CATS = ["Groceries", "Utilities", "Restaurants", "Fuel", "Retail", "Healthcare",
                  "Travel", "Entertainment", "Education", "Government", "E-commerce", "Other"]
DEVICE_TYPES = ["Mobile App", "Web", "POS Terminal", "ATM", "Branch Counter"]

nonzero = txn_count_matrix[txn_count_matrix > 0]
cust_idx_grid, month_idx_grid = np.nonzero(txn_count_matrix)
counts = txn_count_matrix[cust_idx_grid, month_idx_grid]

total_rows = int(counts.sum())
print(f"  simulating {total_rows:,} individual transactions ...")

txn_customer_idx = np.repeat(cust_idx_grid, counts)
txn_month_idx = np.repeat(month_idx_grid, counts)

n_txn = len(txn_customer_idx)
txn_customer_id = cid[txn_customer_idx]
txn_month = np.array(month_labels)[txn_month_idx]
month_start = pd.to_datetime([str(MONTHS[m]) + "-01" for m in txn_month_idx])
day_offset = rng.integers(0, 28, n_txn)
seconds_offset = rng.integers(0, 86400, n_txn)
txn_datetime = month_start + pd.to_timedelta(day_offset, unit="D") + pd.to_timedelta(seconds_offset, unit="s")

txn_type = rng.choice(TXN_TYPES, n_txn, p=TXN_WEIGHTS)
is_digital = np.isin(txn_type, ["Online Payment", "Mobile Payment", "Transfer", "Direct Debit"]) | (rng.random(n_txn) < 0.3)
is_international = rng.random(n_txn) < 0.03
is_recurring = np.isin(txn_type, ["Salary", "Direct Debit", "Bill Payment", "Loan Payment", "Interest Credit"])
is_suspicious = rng.random(n_txn) < 0.006

# amount depends on type
amount_base = {
    "POS": (5, 150), "ATM Withdrawal": (20, 400), "ATM Deposit": (20, 800), "Transfer": (10, 2000),
    "Bill Payment": (10, 300), "Salary": (400, 5000), "Direct Debit": (10, 400), "Card Purchase": (5, 250),
    "Online Payment": (5, 300), "Branch Transaction": (20, 1500), "Mobile Payment": (5, 200),
    "Interest Credit": (1, 60), "Fee": (1, 40), "Refund": (5, 150), "Loan Payment": (50, 900),
    "Cash Deposit": (20, 1200), "Cash Withdrawal": (20, 500),
}
amount = np.zeros(n_txn)
for t, (lo, hi) in amount_base.items():
    m_ = txn_type == t
    amount[m_] = np.round(rng.lognormal(np.log((lo + hi) / 2), 0.5, m_.sum()), 2)
    amount[m_] = np.clip(amount[m_], lo * 0.5, hi * 4)

cust_branch = customers.set_index("customer_id")["branch_id"].reindex(txn_customer_id).values
cust_city = customers.set_index("customer_id")["city"].reindex(txn_customer_id).values

transactions = pd.DataFrame({
    "transaction_id": np.arange(1, n_txn + 1),
    "customer_id": txn_customer_id,
    "transaction_datetime": txn_datetime,
    "transaction_type": pd.Categorical(txn_type),
    "amount": amount.astype("float32"),
    "currency": "USD",
    "channel": pd.Categorical(np.where(is_digital, rng.choice(["Mobile App", "Internet Banking"], n_txn),
                                        rng.choice(["Branch", "ATM", "POS Network"], n_txn))),
    "merchant_category": pd.Categorical(rng.choice(MERCHANT_CATS, n_txn)),
    "branch_id": pd.Categorical(cust_branch),
    "city": pd.Categorical(cust_city),
    "device_type": pd.Categorical(rng.choice(DEVICE_TYPES, n_txn)),
    "is_digital": is_digital,
    "is_international": is_international,
    "is_recurring": is_recurring,
    "is_suspicious": is_suspicious,
})
transactions["transaction_id"] = "TXN" + transactions["transaction_id"].astype(str).str.zfill(8)
save(transactions, "transactions.csv")
transactions.to_csv(os.path.join(OUT, "transactions.csv.gz"), index=False, compression="gzip")
os.remove(os.path.join(OUT, "transactions.csv"))
print("  (transactions stored gzip-compressed for repo size: transactions.csv.gz)")
del txn_customer_idx, txn_month_idx, txn_customer_id, txn_month, month_start, day_offset, seconds_offset, txn_datetime
del txn_type, is_digital, is_international, is_recurring, is_suspicious, amount, cust_branch, cust_city
print("Transactions complete.")

# ---------------------------------------------------------------------------
# 12. CARDS
# ---------------------------------------------------------------------------
card_owners = customer_products[customer_products["product_id"].isin(CARD_PRODUCTS)].copy()
card_owners["card_id"] = [f"CARD{i+1:06d}" for i in range(len(card_owners))]
card_owners["card_type"] = card_owners["product_name"]
credit_limit = np.where(card_owners["product_id"] == "PRD03",
                         np.round(rng.uniform(500, 15000, len(card_owners)), -1), 0)
util = np.clip(rng.beta(2, 4, len(card_owners)), 0, 0.98)
cards = pd.DataFrame({
    "card_id": card_owners["card_id"],
    "customer_id": card_owners["customer_id"],
    "product_id": card_owners["product_id"],
    "card_type": card_owners["card_type"],
    "issue_date": card_owners["adoption_date"],
    "credit_limit": credit_limit,
    "credit_utilization": np.where(card_owners["product_id"] == "PRD03", np.round(util, 3), np.nan),
    "monthly_spend": np.round(rng.gamma(2.2, 90, len(card_owners)), 2),
    "avg_transaction_value": np.round(rng.uniform(8, 90, len(card_owners)), 2),
    "is_active": rng.random(len(card_owners)) > 0.05,
    "digital_wallet_enabled": rng.random(len(card_owners)) < 0.55,
    "late_payment_flag": np.where(card_owners["product_id"] == "PRD03", rng.random(len(card_owners)) < 0.11, False),
})
save(cards, "cards.csv")

# ---------------------------------------------------------------------------
# 13. LOANS + LOAN_PAYMENTS
# ---------------------------------------------------------------------------
loan_owners = customer_products[customer_products["product_id"].isin(LOAN_PRODUCTS)].copy().reset_index(drop=True)
n_loans = len(loan_owners)
loan_owners = loan_owners.merge(customers[["customer_id", "annual_income", "risk_segment"]], on="customer_id")
term_map = {"PRD05": 36, "PRD06": 60, "PRD07": 240, "PRD08": 24, "PRD11": 12}
rate_map = products.set_index("product_id")["interest_rate"].to_dict()
loan_owners["term_months"] = loan_owners["product_id"].map(term_map)
loan_owners["interest_rate"] = loan_owners["product_id"].map(rate_map)
loan_amount = np.clip(loan_owners["annual_income"] * rng.uniform(0.15, 1.4, n_loans), 500, 400000)
loan_amount = np.where(loan_owners["product_id"] == "PRD07", loan_owners["annual_income"] * rng.uniform(2.0, 4.5, n_loans), loan_amount)
risk_default_mult = loan_owners["risk_segment"].map({"Low": 0.4, "Moderate": 0.8, "Elevated": 1.3, "High": 2.0, "Critical": 3.2}).values
loan_to_income_raw = loan_amount / loan_owners["annual_income"].clip(lower=1000).values
lti_mult = np.clip(loan_to_income_raw / 1.2, 0.3, 3.5)
pd_base = np.clip(0.025 * risk_default_mult * lti_mult + rng.normal(0, 0.012, n_loans), 0.004, 0.55)

u = rng.random(n_loans)
dpd_bucket = np.select(
    [u < pd_base, u < pd_base * 2.2, u < pd_base * 4.0],
    ["90+", "60-89", "30-59"], default="Current")
default_flag = dpd_bucket == "90+"
lgd = np.clip(rng.normal(0.45, 0.1, n_loans), 0.15, 0.85)

loans = pd.DataFrame({
    "loan_id": [f"LN{i+1:06d}" for i in range(n_loans)],
    "customer_id": loan_owners["customer_id"],
    "product_id": loan_owners["product_id"],
    "loan_type": loan_owners["product_name"],
    "origination_date": loan_owners["adoption_date"],
    "term_months": loan_owners["term_months"],
    "interest_rate": loan_owners["interest_rate"],
    "loan_amount": np.round(loan_amount, 2),
    "outstanding_balance": np.round(loan_amount * rng.uniform(0.2, 0.95, n_loans), 2),
    "probability_of_default": np.round(pd_base, 4),
    "exposure_at_default": np.round(loan_amount * rng.uniform(0.5, 1.0, n_loans), 2),
    "loss_given_default": np.round(lgd, 3),
    "dpd_bucket": dpd_bucket,
    "default_flag": default_flag,
    "risk_bucket": loan_owners["risk_segment"],
    "branch_id": customers.set_index("customer_id").loc[loan_owners["customer_id"], "branch_id"].values,
    "region": customers.set_index("customer_id").loc[loan_owners["customer_id"], "region"].values,
    "acquisition_channel": customers.set_index("customer_id").loc[loan_owners["customer_id"], "acquisition_channel"].values,
})
loans["expected_credit_loss"] = np.round(loans["probability_of_default"] * loans["loss_given_default"] * loans["exposure_at_default"], 2)
save(loans, "loans.csv")

# loan_payments: monthly schedule of payments made so far (sampled, capped for size)
lp_rows = []
sample_loans = loans.sample(n=min(8000, n_loans), random_state=SEED)
for _, ln in sample_loans.iterrows():
    months_elapsed = min(int((pd.Timestamp("2024-12-31") - pd.Timestamp(ln["origination_date"])).days / 30), ln["term_months"], 24)
    monthly_payment = round(ln["loan_amount"] * (ln["interest_rate"] / 12) / (1 - (1 + ln["interest_rate"] / 12) ** (-ln["term_months"])), 2) if ln["term_months"] > 0 else 0
    for mm in range(max(months_elapsed, 0)):
        on_time = rng.random() > (ln["probability_of_default"] * 0.6)
        lp_rows.append((ln["loan_id"], ln["customer_id"], mm + 1, monthly_payment,
                         "On-Time" if on_time else rng.choice(["Late", "Missed"], p=[0.7, 0.3])))
loan_payments = pd.DataFrame(lp_rows, columns=["loan_id", "customer_id", "payment_number", "payment_amount", "payment_status"])
save(loan_payments, "loan_payments.csv")

# ---------------------------------------------------------------------------
# 14. DEPOSITS (term deposit product subset)
# ---------------------------------------------------------------------------
dep_owners = customer_products[customer_products["product_id"] == "PRD09"].copy()
deposits = pd.DataFrame({
    "deposit_id": [f"DEP{i+1:06d}" for i in range(len(dep_owners))],
    "customer_id": dep_owners["customer_id"],
    "open_date": dep_owners["adoption_date"],
    "principal_amount": np.round(rng.uniform(500, 50000, len(dep_owners)), 2),
    "term_months": rng.choice([3, 6, 12, 24, 36], len(dep_owners), p=[0.15, 0.25, 0.35, 0.15, 0.1]),
    "interest_rate": np.round(rng.uniform(0.03, 0.08, len(dep_owners)), 4),
    "auto_renew": rng.random(len(dep_owners)) < 0.4,
    "status": rng.choice(["Active", "Matured", "Withdrawn Early"], len(dep_owners), p=[0.55, 0.35, 0.1]),
})
save(deposits, "deposits.csv")
print("Cards, loans, loan payments, deposits complete.")

# ---------------------------------------------------------------------------
# 15. FRAUD_EVENTS
# ---------------------------------------------------------------------------
n_fraud = 2200
fraud_customers = rng.choice(cid, n_fraud)
fraud_cat = rng.choice(["Card Fraud", "Account Takeover", "Suspicious Transfer", "ATM Fraud",
                         "Identity-related Anomaly", "Unusual Transaction Pattern"],
                        n_fraud, p=[0.32, 0.13, 0.22, 0.12, 0.09, 0.12])
detected = rng.random(n_fraud) < 0.82
false_positive = (~detected) & (rng.random(n_fraud) < 0.35)
fraud_events = pd.DataFrame({
    "fraud_id": [f"FRD{i+1:05d}" for i in range(n_fraud)],
    "customer_id": fraud_customers,
    "event_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 730, n_fraud), unit="D"),
    "fraud_category": fraud_cat,
    "channel": rng.choice(["Mobile App", "Card Network", "ATM", "Online Banking", "Branch"], n_fraud),
    "amount_at_risk": np.round(rng.gamma(2, 350, n_fraud), 2),
    "loss_amount": np.round(np.where(detected, rng.gamma(1.2, 60, n_fraud), rng.gamma(2, 350, n_fraud)), 2),
    "detected_flag": detected,
    "false_positive_flag": false_positive,
    "region": customers.set_index("customer_id").loc[fraud_customers, "region"].values,
})
save(fraud_events, "fraud_events.csv")

# ---------------------------------------------------------------------------
# 16. CREDIT_EVENTS (delinquency / restructuring / write-off history on loans)
# ---------------------------------------------------------------------------
credit_event_loans = loans[loans["dpd_bucket"] != "Current"].copy()
event_type = np.select(
    [credit_event_loans["dpd_bucket"] == "30-59", credit_event_loans["dpd_bucket"] == "60-89"],
    ["Delinquency Notice - 30 Days", "Delinquency Notice - 60 Days"],
    default="Default / Write-off Review")
credit_events = pd.DataFrame({
    "credit_event_id": [f"CE{i+1:05d}" for i in range(len(credit_event_loans))],
    "loan_id": credit_event_loans["loan_id"].values,
    "customer_id": credit_event_loans["customer_id"].values,
    "event_date": pd.to_datetime("2024-06-01") + pd.to_timedelta(rng.integers(0, 210, len(credit_event_loans)), unit="D"),
    "event_type": event_type,
    "outstanding_at_event": credit_event_loans["outstanding_balance"].values,
    "risk_bucket": credit_event_loans["risk_bucket"].values,
})
save(credit_events, "credit_events.csv")

# ---------------------------------------------------------------------------
# 17. CUSTOMER_INTERACTIONS (complaints / service contacts)
# ---------------------------------------------------------------------------
n_int = 32000
int_customers = rng.choice(cid, n_int, p=None)
interaction_type = rng.choice(["Complaint", "Support Call", "Branch Visit", "Chat", "Email Inquiry"],
                               n_int, p=[0.18, 0.28, 0.22, 0.22, 0.10])
resolution_time_hours = np.round(np.clip(rng.gamma(2, 6, n_int), 0.2, 240), 1)
satisfaction = np.clip(rng.normal(3.7, 0.9, n_int), 1, 5).round(1)
interactions = pd.DataFrame({
    "interaction_id": [f"INT{i+1:06d}" for i in range(n_int)],
    "customer_id": int_customers,
    "interaction_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 730, n_int), unit="D"),
    "interaction_type": interaction_type,
    "channel": rng.choice(["Phone", "Branch", "Mobile App", "Email", "Chat"], n_int),
    "resolution_time_hours": resolution_time_hours,
    "satisfaction_score": satisfaction,
    "repeat_contact_flag": rng.random(n_int) < 0.14,
})
save(interactions, "customer_interactions.csv")

# ---------------------------------------------------------------------------
# 18. CAMPAIGNS + CAMPAIGN_RESPONSES
# ---------------------------------------------------------------------------
n_campaigns = 24
campaign_names = [f"{y}-{q} {t} Campaign" for y in [2023, 2024] for q in ["Q1", "Q2", "Q3", "Q4"]
                   for t in ["Acquisition"]][:n_campaigns]
campaigns = pd.DataFrame({
    "campaign_id": [f"CMP{i+1:03d}" for i in range(n_campaigns)],
    "campaign_name": [f"Campaign {i+1:03d} - {rng.choice(['Credit Card', 'Savings', 'Personal Loan', 'Digital Onboarding', 'Term Deposit'])}"
                       for i in range(n_campaigns)],
    "start_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 700, n_campaigns), unit="D"),
    "channel_id": rng.choice(channels["channel_id"], n_campaigns),
    "target_product_id": rng.choice(products["product_id"], n_campaigns),
    "budget": np.round(rng.uniform(5000, 80000, n_campaigns), -2),
    "impressions": rng.integers(20000, 500000, n_campaigns),
})
campaigns["reach"] = (campaigns["impressions"] * rng.uniform(0.4, 0.8, n_campaigns)).astype(int)

n_resp = 46000
resp_campaign = rng.choice(campaigns["campaign_id"], n_resp)
resp_customer = rng.choice(cid, n_resp)
converted = rng.random(n_resp) < 0.14
campaign_responses = pd.DataFrame({
    "response_id": [f"RESP{i+1:06d}" for i in range(n_resp)],
    "campaign_id": resp_campaign,
    "customer_id": resp_customer,
    "response_date": pd.to_datetime("2023-01-05") + pd.to_timedelta(rng.integers(0, 720, n_resp), unit="D"),
    "responded_flag": True,
    "converted_flag": converted,
    "revenue_generated": np.where(converted, np.round(rng.gamma(2, 60, n_resp), 2), 0.0),
})
save(campaigns, "campaigns.csv")
save(campaign_responses, "campaign_responses.csv")
print("Fraud, credit events, interactions, campaigns complete.")

# ---------------------------------------------------------------------------
# 19. MONTHLY_PRODUCT_METRICS
# ---------------------------------------------------------------------------
cp_month = customer_products.copy()
cp_month["adoption_month"] = pd.to_datetime(cp_month["adoption_date"]).dt.to_period("M")
prod_month_rows = []
for m_i, m in enumerate(MONTHS):
    active_products = cp_month[cp_month["adoption_month"] <= m]
    grp = active_products.groupby("product_id").size().reindex(products["product_id"], fill_value=0)
    new_this_month = cp_month[cp_month["adoption_month"] == m].groupby("product_id").size().reindex(products["product_id"], fill_value=0)
    for pid in products["product_id"]:
        prod_month_rows.append({
            "product_id": pid, "month": str(m), "active_customers": int(grp[pid]),
            "new_customers": int(new_this_month[pid]),
        })
monthly_product_metrics = pd.DataFrame(prod_month_rows).merge(products[["product_id", "product_name", "fee_rate", "interest_rate", "monthly_fee"]], on="product_id")
monthly_product_metrics["revenue"] = np.round(
    monthly_product_metrics["active_customers"] * (monthly_product_metrics["monthly_fee"] + 15 * monthly_product_metrics["fee_rate"] + 25 * monthly_product_metrics["interest_rate"] / 12), 2)
save(monthly_product_metrics, "monthly_product_metrics.csv")

# ---------------------------------------------------------------------------
# 20. MONTHLY_BRANCH_METRICS
# ---------------------------------------------------------------------------
cust_branch_map = customers.set_index("customer_id")["branch_id"]
mcm_branch = monthly_customer_metrics.copy()
mcm_branch["branch_id"] = mcm_branch["customer_id"].map(cust_branch_map)
branch_month = mcm_branch.groupby(["branch_id", "month"]).agg(
    active_customers=("is_active", "sum"),
    total_balance=("balance", "sum"),
    total_transactions=("transaction_count", "sum"),
    fee_income=("fee_income", "sum"),
    interest_income=("interest_income", "sum"),
).reset_index()
branch_emp_count = employees.groupby("branch_id").size().rename("employee_count")
branch_month = branch_month.merge(branch_emp_count, on="branch_id", how="left")

# allocate loan interest income to branches (loans carry the customer's branch_id)
_growth_curve_early = np.linspace(0.75, 1.0, N_MONTHS)
_month_to_growth = dict(zip(month_labels, _growth_curve_early))
branch_loan_balance = loans.groupby("branch_id")["outstanding_balance"].sum()
branch_month["loan_interest_income"] = np.round(
    branch_month["branch_id"].map(branch_loan_balance).fillna(0) *
    branch_month["month"].map(_month_to_growth) * (0.082 / 12), 2)

branch_month["revenue"] = np.round(branch_month["fee_income"] + branch_month["interest_income"] + branch_month["loan_interest_income"], 2)
branch_month["operating_cost"] = np.round(branch_month["employee_count"] * rng.uniform(650, 950, len(branch_month)) +
                                            rng.uniform(600, 1400, len(branch_month)), 2)
branch_month["profit"] = np.round(branch_month["revenue"] - branch_month["operating_cost"], 2)
branch_month["revenue_per_employee"] = np.round(branch_month["revenue"] / branch_month["employee_count"].replace(0, np.nan), 2)
save(branch_month, "monthly_branch_metrics.csv")

# ---------------------------------------------------------------------------
# 21. FINANCIALS (bank-level monthly P&L)
# ---------------------------------------------------------------------------
mcm_all = monthly_customer_metrics.groupby("month").agg(
    total_balance=("balance", "sum"), total_fee_income=("fee_income", "sum"),
    total_interest_income_deposits=("interest_income", "sum"), active_customers=("is_active", "sum"),
    total_transactions=("transaction_count", "sum")).reset_index()

loans_by_month_balance = float(loans["outstanding_balance"].sum())  # static proxy, distributed with growth curve below
growth_curve = np.linspace(0.75, 1.0, N_MONTHS)
financials = mcm_all.copy()
financials["loan_interest_income"] = np.round(loans_by_month_balance * growth_curve * (0.082 / 12), 2)
financials["deposit_interest_expense"] = np.round(financials["total_balance"] * 0.02 / 12, 2)
financials["net_interest_income"] = np.round(financials["loan_interest_income"] + financials["total_interest_income_deposits"] - financials["deposit_interest_expense"], 2)
financials["fee_income"] = financials["total_fee_income"]
financials["card_revenue"] = np.round(cards["monthly_spend"].sum() * 0.018 * growth_curve, 2)
financials["other_operating_income"] = np.round(financials["net_interest_income"] * 0.04, 2)
financials["total_revenue"] = np.round(financials["net_interest_income"] + financials["fee_income"] + financials["card_revenue"] + financials["other_operating_income"], 2)

credit_loss_month = float(loans["expected_credit_loss"].sum()) / N_MONTHS
financials["credit_loss"] = np.round(credit_loss_month * growth_curve * rng.uniform(0.9, 1.1, N_MONTHS), 2)
financials["personnel_cost"] = np.round(len(employees) * 650 * rng.uniform(0.97, 1.03, N_MONTHS), 2)
financials["branch_cost"] = np.round(N_BRANCHES * 4200 * rng.uniform(0.97, 1.03, N_MONTHS), 2)
financials["technology_cost"] = np.round(financials["total_revenue"] * 0.05, 2)
financials["marketing_cost"] = np.round(campaigns["budget"].sum() / N_MONTHS * rng.uniform(0.8, 1.2, N_MONTHS), 2)
financials["operations_cost"] = np.round(financials["total_revenue"] * 0.06, 2)
financials["other_operating_costs"] = np.round(financials["total_revenue"] * 0.02, 2)
financials["total_operating_cost"] = financials[["personnel_cost", "branch_cost", "technology_cost",
                                                   "marketing_cost", "operations_cost", "other_operating_costs"]].sum(axis=1).round(2)
financials["pre_provision_profit"] = np.round(financials["total_revenue"] - financials["total_operating_cost"], 2)
financials["operating_profit"] = financials["pre_provision_profit"]
financials["profit_after_credit_costs"] = np.round(financials["operating_profit"] - financials["credit_loss"], 2)
financials["profit_margin"] = np.round(financials["profit_after_credit_costs"] / financials["total_revenue"], 4)
avg_assets_proxy = financials["total_balance"] + loans_by_month_balance
financials["return_on_assets"] = np.round(financials["profit_after_credit_costs"] * 12 / avg_assets_proxy, 4)
equity_proxy = avg_assets_proxy * 0.10
financials["return_on_equity"] = np.round(financials["profit_after_credit_costs"] * 12 / equity_proxy, 4)
financials["cost_to_income_ratio"] = np.round(financials["total_operating_cost"] / financials["total_revenue"], 4)
financials["net_interest_margin"] = np.round(financials["net_interest_income"] * 12 / avg_assets_proxy, 4)
save(financials, "financials.csv")

# ---------------------------------------------------------------------------
# 22. FORECAST_INPUTS + SCENARIO_ASSUMPTIONS
# ---------------------------------------------------------------------------
forecast_inputs = financials[["month", "total_balance", "total_revenue", "net_interest_income",
                               "fee_income", "total_operating_cost", "credit_loss",
                               "profit_after_credit_costs", "active_customers"]].copy()
forecast_inputs["outstanding_loans_proxy"] = loans_by_month_balance * growth_curve
save(forecast_inputs, "forecast_inputs.csv")

scenario_assumptions = pd.DataFrame([
    {"scenario": "Base Case", "deposit_growth_monthly": 0.006, "loan_growth_monthly": 0.008,
     "interest_rate_delta": 0.0, "credit_loss_multiplier": 1.0, "fee_income_growth_monthly": 0.004,
     "customer_acquisition_growth_monthly": 0.010, "churn_rate_monthly": 0.010, "operating_cost_growth_monthly": 0.004,
     "digital_adoption_growth_monthly": 0.004, "marketing_spend_multiplier": 1.0},
    {"scenario": "Growth Case", "deposit_growth_monthly": 0.012, "loan_growth_monthly": 0.016,
     "interest_rate_delta": -0.005, "credit_loss_multiplier": 1.15, "fee_income_growth_monthly": 0.009,
     "customer_acquisition_growth_monthly": 0.020, "churn_rate_monthly": 0.009, "operating_cost_growth_monthly": 0.008,
     "digital_adoption_growth_monthly": 0.008, "marketing_spend_multiplier": 1.4},
    {"scenario": "Efficiency Case", "deposit_growth_monthly": 0.005, "loan_growth_monthly": 0.006,
     "interest_rate_delta": 0.0, "credit_loss_multiplier": 0.9, "fee_income_growth_monthly": 0.004,
     "customer_acquisition_growth_monthly": 0.006, "churn_rate_monthly": 0.009, "operating_cost_growth_monthly": -0.004,
     "digital_adoption_growth_monthly": 0.010, "marketing_spend_multiplier": 0.75},
    {"scenario": "Downside Case", "deposit_growth_monthly": 0.001, "loan_growth_monthly": 0.002,
     "interest_rate_delta": 0.01, "credit_loss_multiplier": 1.5, "fee_income_growth_monthly": -0.002,
     "customer_acquisition_growth_monthly": 0.002, "churn_rate_monthly": 0.016, "operating_cost_growth_monthly": 0.006,
     "digital_adoption_growth_monthly": 0.002, "marketing_spend_multiplier": 0.9},
    {"scenario": "Stress Case", "deposit_growth_monthly": -0.006, "loan_growth_monthly": -0.004,
     "interest_rate_delta": 0.025, "credit_loss_multiplier": 2.4, "fee_income_growth_monthly": -0.01,
     "customer_acquisition_growth_monthly": -0.005, "churn_rate_monthly": 0.028, "operating_cost_growth_monthly": 0.003,
     "digital_adoption_growth_monthly": 0.0, "marketing_spend_multiplier": 0.6},
])
save(scenario_assumptions, "scenario_assumptions.csv")

print("\n== DATA GENERATION COMPLETE ==")
print(f"Customers: {len(customers):,} | Accounts: {len(accounts):,} | Transactions: {n_txn:,}")
print(f"Loans: {len(loans):,} | Cards: {len(cards):,} | Deposits: {len(deposits):,}")









