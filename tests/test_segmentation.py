def test_rfm_scores_within_1_to_5(customers):
    for col in ("r_score", "f_score", "m_score"):
        assert customers[col].between(1, 5).all()


def test_every_customer_has_a_value_segment(customers):
    valid = {"Mass", "Mass Affluent", "Affluent", "High Value", "Premium"}
    assert set(customers["value_segment"].unique()).issubset(valid)


def test_every_customer_has_a_lifecycle_segment(customers):
    valid = {"New", "Growing", "Established", "Loyal", "At Risk", "Dormant", "Churned"}
    assert set(customers["lifecycle_segment"].unique()).issubset(valid)


def test_churned_customers_are_flagged_churned_lifecycle(customers):
    churned = customers[customers["churn_flag"]]
    assert (churned["lifecycle_segment"] == "Churned").mean() > 0.9


def test_clv_is_finite_and_bounded(customers):
    assert customers["customer_lifetime_value"].notna().all()
    assert (customers["customer_lifetime_value"] > -10000).all()


def test_products_owned_count_is_positive(customers):
    assert (customers["products_owned_count"] >= 0).all()


def test_multi_product_flag_consistent_with_count(customers):
    expected = customers["products_owned_count"] > 1
    assert (customers["multi_product_flag"] == expected).all()


def test_digital_adoption_categories_valid(customers):
    assert set(customers["digital_adoption"].unique()).issubset({"High", "Medium", "Low"})


def test_recency_non_negative(customers):
    assert (customers["recency_months"] >= 0).all()
