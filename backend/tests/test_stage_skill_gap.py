from app.services.graph.skill_graph import weighted_skill_gap


def _by_name(results, name):
    return next(r for r in results if r["name"] == name)


def test_one_hop_skill_gets_nonzero_proximity(db_session, skills, skill_edges):
    results = weighted_skill_gap(db_session, {"Docker"}, ["Kubernetes"])

    assert _by_name(results, "Kubernetes")["graph_proximity"] > 0.0


def test_two_hop_skill_gets_lower_proximity_than_one_hop(db_session, skills, skill_edges):
    results = weighted_skill_gap(db_session, {"Docker"}, ["Kubernetes", "Helm"])

    kubernetes_proximity = _by_name(results, "Kubernetes")["graph_proximity"]
    helm_proximity = _by_name(results, "Helm")["graph_proximity"]
    assert helm_proximity < kubernetes_proximity


def test_skill_with_no_edges_gets_zero_proximity(db_session, skills, skill_edges):
    results = weighted_skill_gap(db_session, {"Docker"}, ["GraphQL"])

    assert _by_name(results, "GraphQL")["graph_proximity"] == 0.0


def test_market_demand_pulled_from_skill_table(db_session, skills, skill_edges):
    results = weighted_skill_gap(db_session, {"Docker"}, ["Kubernetes"])

    assert _by_name(results, "Kubernetes")["market_demand"] == 0.85


def test_results_sorted_by_importance_score_descending(db_session, skills, skill_edges):
    results = weighted_skill_gap(db_session, {"Docker"}, ["Kubernetes", "Helm", "GraphQL"])

    scores = [r["importance_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_no_owned_skills_still_ranks_on_demand_alone(db_session, skills, skill_edges):
    results = weighted_skill_gap(db_session, set(), ["Kubernetes", "Helm"])

    assert all(r["graph_proximity"] == 0.0 for r in results)
