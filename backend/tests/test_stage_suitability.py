from app.db.models import Job
from app.services.recommendation.engine import score_roles


def _entry(skill):
    return {"skill_id": str(skill.id), "name": skill.name, "category": skill.category, "matched_on": skill.name}


def _role(results, title):
    return next(r for r in results if r["role_title"] == title)


def test_required_skills_union_across_postings_includes_helm(db_session, skills, jobs):
    results = score_roles(db_session, [], target_roles=["Backend Engineer"])

    backend = _role(results, "Backend Engineer")
    assert "Helm" in backend["missing_skills"]  # only required by the second posting


def test_matched_and_missing_skills_reflect_user_skillset(db_session, skills, jobs):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]

    results = score_roles(db_session, extracted, target_roles=["Backend Engineer"])

    backend = _role(results, "Backend Engineer")
    assert set(backend["matched_skills"]) == {"Python", "FastAPI"}
    assert set(backend["missing_skills"]) == {"Docker", "Kubernetes", "Helm"}


def test_target_roles_filter_restricts_scored_titles(db_session, skills, jobs):
    results = score_roles(db_session, [], target_roles=["Frontend Engineer"])

    assert {r["role_title"] for r in results} == {"Frontend Engineer"}


def test_target_roles_filter_is_case_insensitive(db_session, skills, jobs):
    results = score_roles(db_session, [], target_roles=["frontend engineer"])

    assert {r["role_title"] for r in results} == {"Frontend Engineer"}


def test_unknown_target_role_returns_empty_list(db_session, skills, jobs):
    results = score_roles(db_session, [], target_roles=["Nonexistent Role"])

    assert results == []


def test_role_with_no_required_skills_is_excluded(db_session, skills, jobs):
    empty_job = Job(title="Ghost Role", company="Nowhere", description="", required_skills=[])
    db_session.add(empty_job)
    db_session.commit()

    results = score_roles(db_session, [])

    assert "Ghost Role" not in {r["role_title"] for r in results}


def test_results_sorted_by_final_score_descending(db_session, skills, jobs):
    extracted = [_entry(skills["Python"]), _entry(skills["FastAPI"])]

    results = score_roles(db_session, extracted)

    scores = [r["final_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_score_graph_gives_partial_credit_beyond_binary_overlap(db_session, skills, skill_edges, jobs):
    # Owns only Docker; Kubernetes (1 hop) and Helm (2 hops) are "missing"
    # but graph-adjacent - score_graph should exceed the binary score_overlap.
    extracted = [_entry(skills["Docker"])]

    results = score_roles(db_session, extracted, target_roles=["Backend Engineer"])

    backend = _role(results, "Backend Engineer")
    assert backend["score_graph"] > backend["score_overlap"]


def test_blank_resume_text_gives_zero_text_score_for_every_role(db_session, skills, jobs):
    results = score_roles(db_session, [], resume_text="")

    assert all(r["score_text"] == 0.0 for r in results)
