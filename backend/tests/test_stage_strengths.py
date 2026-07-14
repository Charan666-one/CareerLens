from app.services.profile.strengths import analyze_strengths


def _entry(skill):
    return {"skill_id": str(skill.id), "name": skill.name, "category": skill.category, "matched_on": skill.name}


def test_category_with_two_high_demand_skills_is_a_strength(db_session, skills):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]

    result = analyze_strengths(db_session, extracted)

    categories = {s["category"] for s in result["strengths"]}
    assert "backend" in categories


def test_thin_category_is_not_a_strength_but_is_a_weakness(db_session, skills):
    # React owned (1 skill in "frontend"), TypeScript missing -> thin category
    extracted = [_entry(skills["React"])]

    result = analyze_strengths(db_session, extracted)

    assert "frontend" not in {s["category"] for s in result["strengths"]}
    frontend_weakness = next(w for w in result["weaknesses"] if w["category"] == "frontend")
    assert "TypeScript" in frontend_weakness["missing_high_demand_skills"]


def test_category_with_zero_owned_skills_is_a_weakness(db_session, skills):
    extracted = [_entry(skills["Python"])]

    result = analyze_strengths(db_session, extracted)

    data_weakness = next(w for w in result["weaknesses"] if w["category"] == "data")
    assert "SQL" in data_weakness["missing_high_demand_skills"]


def test_weaknesses_capped_at_three_missing_skills(db_session, skills):
    # devops has Docker/Kubernetes/Helm already (3) - add a 4th to prove the cap
    from app.db.models import Skill

    extra = Skill(name="Terraform", aliases=[], category="devops", market_demand=0.72, avg_learn_weeks=5)
    db_session.add(extra)
    db_session.commit()

    result = analyze_strengths(db_session, [])

    devops_weakness = next(w for w in result["weaknesses"] if w["category"] == "devops")
    assert len(devops_weakness["missing_high_demand_skills"]) == 3


def test_weaknesses_sorted_by_category_name(db_session, skills):
    result = analyze_strengths(db_session, [])

    categories = [w["category"] for w in result["weaknesses"]]
    assert categories == sorted(categories)


def test_strengths_sorted_by_count_times_demand_descending(db_session, skills):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]

    result = analyze_strengths(db_session, extracted)

    scores = [s["skill_count"] * s["avg_market_demand"] for s in result["strengths"]]
    assert scores == sorted(scores, reverse=True)


def test_no_extracted_skills_yields_empty_strengths_but_full_weaknesses(db_session, skills):
    result = analyze_strengths(db_session, [])

    assert result["strengths"] == []
    assert len(result["weaknesses"]) > 0
