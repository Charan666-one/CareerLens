from app.services.recommendation.engine import (
    DEMAND_WEIGHT,
    GRAPH_WEIGHT,
    TEXT_WEIGHT,
    _combine_suitability,
)


def test_weights_sum_to_one():
    assert round(TEXT_WEIGHT + GRAPH_WEIGHT + DEMAND_WEIGHT, 6) == 1.0


def test_final_score_matches_manual_weighted_sum():
    score_text, score_graph, score_demand = 0.4, 0.8, 0.6

    result = _combine_suitability(score_text, score_graph, score_demand)

    expected = round(
        TEXT_WEIGHT * score_text + GRAPH_WEIGHT * score_graph + DEMAND_WEIGHT * score_demand,
        4,
    )
    assert result["final_score"] == expected


def test_result_reports_all_three_components():
    result = _combine_suitability(0.1, 0.2, 0.3)

    assert result["score_text"] == 0.1
    assert result["score_graph"] == 0.2
    assert result["score_demand"] == 0.3


def test_zero_signals_give_zero_final_score():
    result = _combine_suitability(0.0, 0.0, 0.0)
    assert result["final_score"] == 0.0


def test_max_signals_give_final_score_of_one():
    result = _combine_suitability(1.0, 1.0, 1.0)
    assert result["final_score"] == 1.0
