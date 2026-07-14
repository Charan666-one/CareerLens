"""
Prerequisite-graph analysis over the `skill_edges` table, used by the
skill-gap pipeline stage to weight missing skills by a hybrid of graph
proximity, TF-IDF textual similarity, and market demand (not just raw
market demand alone).
"""
import networkx as nx
from sqlalchemy.orm import Session

from app.db.models import Skill, SkillEdge
from app.services.nlp.job_corpus import description_corpus_by_skill
from app.services.nlp.text_similarity import similarity_scores

# Symmetric with recommendation/engine.py's TEXT_WEIGHT/GRAPH_WEIGHT/
# DEMAND_WEIGHT by design - graph proximity anchors both stages (most
# discriminating signal), demand is second, and text is weighted lowest
# since the 8-job seed corpus gives TF-IDF real but statistically limited
# power.
TEXT_WEIGHT = 0.30
PROXIMITY_WEIGHT = 0.45
DEMAND_WEIGHT = 0.25


def _combine_skill_gap(score_text: float, graph_proximity: float, market_demand: float) -> dict:
    """
    The one place the skill-gap hybrid's weighted sum happens - pure and
    DB-free so it's directly unit-testable. Every score this returns is
    traceable to these three named components, not a black-box number.
    """
    final_score = round(
        TEXT_WEIGHT * score_text
        + PROXIMITY_WEIGHT * graph_proximity
        + DEMAND_WEIGHT * (market_demand or 0.0),
        4,
    )
    return {
        "score_text": round(score_text, 4),
        "graph_proximity": round(graph_proximity, 4),
        "market_demand": market_demand or 0.0,
        "final_score": final_score,
    }


def build_graph(db: Session) -> nx.DiGraph:
    """
    Directed graph, nodes = skill name, edges = skill_edges rows. Edge
    `distance` is the inverse of its weight, so a strong prerequisite link
    (weight close to 1.0) is "closer" than a weak one.
    """
    graph = nx.DiGraph()

    id_to_name = dict(db.query(Skill.id, Skill.name).all())
    for skill_id, name in id_to_name.items():
        graph.add_node(name)

    for edge in db.query(SkillEdge).all():
        parent_name = id_to_name.get(edge.parent_skill_id)
        child_name = id_to_name.get(edge.child_skill_id)
        if parent_name is None or child_name is None:
            continue
        weight = edge.weight or 1.0
        graph.add_edge(parent_name, child_name, distance=1.0 / weight)

    return graph


def weighted_skill_gap(
    db: Session,
    user_skill_names: set[str],
    missing_skill_names: list[str],
    resume_text: str = "",
) -> list[dict]:
    """
    For each missing skill, blend three signals into a single
    importance_score (see _combine_skill_gap): graph proximity (shortest
    prerequisite/enablement path from the nearest skill the candidate
    already has), TF-IDF textual similarity (resume vs the descriptions of
    jobs that require this skill), and market demand. Missing skills
    unreachable from any owned skill get graph_proximity 0 and are ranked
    on the other two signals.

    Changing these weights (see TEXT_WEIGHT/PROXIMITY_WEIGHT/DEMAND_WEIGHT
    above) will reorder downstream roadmap sequencing
    (roadmap/generator.py::sequence_roadmap tie-breaks on this score) -
    that's expected, not a regression.
    """
    graph = build_graph(db)

    sources = [name for name in user_skill_names if name in graph]
    if sources:
        distances = nx.multi_source_dijkstra_path_length(graph, sources, weight="distance")
    else:
        distances = {}

    skill_rows = {
        s.name: s
        for s in db.query(Skill).filter(Skill.name.in_(missing_skill_names)).all()
    }

    skill_corpus = description_corpus_by_skill(db, missing_skill_names)
    text_scores = similarity_scores(
        resume_text, [skill_corpus.get(name, "") for name in missing_skill_names]
    )

    results = []
    for name, score_text in zip(missing_skill_names, text_scores):
        skill = skill_rows.get(name)
        market_demand = skill.market_demand if skill else 0.0

        distance = distances.get(name)
        graph_proximity = 1.0 / (1.0 + distance) if distance is not None else 0.0

        combined = _combine_skill_gap(score_text, graph_proximity, market_demand)

        results.append(
            {
                "name": name,
                "category": skill.category if skill else None,
                "avg_learn_weeks": skill.avg_learn_weeks if skill else 4,
                "score_text": combined["score_text"],
                "graph_proximity": combined["graph_proximity"],
                "market_demand": combined["market_demand"],
                "importance_score": combined["final_score"],
            }
        )

    results.sort(key=lambda s: s["importance_score"], reverse=True)
    return results
