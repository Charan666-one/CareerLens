"""
Job/role recommendation scoring.

score_jobs() (per single posting, used by the legacy /api/recommendations
route) still uses the original overlap+demand blend below - out of scope
for the Checkpoint 3 hybrid upgrade, which only covers the pipeline's
suitability and skill-gap stages.

score_roles() (per role, used by the suitability pipeline stage) has been
upgraded to the hybrid 3-signal model: TF-IDF textual similarity (resume
vs role description), graph proximity (skill graph distance from the
candidate's known skills to the role's required skills), and market
demand. See _combine_suitability() for where those three combine.
"""
from sqlalchemy.orm import Session
import networkx as nx

from app.db.models import Job, Skill
from app.services.graph.skill_graph import build_graph
from app.services.nlp.job_corpus import description_corpus_by_title
from app.services.nlp.text_similarity import similarity_scores

# Symmetric with skill_graph.py's TEXT_WEIGHT/PROXIMITY_WEIGHT/DEMAND_WEIGHT
# by design - graph proximity anchors both stages (most discriminating
# signal), demand is second, and text is weighted lowest since the 8-job
# seed corpus gives TF-IDF real but statistically limited power.
TEXT_WEIGHT = 0.30
GRAPH_WEIGHT = 0.45
DEMAND_WEIGHT = 0.25


def _user_skill_names(extracted_skills: list[dict]) -> set[str]:
    """extracted_skills comes from CandidateProfile.extracted_skills, the
    JSON payload saved by the resume upload route - each entry has a
    'name' key matching Skill.name."""
    return {entry["name"] for entry in extracted_skills}


def _combine_suitability(score_text: float, score_graph: float, score_demand: float) -> dict:
    """
    The one place the suitability hybrid's weighted sum happens - pure and
    DB-free so it's directly unit-testable. Every score this returns is
    traceable to these three named components, not a black-box number.
    """
    final_score = round(
        TEXT_WEIGHT * score_text + GRAPH_WEIGHT * score_graph + DEMAND_WEIGHT * score_demand,
        4,
    )
    return {
        "score_text": round(score_text, 4),
        "score_graph": round(score_graph, 4),
        "score_demand": round(score_demand, 4),
        "final_score": final_score,
    }


def _score_skillset(required: set[str], user_skills: set[str], demand_by_name: dict) -> dict:
    """
    Overlap+demand blend used only by score_jobs() (legacy, per-posting
    /api/recommendations route) now that score_roles() has its own hybrid
    scoring below.
    """
    matched = sorted(required & user_skills)
    missing = sorted(required - user_skills)

    score_overlap = len(matched) / len(required)

    if matched:
        score_demand = sum(demand_by_name.get(name, 0.0) for name in matched) / len(matched)
    else:
        score_demand = 0.0

    # simple blend for now: mostly overlap, demand as a secondary signal
    final_score = round(0.8 * score_overlap + 0.2 * score_demand, 4)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "score_overlap": round(score_overlap, 4),
        "score_demand": round(score_demand, 4),
        "final_score": final_score,
    }


def score_jobs(db: Session, extracted_skills: list[dict]) -> list[dict]:
    """
    Score every job in the DB against the candidate's extracted skills.
    Returns a list of dicts (ready to pass into JobRecommendation),
    sorted by final_score descending.
    """
    user_skills = _user_skill_names(extracted_skills)

    # market_demand lookup, keyed by skill name, for score_demand
    demand_by_name = dict(db.query(Skill.name, Skill.market_demand).all())

    results = []
    for job in db.query(Job).all():
        required = set(job.required_skills or [])

        if not required:
            # avoid divide-by-zero; a job with no listed requirements
            # can't be meaningfully scored on overlap
            continue

        results.append(
            {
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                **_score_skillset(required, user_skills, demand_by_name),
            }
        )

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results


def score_roles(
    db: Session,
    extracted_skills: list[dict],
    target_roles: list[str] | None = None,
    resume_text: str = "",
) -> list[dict]:
    """
    Score the candidate against "roles" - distinct job titles, with
    required_skills unioned across every posting that shares that title.
    If target_roles is given, only those titles are scored (case-insensitive
    match); otherwise every known title is scored.

    Hybrid score per role = TEXT_WEIGHT * score_text + GRAPH_WEIGHT *
    score_graph + DEMAND_WEIGHT * score_demand (see _combine_suitability).
    matched_skills/missing_skills/score_overlap are kept in the result for
    context but are informational only - not part of the weighted sum.
    Graph proximity is a strict generalization of overlap: a matched skill
    sits at graph distance 0 from itself, so score_graph reproduces
    "matched" as its maximum case while unmatched-but-close skills get
    graduated partial credit instead of zero.
    """
    user_skills = _user_skill_names(extracted_skills)
    demand_by_name = dict(db.query(Skill.name, Skill.market_demand).all())

    required_by_title: dict[str, set[str]] = {}
    for job in db.query(Job).all():
        bucket = required_by_title.setdefault(job.title, set())
        bucket.update(job.required_skills or [])

    if target_roles:
        wanted = {t.lower() for t in target_roles}
        required_by_title = {
            title: required
            for title, required in required_by_title.items()
            if title.lower() in wanted
        }

    # Drop titles with no required skills before doing any scoring work.
    required_by_title = {title: req for title, req in required_by_title.items() if req}
    titles = list(required_by_title.keys())

    graph = build_graph(db)
    sources = [name for name in user_skills if name in graph]
    distances = nx.multi_source_dijkstra_path_length(graph, sources, weight="distance") if sources else {}

    title_corpus = description_corpus_by_title(db, titles)
    text_scores = similarity_scores(resume_text, [title_corpus.get(title, "") for title in titles])

    results = []
    for title, text_score in zip(titles, text_scores):
        required = required_by_title[title]
        overlap_stats = _score_skillset(required, user_skills, demand_by_name)

        proximities = [
            1.0 / (1.0 + distances[name]) if name in distances else 0.0
            for name in required
        ]
        score_graph = sum(proximities) / len(proximities)
        score_demand = sum(demand_by_name.get(name, 0.0) for name in required) / len(required)

        results.append(
            {
                "role_title": title,
                "matched_skills": overlap_stats["matched_skills"],
                "missing_skills": overlap_stats["missing_skills"],
                "score_overlap": overlap_stats["score_overlap"],
                **_combine_suitability(text_score, score_graph, score_demand),
            }
        )

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results
