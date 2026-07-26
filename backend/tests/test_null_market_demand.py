"""
`skills.market_demand` is nullable, so a row can hold NULL even though
app.db.seed never writes one (bulk UPDATE, CSV import, a migration adding
the column). Every consumer used to do `demand_by_name.get(name, 0.0)`,
which does NOT guard against this - the key exists and its value is None,
so the default never applies and the following arithmetic raised
TypeError, surfacing as a 500 on /profile, /strengths and /suitability.

These pin the NULL-safe behaviour of app.services.market.demand_by_skill_name.
"""
from app.services.market import demand_by_skill_name
from app.services.profile.builder import build_identity_profile
from app.services.profile.strengths import analyze_strengths
from app.services.recommendation.engine import score_roles


def _null_out(db_session, skills, name):
    skills[name].market_demand = None
    db_session.commit()


def _entry(skill):
    return {
        "skill_id": str(skill.id),
        "name": skill.name,
        "category": skill.category,
        "matched_on": skill.name,
    }


def test_lookup_coerces_null_demand_to_zero(db_session, skills):
    _null_out(db_session, skills, "Python")

    lookup = demand_by_skill_name(db_session)

    assert lookup["Python"] == 0.0
    assert all(v is not None for v in lookup.values())


def test_build_identity_profile_survives_null_demand(db_session, skills, test_user):
    _null_out(db_session, skills, "Python")

    result = build_identity_profile(db_session, [_entry(skills["Python"])], test_user)

    assert result["skill_count"] == 1
    assert result["top_categories"][0]["avg_market_demand"] == 0.0


def test_analyze_strengths_survives_null_demand(db_session, skills):
    _null_out(db_session, skills, "Python")
    _null_out(db_session, skills, "FastAPI")

    result = analyze_strengths(
        db_session, [_entry(skills["Python"]), _entry(skills["FastAPI"])]
    )

    # backend now averages 0.0 demand, so it no longer clears the
    # strength threshold - the point is that it returns instead of raising.
    assert result["strengths"] == []


def test_score_roles_survives_null_demand(db_session, skills, skill_edges, jobs):
    _null_out(db_session, skills, "Python")

    roles = score_roles(db_session, [_entry(skills["Python"])], resume_text="python")

    assert roles, "expected at least one scored role"
    assert all(r["score_demand"] is not None for r in roles)
