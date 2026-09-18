def test_churn_model_roc_auc_within_valid_range(churn_results):
    for model in ("logistic_regression", "gradient_boosting"):
        auc = churn_results[model]["roc_auc"]
        assert 0.5 <= auc <= 1.0, f"{model} ROC-AUC {auc} should beat random guessing"


def test_churn_model_beats_random_guessing_meaningfully(churn_results):
    assert churn_results["gradient_boosting"]["roc_auc"] > 0.7


def test_churn_model_confusion_matrix_shape(churn_results):
    for model in ("logistic_regression", "gradient_boosting"):
        cm = churn_results[model]["confusion_matrix"]
        assert len(cm) == 2 and len(cm[0]) == 2


def test_credit_risk_model_roc_auc_within_valid_range(credit_results):
    for model in ("logistic_regression", "gradient_boosting"):
        auc = credit_results[model]["roc_auc"]
        assert 0.4 <= auc <= 1.0


def test_npl_ratio_within_plausible_bounds(credit_results):
    assert 0 <= credit_results["npl_ratio"] <= 0.25


def test_default_rate_within_plausible_bounds(credit_results):
    assert 0 <= credit_results["default_rate"] <= 0.20


def test_dpd_distribution_sums_to_one(credit_results):
    total = sum(credit_results["dpd_distribution"].values())
    assert abs(total - 1.0) < 0.01


def test_portfolio_risk_summary_has_all_buckets(credit_results):
    buckets = {row["risk_bucket"] for row in credit_results["portfolio_risk_summary"]}
    assert buckets.issuperset({"Low", "Moderate", "Elevated", "High", "Critical"})


def test_expected_credit_loss_matches_pd_lgd_ead(loans):
    computed = loans["probability_of_default"] * loans["loss_given_default"] * loans["exposure_at_default"]
    assert (loans["expected_credit_loss"] - computed).abs().max() < 1.0
