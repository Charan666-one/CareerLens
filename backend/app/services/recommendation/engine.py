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

        matched = sorted(required & user_skills)
        missing = sorted(required - user_skills)

        score_overlap = len(matched) / len(required)

        if matched:
            score_demand = sum(demand_by_name.get(name, 0.0) for name in matched) / len(matched)
        else:
            score_demand = 0.0

        # simple blend for now: mostly overlap, demand as a secondary signal
        final_score = round(0.8 * score_overlap + 0.2 * score_demand, 4)

        results.append(
            {
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "matched_skills": matched,
                "missing_skills": missing,
                "score_overlap": round(score_overlap, 4),
                "score_demand": round(score_demand, 4),
                "final_score": final_score,
            }
        )

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results
