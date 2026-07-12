"""
Builds the final, explainable job recommendations for the recommendations
pipeline stage. Reuses score_jobs() for the actual scoring (never
reimplements it) and layers a plain-language explanation on top, drawing
on the profile/strengths/suitability/roadmap/resume_score state already
persisted by the earlier stages.
"""
from sqlalchemy.orm import Session

from app.db.models import Skill
from app.services.recommendation.engine import score_jobs

TOP_N = 10


def _category_by_name(db: Session) -> dict:
    return dict(db.query(Skill.name, Skill.category).all())


def _explain(job: dict, profile: dict, strengths: dict, suitability: dict, roadmap: dict, resume_score: dict, category_by_name: dict) -> str:
    parts = []

    if profile:
        parts.append(
            f"As a {profile.get('experience_level', 'candidate')} "
            f"{profile.get('primary_domain') or 'generalist'} profile, this role is a "
            f"{round(job['final_score'] * 100)}% match on your current skills."
        )

    strength_categories = {s["category"] for s in (strengths or {}).get("strengths", [])}
    matched_categories = {
        category_by_name.get(name) for name in job["matched_skills"]
        if category_by_name.get(name) in strength_categories
    }
    if matched_categories:
        parts.append(f"It draws on your strength in {', '.join(sorted(matched_categories))}.")

    roles = (suitability or {}).get("roles", [])
    role_match = next((r for r in roles if r["role_title"].lower() == job["title"].lower()), None)
    if role_match:
        parts.append(
            f"Your suitability score for the '{role_match['role_title']}' role is "
            f"{round(role_match['final_score'] * 100)}%."
        )

    roadmap_skill_names = {s["name"] for s in (roadmap or {}).get("sequenced_skills", [])}
    overlap = sorted(set(job["missing_skills"]) & roadmap_skill_names)
    if overlap:
        parts.append(f"Your current roadmap already covers what's missing here: {', '.join(overlap)}.")

    if resume_score and resume_score.get("overall_score", 100) < 60:
        parts.append(
            f"Your resume currently scores {resume_score['overall_score']}/100 - "
            "improving it may strengthen this application."
        )

    return " ".join(parts) if parts else "Scored on skill overlap and market demand alone."


def build_recommendations(
    db: Session,
    extracted_skills: list[dict],
    profile: dict,
    strengths: dict,
    suitability: dict,
    roadmap: dict,
    resume_score: dict,
) -> list[dict]:
    scored = score_jobs(db, extracted_skills)[:TOP_N]
    category_by_name = _category_by_name(db)

    return [
        {
            "job_id": str(job["job_id"]),
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "final_score": job["final_score"],
            "matched_skills": job["matched_skills"],
            "missing_skills": job["missing_skills"],
            "explanation": _explain(job, profile, strengths, suitability, roadmap, resume_score, category_by_name),
        }
        for job in scored
    ]
