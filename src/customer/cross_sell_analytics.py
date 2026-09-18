"""
Cross-Sell, Product Affinity & Next-Best-Product
--------------------------------------------------
1. Product penetration and cross-sell/up-sell rates.
2. Product-pair affinity (lift) via market-basket-style co-occurrence.
3. A simple analytical next-best-product propensity model per customer.
"""
import pandas as pd
import numpy as np
import json, os
from itertools import combinations
from sklearn.ensemble import RandomForestClassifier

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "outputs", "reports")
os.makedirs(OUT, exist_ok=True)

customers = pd.read_csv(os.path.join(RAW, "customers.csv"))
cp = pd.read_csv(os.path.join(RAW, "customer_products.csv"))
products = pd.read_csv(os.path.join(RAW, "products.csv"))

# ---- penetration & cross-sell ----
n_customers = customers["customer_id"].nunique()
penetration = cp.groupby("product_name")["customer_id"].nunique().sort_values(ascending=False)
penetration_pct = (penetration / n_customers * 100).round(2)

single_product = (customers["products_owned_count"] == 1).mean()
multi_product = 1 - single_product

results = {
    "n_customers": int(n_customers),
    "single_product_rate": round(single_product, 4),
    "multi_product_rate": round(multi_product, 4),
    "avg_products_per_customer": round(customers["products_owned_count"].mean(), 3),
    "product_penetration_pct": penetration_pct.to_dict(),
}

# ---- product affinity (lift) ----
baskets = cp.groupby("customer_id")["product_name"].apply(set)
prod_names = products["product_name"].tolist()
support = {p: sum(p in b for b in baskets) / n_customers for p in prod_names}

affinity_rows = []
for a, b in combinations(prod_names, 2):
    both = sum((a in bask) and (b in bask) for bask in baskets)
    p_both = both / n_customers
    exp = support[a] * support[b]
    lift = round(p_both / exp, 3) if exp > 0 else 0
    if both >= 30:
        affinity_rows.append({"product_a": a, "product_b": b, "customers_with_both": both, "lift": lift})
affinity_df = pd.DataFrame(affinity_rows).sort_values("lift", ascending=False)
results["top_product_affinities"] = affinity_df.head(10).to_dict(orient="records")

# retention check: does Product A + Product B combo retain better than A alone?
retention_rows = []
churn_map = customers.set_index("customer_id")["churn_flag"]
for a, b in affinity_df.head(6)[["product_a", "product_b"]].itertuples(index=False):
    both_custs = [c for c, bask in baskets.items() if a in bask and b in bask]
    a_only_custs = [c for c, bask in baskets.items() if a in bask and b not in bask]
    if len(both_custs) >= 20 and len(a_only_custs) >= 20:
        retention_rows.append({
            "combo": f"{a} + {b}",
            "retention_rate_combo": round(1 - churn_map.reindex(both_custs).mean(), 4),
            "retention_rate_a_only": round(1 - churn_map.reindex(a_only_custs).mean(), 4),
        })
results["cross_sell_retention_effect"] = retention_rows

# ---- Next-Best-Product propensity model ----
owned_matrix = pd.crosstab(cp["customer_id"], cp["product_name"])
owned_matrix = owned_matrix.reindex(customers["customer_id"]).fillna(0).astype(int)

feat_cols = ["age", "annual_income", "tenure_years", "products_owned_count", "customer_value_score"]
cust_feat = customers.set_index("customer_id")[feat_cols].reindex(owned_matrix.index)
cust_feat["digital_high"] = (customers.set_index("customer_id")["digital_adoption"] == "High").astype(int).reindex(owned_matrix.index).values

candidate_products = ["Credit Card", "Personal Loan", "Term Deposit", "Investment Account", "Bancassurance", "Auto Loan"]
nbp_rows = []
for prod in candidate_products:
    if prod not in owned_matrix.columns:
        continue
    y = owned_matrix[prod]
    if y.sum() < 50 or y.sum() > len(y) - 50:
        continue
    X = cust_feat.fillna(0)
    not_owned_mask = y == 0
    clf = RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42, class_weight="balanced")
    clf.fit(X, y)
    proba = clf.predict_proba(X[not_owned_mask])[:, 1]
    top_idx = np.argsort(-proba)[:1000]
    target_customers = X[not_owned_mask].index[top_idx]
    price_map = products.set_index("product_name")
    fee_rate = float(price_map.loc[prod, "fee_rate"]) if prod in price_map.index else 0.01
    monthly_fee = float(price_map.loc[prod, "monthly_fee"]) if prod in price_map.index else 0
    avg_income = cust_feat.loc[target_customers, "annual_income"].mean()
    expected_revenue_per_customer = round(monthly_fee * 12 + fee_rate * avg_income * 0.05, 2)
    for c, p in zip(target_customers[:200], proba[top_idx][:200]):
        nbp_rows.append({"customer_id": c, "recommended_product": prod, "propensity_score": round(float(p), 4),
                          "expected_annual_revenue": expected_revenue_per_customer})

nbp_df = pd.DataFrame(nbp_rows).sort_values(["customer_id", "propensity_score"], ascending=[True, False])
nbp_df = nbp_df.groupby("customer_id").first().reset_index()
nbp_df.to_csv(os.path.join(BASE, "data", "processed", "next_best_product.csv"), index=False)
results["next_best_product_sample_size"] = len(nbp_df)
results["next_best_product_by_recommendation"] = nbp_df["recommended_product"].value_counts().to_dict()

with open(os.path.join(OUT, "cross_sell_results.json"), "w") as fh:
    json.dump(results, fh, indent=2, default=str)

print(json.dumps({k: v for k, v in results.items() if "affinit" not in k}, indent=2, default=str))
