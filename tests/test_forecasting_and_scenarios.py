EXPECTED_SERIES = {"deposits", "loans", "revenue", "net_interest_income", "fee_income",
                    "operating_costs", "credit_loss", "profit", "customer_base"}


def test_all_expected_series_forecasted(forecast_results):
    assert EXPECTED_SERIES.issubset(set(forecast_results["series"].keys()))


def test_each_series_has_12_month_forecast(forecast_results):
    for name, r in forecast_results["series"].items():
        assert len(r["forecast_12m"]) == 12, f"{name} forecast should have 12 values"


def test_each_series_has_a_selected_best_method(forecast_results):
    valid_methods = {"Seasonal Naive", "Moving Average", "Holt-Winters (ETS)", "Linear Trend (ML)"}
    for name, r in forecast_results["series"].items():
        assert r["best_method"] in valid_methods


def test_backtest_scores_present_for_all_candidates(forecast_results):
    for name, r in forecast_results["series"].items():
        assert len(r["backtest_scores"]) == 4


def test_forecasted_deposits_are_positive(forecast_results):
    assert all(v > 0 for v in forecast_results["series"]["deposits"]["forecast_12m"])


EXPECTED_SCENARIOS = {"Base Case", "Growth Case", "Efficiency Case", "Downside Case", "Stress Case"}


def test_all_scenarios_present(scenario_results):
    assert set(scenario_results.keys()) == EXPECTED_SCENARIOS


def test_each_scenario_has_12_month_path(scenario_results):
    for name, r in scenario_results.items():
        assert len(r["path"]) == 12


def test_stress_case_worse_than_base_case_on_credit_loss(scenario_results):
    base_final_loss = scenario_results["Base Case"]["path"][-1]["credit_loss"]
    stress_final_loss = scenario_results["Stress Case"]["path"][-1]["credit_loss"]
    assert stress_final_loss > base_final_loss


def test_growth_case_has_higher_month12_deposits_than_downside(scenario_results):
    growth_dep = scenario_results["Growth Case"]["path"][-1]["deposits"]
    downside_dep = scenario_results["Downside Case"]["path"][-1]["deposits"]
    assert growth_dep > downside_dep
