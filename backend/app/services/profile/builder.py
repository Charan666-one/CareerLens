"""
Builds the "Professional Identity Profile" for the profile pipeline stage.

Takes the skills already extracted from a resume (see
app/services/nlp/skill_normalizer.py) and summarizes them into a category
breakdown, a primary domain, and an experience-level bucket. Deliberately
heuristic/rule-based, matching the rest of the codebase's current style.
"""
from sqlalchemy.orm import Session

from app.db.models import Skill, User

EXPERIENCE_BANDS = (
    (0, "entry-level"),
    (3, "junior"),
    (6, "mid-level"),
)


def _experience_level(years: int) -> str:
    level = "senior"
    for threshold, label in EXPERIENCE_BANDS:
        if years >= threshold:
            level = label
    return level


def build_identity_profile(db: Session, extracted_skills: list[dict], user: User) -> dict:
    """
    extracted_skills: list of {skill_id, name, category, matched_on} dicts,
    as produced by skill_normalizer.extract_skills().
    """
    demand_by_name = dict(db.query(Skill.name, Skill.market_demand).all())

    by_category: dict[str, dict] = {}
    for entry in extracted_skills:
        category = entry.get("category") or "uncategorized"
        bucket = by_category.setdefault(category, {"skill_count": 0, "demand_total": 0.0})
        bucket["skill_count"] += 1
        bucket["demand_total"] += demand_by_name.get(entry["name"], 0.0)

    top_categories = sorted(
        (
            {
                "category": category,
                "skill_count": bucket["skill_count"],
                "avg_market_demand": round(bucket["demand_total"] / bucket["skill_count"], 4),
            }
            for category, bucket in by_category.items()
        ),
        key=lambda c: (c["skill_count"], c["avg_market_demand"]),
        reverse=True,
    )

    primary_domain = top_categories[0]["category"] if top_categories else None
    experience_level = _experience_level(user.experience_years or 0)
    skill_count = len(extracted_skills)

    if primary_domain:
        summary = (
            f"{experience_level.capitalize()} candidate with {skill_count} identified skill(s), "
            f"strongest in {primary_domain}."
        )
    else:
        summary = f"{experience_level.capitalize()} candidate with no skills identified yet."

    return {
        "extracted_skills": extracted_skills,
        "primary_domain": primary_domain,
        "experience_level": experience_level,
        "top_categories": top_categories,
        "skill_count": skill_count,
        "summary": summary,
    }
