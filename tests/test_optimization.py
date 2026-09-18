def test_optimization_status_is_optimal(optimization_results):
    assert optimization_results["status"] == "Optimal"


def test_optimized_spend_within_budget(optimization_results):
    total = sum(optimization_results["optimized_allocation"].values())
    assert total <= optimization_results["total_budget"] + 1.0


def test_optimized_spend_respects_segment_ceiling(optimization_results):
    ceiling = optimization_results["cac_ceiling_per_segment"]
    for seg, spend in optimization_results["optimized_allocation"].items():
        assert spend <= ceiling + 1.0


def test_optimized_spend_respects_segment_floor(optimization_results):
    floor = optimization_results["min_spend_per_segment"]
    for seg, spend in optimization_results["optimized_allocation"].items():
        assert spend >= floor - 1.0


def test_optimized_profit_at_least_matches_current(optimization_results):
    assert (optimization_results["expected_incremental_profit_optimized"] >=
            optimization_results["expected_incremental_profit_current"] - 1.0)
