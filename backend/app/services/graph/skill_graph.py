"""
Prerequisite-graph analysis over the `skill_edges` table, used by the
skill-gap pipeline stage to weight missing skills by graph proximity to
the candidate's existing skills (not just raw market demand).
"""
import networkx as nx
from sqlalchemy.orm import Session

from app.db.models import Skill, SkillEdge

PROXIMITY_WEIGHT = 0.6
DEMAND_WEIGHT = 0.4


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
) -> list[dict]:
    """
    For each missing skill, find its shortest-path distance (via
    prerequisite/enablement edges) from the nearest skill the candidate
    already has, and blend that proximity with the skill's market demand
    into a single importance_score. Missing skills unreachable from any
    owned skill get graph_proximity 0 and are ranked on demand alone.
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

    results = []
    for name in missing_skill_names:
        skill = skill_rows.get(name)
        market_demand = skill.market_demand if skill else 0.0

        distance = distances.get(name)
        graph_proximity = round(1.0 / (1.0 + distance), 4) if distance is not None else 0.0

        importance_score = round(
            PROXIMITY_WEIGHT * graph_proximity + DEMAND_WEIGHT * (market_demand or 0.0), 4
        )

        results.append(
            {
                "name": name,
                "category": skill.category if skill else None,
                "market_demand": market_demand,
                "avg_learn_weeks": skill.avg_learn_weeks if skill else 4,
                "graph_proximity": graph_proximity,
                "importance_score": importance_score,
            }
        )

    results.sort(key=lambda s: s["importance_score"], reverse=True)
    return results
