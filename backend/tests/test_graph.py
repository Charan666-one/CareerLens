from app.services.graph.skill_graph import (
    DEMAND_WEIGHT,
    PROXIMITY_WEIGHT,
    TEXT_WEIGHT,
    _combine_skill_gap,
)


def test_weights_sum_to_one():
    assert round(TEXT_WEIGHT + PROXIMITY_WEIGHT + DEMAND_WEIGHT, 6) == 1.0


def test_final_score_matches_manual_weighted_sum():
    score_text, graph_proximity, market_demand = 0.5, 0.9, 0.7

    result = _combine_skill_gap(score_text, graph_proximity, market_demand)

    expected = round(
        TEXT_WEIGHT * score_text
        + PROXIMITY_WEIGHT * graph_proximity
        + DEMAND_WEIGHT * market_demand,
        4,
    )
    assert result["final_score"] == expected


def test_result_reports_all_three_components():
    result = _combine_skill_gap(0.2, 0.4, 0.6)

    assert result["score_text"] == 0.2
    assert result["graph_proximity"] == 0.4
    assert result["market_demand"] == 0.6


def test_none_market_demand_treated_as_zero():
    result = _combine_skill_gap(0.5, 0.5, None)
    assert result["market_demand"] == 0.0
    assert result["final_score"] == round(TEXT_WEIGHT * 0.5 + PROXIMITY_WEIGHT * 0.5, 4)
