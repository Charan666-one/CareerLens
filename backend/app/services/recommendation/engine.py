"""
Basic overlap-based job recommendation scoring.

For each job, compares the candidate's extracted skill names against the
job's required_skills. Semantic similarity and graph-based scoring
(score_semantic, score_graph on the Recommendation model) are later
phases per the project plan - this is intentionally simple keyword
overlap first.
"""
from sqlalchemy.orm import Session

from app.db.models import Job, Skill


def _user_skill_names(extracted_skills: list[dict]) -> set[str]:
    """extracted_skills comes from CandidateProfile.extracted_skills, the
    JSON payload saved by the resume upload route - each entry has a
    'name' key matching Skill.name."""
    return {entry["name"] for entry in extracted_skills}


def _score_skillset(required: set[str], user_skills: set[str], demand_by_name: dict) -> dict:
    """
    Shared overlap+demand blend used to score a candidate against any
    required-skill set, whether that set belongs to a single job posting
    (score_jobs) or a role aggregated across postings (score_roles).
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


def score_roles(db: Session, extracted_skills: list[dict], target_roles: list[str] | None = None) -> list[dict]:
    """
    Score the candidate against "roles" - distinct job titles, with
    required_skills unioned across every posting that shares that title.
    If target_roles is given, only those titles are scored (case-insensitive
    match); otherwise every known title is scored.
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

    results = []
    for title, required in required_by_title.items():
        if not required:
            continue

        results.append(
            {
                "role_title": title,
                **_score_skillset(required, user_skills, demand_by_name),
            }
        )

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results
