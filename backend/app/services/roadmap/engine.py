"""
Basic roadmap generator: aggregates missing skills across all jobs the
user is a partial match for, ranks them by how many jobs each skill would
help complete, and estimates the time to close that gap.

Graph-based sequencing (using skill_edges for prerequisites/order) is a
later phase per the project plan - this is intentionally a flat ranked
list first.
"""
from sqlalchemy.orm import Session

from app.db.models import Skill
from app.services.recommendation.engine import score_jobs


def generate_roadmap(db: Session, extracted_skills: list[dict], target_role: str | None) -> dict:
    scored_jobs = score_jobs(db, extracted_skills)

    # Only consider jobs the user is a partial match for (score_overlap > 0
    # and < 1). A job with 0 overlap is too far off to be a near-term
    # target; a job already at 1.0 has nothing missing.
    partial_jobs = [j for j in scored_jobs if 0 < j["score_overlap"] < 1]

    # Count how many partial jobs each missing skill would help complete
    skill_job_counts: dict[str, int] = {}
    for job in partial_jobs:
        for skill_name in job["missing_skills"]:
            skill_job_counts[skill_name] = skill_job_counts.get(skill_name, 0) + 1

    if not skill_job_counts:
        return {
            "target_role": target_role,
            "missing_skills": [],
            "estimated_weeks": 0,
            "jobs_unlocked": 0,
        }

    skills_by_name = {
        s.name: s
        for s in db.query(Skill).filter(Skill.name.in_(skill_job_counts.keys())).all()
    }

    ranked = []
    for name, job_count in skill_job_counts.items():
        skill = skills_by_name.get(name)
        ranked.append(
            {
                "name": name,
                "category": skill.category if skill else None,
                "avg_learn_weeks": skill.avg_learn_weeks if skill else 4,
                "unlocks_jobs": job_count,
            }
        )

    # most job-impact first, then quickest wins as tiebreaker
    ranked.sort(key=lambda s: (-s["unlocks_jobs"], s["avg_learn_weeks"]))

    estimated_weeks = sum(s["avg_learn_weeks"] for s in ranked)

    # jobs_unlocked: how many partial jobs would reach full match if the
    # user learned every skill in this ranked list
    recommended_names = {s["name"] for s in ranked}
    jobs_unlocked = sum(
        1 for job in partial_jobs
        if set(job["missing_skills"]) <= recommended_names
    )

    return {
        "target_role": target_role,
        "missing_skills": ranked,
        "estimated_weeks": estimated_weeks,
        "jobs_unlocked": jobs_unlocked,
    }
