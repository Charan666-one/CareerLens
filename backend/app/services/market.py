"""
Shared market-demand lookup over the `skills` table.

`skills.market_demand` is nullable, so a row can legitimately hold NULL -
any bulk UPDATE, CSV import, or a future migration that adds a column will
produce them even though `app.db.seed` can't. A plain
`dict(db.query(Skill.name, Skill.market_demand).all())` then maps a name to
None, and a `.get(name, 0.0)` default does NOT save you: the key exists, the
*value* is None, so the default never applies and the next `+=` or `sum()`
raises TypeError - a 500 on /profile, /strengths and /suitability.

Coercing once here means every caller can treat demand as a float.
"""
from sqlalchemy.orm import Session

from app.db.models import Skill


def demand_by_skill_name(db: Session) -> dict[str, float]:
    """Map skill name -> market demand, with NULL coerced to 0.0."""
    return {
        name: (0.0 if demand is None else demand)
        for name, demand in db.query(Skill.name, Skill.market_demand).all()
    }
