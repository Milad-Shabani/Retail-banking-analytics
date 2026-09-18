import pandas as pd


def test_customers_no_duplicate_ids(customers):
    assert customers["customer_id"].is_unique


def test_accounts_no_duplicate_ids(accounts):
    assert accounts["account_id"].is_unique


def test_loans_no_duplicate_ids(loans):
    assert loans["loan_id"].is_unique


def test_customers_required_columns_present(customers):
    required = {"customer_id", "age", "region", "income_band", "churn_flag",
                "customer_lifetime_value", "rfm_segment", "value_segment"}
    assert required.issubset(set(customers.columns))


def test_customers_no_missing_ids(customers):
    assert customers["customer_id"].isna().sum() == 0


def test_accounts_referential_integrity(accounts, customers):
    valid_ids = set(customers["customer_id"])
    assert set(accounts["customer_id"]).issubset(valid_ids)


def test_loans_referential_integrity(loans, customers):
    valid_ids = set(customers["customer_id"])
    assert set(loans["customer_id"]).issubset(valid_ids)


def test_customer_products_referential_integrity(customer_products, customers):
    valid_ids = set(customers["customer_id"])
    assert set(customer_products["customer_id"]).issubset(valid_ids)


def test_age_within_plausible_range(customers):
    assert customers["age"].between(18, 100).all()


def test_income_non_negative(customers):
    assert (customers["annual_income"] >= 0).all()


def test_loan_amounts_positive(loans):
    assert (loans["loan_amount"] > 0).all()


def test_loan_outstanding_not_exceed_amount_materially(loans):
    # outstanding balance should not exceed the original loan amount
    assert (loans["outstanding_balance"] <= loans["loan_amount"] + 0.01).all()


def test_dpd_bucket_values_valid(loans):
    assert set(loans["dpd_bucket"].unique()).issubset({"Current", "30-59", "60-89", "90+"})


def test_fraud_loss_non_negative(fraud_events):
    assert (fraud_events["loss_amount"] >= 0).all()


def test_branches_no_duplicate_ids(branches):
    assert branches["branch_id"].is_unique
