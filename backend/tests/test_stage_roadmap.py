import networkx as nx
import pytest

from app.db.models import Skill, SkillEdge
from app.services.roadmap.generator import sequence_roadmap


def _missing(name, importance_score, avg_learn_weeks=4, category=None):
    return {
        "name": name,
        "category": category,
        "avg_learn_weeks": avg_learn_weeks,
        "importance_score": importance_score,
    }


def test_empty_missing_skills_short_circuits(db_session):
    result = sequence_roadmap(db_session, [])

    assert result == {"sequenced_skills": [], "total_estimated_weeks": 0}


def test_two_hop_prerequisite_chain_orders_by_depth(db_session, skills, skill_edges):
    missing = [
        _missing("Helm", importance_score=0.9, avg_learn_weeks=3, category="devops"),
        _missing("Docker", importance_score=0.1, avg_learn_weeks=6, category="devops"),
        _missing("Kubernetes", importance_score=0.5, avg_learn_weeks=8, category="devops"),
    ]

    result = sequence_roadmap(db_session, missing)

    names_in_order = [s["name"] for s in result["sequenced_skills"]]
    assert names_in_order == ["Docker", "Kubernetes", "Helm"]


def test_same_depth_ties_broken_by_importance_score_descending(db_session, skills, skill_edges):
    # Docker and GraphQL share no prerequisite edge - both depth 0.
    missing = [
        _missing("Docker", importance_score=0.5),
        _missing("GraphQL", importance_score=0.9),
    ]

    result = sequence_roadmap(db_session, missing)

    names_in_order = [s["name"] for s in result["sequenced_skills"]]
    assert names_in_order == ["GraphQL", "Docker"]


def test_cumulative_weeks_sums_avg_learn_weeks_in_order(db_session, skills, skill_edges):
    missing = [
        _missing("Docker", importance_score=0.1, avg_learn_weeks=6),
        _missing("Kubernetes", importance_score=0.5, avg_learn_weeks=8),
        _missing("Helm", importance_score=0.9, avg_learn_weeks=3),
    ]

    result = sequence_roadmap(db_session, missing)

    cumulative = [s["cumulative_weeks"] for s in result["sequenced_skills"]]
    assert cumulative == [6, 14, 17]
    assert result["total_estimated_weeks"] == 17


def test_prerequisite_cycle_raises_networkx_unfeasible(db_session):
    # Deliberately construct a cycle - documents current (uncaught)
    # behavior rather than fixing it, which is out of scope here.
    a = Skill(name="CycleA", aliases=[], category="test", market_demand=0.5, avg_learn_weeks=1)
    b = Skill(name="CycleB", aliases=[], category="test", market_demand=0.5, avg_learn_weeks=1)
    db_session.add_all([a, b])
    db_session.commit()
    db_session.add_all(
        [
            SkillEdge(parent_skill_id=a.id, child_skill_id=b.id, relation_type="prerequisite", weight=1.0),
            SkillEdge(parent_skill_id=b.id, child_skill_id=a.id, relation_type="prerequisite", weight=1.0),
        ]
    )
    db_session.commit()

    missing = [_missing("CycleA", 0.5), _missing("CycleB", 0.5)]

    with pytest.raises(nx.NetworkXUnfeasible):
        sequence_roadmap(db_session, missing)
