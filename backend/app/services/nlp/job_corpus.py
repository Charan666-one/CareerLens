"""
Aggregates Job.description text into per-title / per-skill corpora, for
TF-IDF textual similarity scoring in the suitability and skill-gap stages.

Kept separate from app/services/graph/skill_graph.py (scoped to Skill/
SkillEdge graph analysis) and app/api/routes/pipeline.py (no business/ML
logic per its own docstring) - this is the one place Job rows get grouped
into text corpora for either stage to consume.
"""
from sqlalchemy.orm import Session

from app.db.models import Job


def description_corpus_by_title(db: Session, titles: list[str]) -> dict[str, str]:
    """One text blob per job title, joining every posting's description
    that shares that title - mirrors the required_skills union already
    done for the same titles in recommendation/engine.py::score_roles."""
    wanted = set(titles)
    corpus: dict[str, list[str]] = {}
    for job in db.query(Job).all():
        if job.title not in wanted:
            continue
        corpus.setdefault(job.title, []).append(job.description or "")
    return {title: " ".join(parts) for title, parts in corpus.items()}


def description_corpus_by_skill(db: Session, skill_names: list[str]) -> dict[str, str]:
    """One text blob per skill name, joining the descriptions of every job
    whose required_skills lists that skill."""
    wanted = set(skill_names)
    corpus: dict[str, list[str]] = {}
    for job in db.query(Job).all():
        for skill_name in job.required_skills or []:
            if skill_name not in wanted:
                continue
            corpus.setdefault(skill_name, []).append(job.description or "")
    return {name: " ".join(parts) for name, parts in corpus.items()}
