"""
Strengths / weaknesses analysis for the strengths pipeline stage.

Strengths = skill categories where the candidate has good coverage and
those skills are in high market demand. Weaknesses = categories from the
full skill taxonomy that are thin or absent for this candidate, each
annotated with the highest-demand skills they're missing there.
"""
from sqlalchemy.orm import Session

from app.db.models import Skill

STRENGTH_MIN_SKILL_COUNT = 2
STRENGTH_MIN_AVG_DEMAND = 0.6
MAX_MISSING_SKILLS_PER_WEAKNESS = 3


def analyze_strengths(db: Session, extracted_skills: list[dict]) -> dict:
    user_skill_names = {entry["name"] for entry in extracted_skills}
    demand_by_name = dict(db.query(Skill.name, Skill.market_demand).all())

    by_category: dict[str, dict] = {}
    for entry in extracted_skills:
        category = entry.get("category") or "uncategorized"
        bucket = by_category.setdefault(category, {"skill_count": 0, "demand_total": 0.0})
        bucket["skill_count"] += 1
        bucket["demand_total"] += demand_by_name.get(entry["name"], 0.0)

    scored_categories = [
        {
            "category": category,
            "skill_count": bucket["skill_count"],
            "avg_market_demand": round(bucket["demand_total"] / bucket["skill_count"], 4),
        }
        for category, bucket in by_category.items()
    ]

    strengths = sorted(
        (
            c for c in scored_categories
            if c["skill_count"] >= STRENGTH_MIN_SKILL_COUNT
            and c["avg_market_demand"] >= STRENGTH_MIN_AVG_DEMAND
        ),
        key=lambda c: c["skill_count"] * c["avg_market_demand"],
        reverse=True,
    )

    all_skills_by_category: dict[str, list[Skill]] = {}
    for skill in db.query(Skill).all():
        all_skills_by_category.setdefault(skill.category or "uncategorized", []).append(skill)

    covered_categories = {c["category"] for c in scored_categories}
    weaknesses = []
    for category, skills in all_skills_by_category.items():
        missing = sorted(
            (s for s in skills if s.name not in user_skill_names),
            key=lambda s: s.market_demand or 0.0,
            reverse=True,
        )
        is_thin = category not in covered_categories or by_category.get(category, {}).get("skill_count", 0) < STRENGTH_MIN_SKILL_COUNT
        if is_thin and missing:
            weaknesses.append(
                {
                    "category": category,
                    "missing_high_demand_skills": [s.name for s in missing[:MAX_MISSING_SKILLS_PER_WEAKNESS]],
                }
            )

    weaknesses.sort(key=lambda w: w["category"])

    return {"strengths": strengths, "weaknesses": weaknesses}
