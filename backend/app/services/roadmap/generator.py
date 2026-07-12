"""
Sequences a weighted skill gap (see app/services/graph/skill_graph.py)
into an ordered learning roadmap: prerequisites first, then ranked by
importance within the same prerequisite depth, with cumulative time
estimates.
"""
import networkx as nx
from sqlalchemy.orm import Session

from app.db.models import Skill, SkillEdge


def _prerequisite_depths(db: Session, skill_names: list[str]) -> dict[str, int]:
    """
    depth[skill] = length of the longest prerequisite chain (within this
    skill set) ending at that skill. Skills with no in-set prerequisite
    get depth 0.
    """
    name_set = set(skill_names)
    subgraph = nx.DiGraph()
    subgraph.add_nodes_from(name_set)

    id_to_name = dict(db.query(Skill.id, Skill.name).all())
    for edge in db.query(SkillEdge).filter(SkillEdge.relation_type == "prerequisite").all():
        parent_name = id_to_name.get(edge.parent_skill_id)
        child_name = id_to_name.get(edge.child_skill_id)
        if parent_name in name_set and child_name in name_set:
            subgraph.add_edge(parent_name, child_name)

    depths: dict[str, int] = {}
    for node in nx.topological_sort(subgraph):
        preds = list(subgraph.predecessors(node))
        depths[node] = max((depths[p] + 1 for p in preds), default=0)

    return depths


def sequence_roadmap(db: Session, missing_skills: list[dict]) -> dict:
    """
    missing_skills: the weighted skill-gap list persisted by the skill-gap
    stage, each a dict with at least name/category/avg_learn_weeks/
    importance_score.
    """
    if not missing_skills:
        return {"sequenced_skills": [], "total_estimated_weeks": 0}

    names = [s["name"] for s in missing_skills]
    depths = _prerequisite_depths(db, names)

    ordered = sorted(
        missing_skills,
        key=lambda s: (depths.get(s["name"], 0), -s.get("importance_score", 0.0)),
    )

    sequenced = []
    cumulative_weeks = 0
    for index, skill in enumerate(ordered, start=1):
        cumulative_weeks += skill.get("avg_learn_weeks", 4)
        sequenced.append(
            {
                "name": skill["name"],
                "category": skill.get("category"),
                "order": index,
                "avg_learn_weeks": skill.get("avg_learn_weeks", 4),
                "cumulative_weeks": cumulative_weeks,
                "importance_score": skill.get("importance_score", 0.0),
            }
        )

    return {"sequenced_skills": sequenced, "total_estimated_weeks": cumulative_weeks}
