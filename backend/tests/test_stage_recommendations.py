from app.db.models import Job
from app.services.recommendation.explainer import TOP_N, build_recommendations


def _entry(skill):
    return {"skill_id": str(skill.id), "name": skill.name, "category": skill.category, "matched_on": skill.name}


def _acme_backend(results):
    return next(r for r in results if r["title"] == "Backend Engineer" and r["company"] == "Acme Co")


def test_returns_at_most_top_n_recommendations(db_session, skills, jobs):
    for i in range(10):
        db_session.add(Job(title=f"Filler Role {i}", company="Filler Co", description="filler", required_skills=["Python"]))
    db_session.commit()

    results = build_recommendations(db_session, [_entry(skills["Python"])], {}, {}, {}, {}, {})

    assert len(results) == TOP_N


def test_explanation_mentions_primary_domain_and_experience_level(db_session, skills, jobs):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]
    profile = {"primary_domain": "backend", "experience_level": "junior"}

    results = build_recommendations(db_session, extracted, profile, {}, {}, {}, {})

    acme = _acme_backend(results)
    assert "backend" in acme["explanation"]
    assert "junior" in acme["explanation"]


def test_explanation_mentions_strength_category_for_matched_skill(db_session, skills, jobs):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]
    strengths = {"strengths": [{"category": "backend", "skill_count": 2, "avg_market_demand": 0.85}]}

    results = build_recommendations(db_session, extracted, {}, strengths, {}, {}, {})

    acme = _acme_backend(results)
    assert "strength in backend" in acme["explanation"]


def test_explanation_mentions_suitability_score_for_matching_role_title(db_session, skills, jobs):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]
    suitability = {"roles": [{"role_title": "Backend Engineer", "final_score": 0.75}]}

    results = build_recommendations(db_session, extracted, {}, {}, suitability, {}, {})

    acme = _acme_backend(results)
    assert "Backend Engineer" in acme["explanation"]
    assert "75%" in acme["explanation"]


def test_explanation_mentions_roadmap_overlap_for_missing_skill(db_session, skills, jobs):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]
    roadmap = {"sequenced_skills": [{"name": "Docker"}]}

    results = build_recommendations(db_session, extracted, {}, {}, {}, roadmap, {})

    acme = _acme_backend(results)
    assert "Docker" in acme["explanation"]


def test_explanation_flags_low_resume_score(db_session, skills, jobs):
    extracted = [_entry(skills["Python"])]
    resume_score = {"overall_score": 45}

    results = build_recommendations(db_session, extracted, {}, {}, {}, {}, resume_score)

    acme = _acme_backend(results)
    assert "45/100" in acme["explanation"]


def test_explanation_falls_back_to_generic_message_when_no_signals(db_session, skills, jobs):
    results = build_recommendations(db_session, [], {}, {}, {}, {}, {})

    assert all(r["explanation"] == "Scored on skill overlap and market demand alone." for r in results)


def test_job_id_serialized_as_string(db_session, skills, jobs):
    results = build_recommendations(db_session, [_entry(skills["Python"])], {}, {}, {}, {}, {})

    assert isinstance(results[0]["job_id"], str)
