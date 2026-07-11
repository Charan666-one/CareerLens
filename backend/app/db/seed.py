"""
Seed the `skills` and `skill_edges` tables from the JSON files in
backend/data/seed/.

Safe to re-run: uses upserts (INSERT ... ON CONFLICT DO UPDATE), keyed on
Skill.name and SkillEdge.(parent_skill_id, child_skill_id).

Run migrations first so the tables exist:
    alembic upgrade head

Then seed:
    python -m app.db.seed
"""
import json
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Skill, SkillEdge

SEED_DIR = Path(__file__).resolve().parents[2] / "data" / "seed"
SKILLS_FILE = SEED_DIR / "skills.json"
EDGES_FILE = SEED_DIR / "edges.json"


def load_json(path: Path):
    with open(path) as f:
        return json.load(f)


def seed_skills(db: Session) -> dict:
    """Upsert skills by unique name. Returns {name: id} for edge seeding."""
    skills_data = load_json(SKILLS_FILE)

    for row in skills_data:
        stmt = pg_insert(Skill).values(
            name=row["name"],
            aliases=row.get("aliases", []),
            category=row.get("category"),
            market_demand=row.get("market_demand", 0.0),
            avg_learn_weeks=row.get("avg_learn_weeks", 4),
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[Skill.name],
            set_={
                "aliases": stmt.excluded.aliases,
                "category": stmt.excluded.category,
                "market_demand": stmt.excluded.market_demand,
                "avg_learn_weeks": stmt.excluded.avg_learn_weeks,
            },
        )
        db.execute(stmt)
    db.commit()

    name_to_id = dict(db.query(Skill.name, Skill.id).all())
    print(f"Seeded {len(skills_data)} skills.")
    return name_to_id


def seed_edges(db: Session, name_to_id: dict) -> None:
    edges_data = load_json(EDGES_FILE)

    inserted = 0
    skipped = []
    for row in edges_data:
        parent_name = row["parent"]
        child_name = row["child"]
        parent_id = name_to_id.get(parent_name)
        child_id = name_to_id.get(child_name)

        if parent_id is None or child_id is None:
            missing = parent_name if parent_id is None else child_name
            skipped.append((parent_name, child_name, missing))
            continue

        stmt = pg_insert(SkillEdge).values(
            parent_skill_id=parent_id,
            child_skill_id=child_id,
            relation_type=row.get("relation"),
            weight=row.get("weight", 1.0),
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[SkillEdge.parent_skill_id, SkillEdge.child_skill_id],
            set_={
                "relation_type": stmt.excluded.relation_type,
                "weight": stmt.excluded.weight,
            },
        )
        db.execute(stmt)
        inserted += 1

    db.commit()
    print(f"Seeded {inserted} skill edges.")

    if skipped:
        print(
            f"\nWARNING: skipped {len(skipped)} edge(s) referencing a skill "
            "not present in skills.json:"
        )
        for parent_name, child_name, missing in skipped:
            print(f"  - {parent_name} -> {child_name}  (missing skill: '{missing}')")
        print(
            "Add the missing skill(s) to data/seed/skills.json and re-run "
            "this script to pick up those edges."
        )


def main():
    db = SessionLocal()
    try:
        name_to_id = seed_skills(db)
        seed_edges(db, name_to_id)
    finally:
        db.close()


if __name__ == "__main__":
    main()