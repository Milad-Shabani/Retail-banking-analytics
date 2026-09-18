import numpy as np


def test_total_revenue_reconciles(financials):
    expected = (financials["net_interest_income"] + financials["fee_income"] +
                financials["card_revenue"] + financials["other_operating_income"])
    assert np.allclose(financials["total_revenue"], expected, atol=1.0)


def test_total_operating_cost_reconciles(financials):
    cost_components = ["personnel_cost", "branch_cost", "technology_cost",
                        "marketing_cost", "operations_cost", "other_operating_costs"]
    expected = financials[cost_components].sum(axis=1)
    assert np.allclose(financials["total_operating_cost"], expected, atol=1.0)


def test_pre_provision_profit_reconciles(financials):
    expected = financials["total_revenue"] - financials["total_operating_cost"]
    assert np.allclose(financials["pre_provision_profit"], expected, atol=1.0)


def test_profit_after_credit_costs_reconciles(financials):
    expected = financials["pre_provision_profit"] - financials["credit_loss"]
    assert np.allclose(financials["profit_after_credit_costs"], expected, atol=1.0)


def test_net_interest_income_reconciles(financials):
    expected = (financials["loan_interest_income"] + financials["total_interest_income_deposits"] -
                financials["deposit_interest_expense"])
    assert np.allclose(financials["net_interest_income"], expected, atol=1.0)


def test_cost_to_income_ratio_formula(financials):
    expected = financials["total_operating_cost"] / financials["total_revenue"]
    assert np.allclose(financials["cost_to_income_ratio"], expected, atol=1e-3)


def test_profit_margin_formula(financials):
    expected = financials["profit_after_credit_costs"] / financials["total_revenue"]
    assert np.allclose(financials["profit_margin"], expected, atol=1e-3)


def test_financials_no_missing_months(financials):
    assert len(financials) == 24
    assert financials["month"].is_unique


def test_revenue_is_positive_every_month(financials):
    assert (financials["total_revenue"] > 0).all()


def test_branch_profit_reconciles(monthly_branch_metrics):
    expected = monthly_branch_metrics["revenue"] - monthly_branch_metrics["operating_cost"]
    assert (monthly_branch_metrics["profit"] - expected).abs().max() < 1.0


def test_most_branches_are_profitable_on_average(monthly_branch_metrics):
    avg_profit_by_branch = monthly_branch_metrics.groupby("branch_id")["profit"].mean()
    # a healthy majority of branches should be profitable on average
    assert (avg_profit_by_branch > 0).mean() >= 0.6
