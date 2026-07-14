from app.db.models import AnalysisState
from tests.conftest import GOOD_RESUME_TEXT

PROFILE_URL = "/api/pipeline/profile"
STRENGTHS_URL = "/api/pipeline/strengths"
SUITABILITY_URL = "/api/pipeline/suitability"
SKILL_GAP_URL = "/api/pipeline/skill-gap"
ROADMAP_URL = "/api/pipeline/roadmap"
RESUME_SCORE_URL = "/api/pipeline/resume-score"
RECOMMENDATIONS_URL = "/api/pipeline/recommendations"


def _upload(client, url, headers, content: bytes, filename="resume.txt", content_type="text/plain"):
    return client.post(url, headers=headers, files={"file": (filename, content, content_type)})


def _state(db_session, user):
    return db_session.query(AnalysisState).filter(AnalysisState.user_id == user.id).first()


# --------------------------------------------------------------------
# Happy paths + persistence
# --------------------------------------------------------------------


def test_profile_route_persists_state_and_returns_derived_profile(client, db_session, skills, jobs, test_user, auth_headers):
    response = _upload(client, PROFILE_URL, auth_headers, GOOD_RESUME_TEXT.encode())

    assert response.status_code == 201 or response.status_code == 200
    body = response.json()
    assert body["skill_count"] > 0
    assert "python" in {s["name"].lower() for s in body["extracted_skills"]}

    state = _state(db_session, test_user)
    assert state is not None
    assert state.profile is not None
    assert state.profile_updated_at is not None
    assert state.resume_text == GOOD_RESUME_TEXT


def test_resume_score_route_persists_state_independent_of_other_stages(client, db_session, test_user, auth_headers):
    response = _upload(client, RESUME_SCORE_URL, auth_headers, GOOD_RESUME_TEXT.encode())

    assert response.status_code == 200
    body = response.json()
    assert "overall_score" in body

    state = _state(db_session, test_user)
    assert state.resume_score is not None
    assert state.profile is None  # unaffected - resume-score has no prerequisite


def test_full_pipeline_happy_path_through_all_seven_stages(client, db_session, skills, skill_edges, jobs, test_user, auth_headers):
    profile_resp = _upload(client, PROFILE_URL, auth_headers, GOOD_RESUME_TEXT.encode())
    assert profile_resp.status_code in (200, 201)

    strengths_resp = client.post(STRENGTHS_URL, headers=auth_headers)
    assert strengths_resp.status_code == 200

    suitability_resp = client.post(SUITABILITY_URL, headers=auth_headers, json={})
    assert suitability_resp.status_code == 200
    roles = suitability_resp.json()["roles"]
    assert any(r["role_title"] == "Backend Engineer" for r in roles)
    assert abs(sum(suitability_resp.json()["weights"].values()) - 1.0) < 1e-6

    skill_gap_resp = client.post(SKILL_GAP_URL, headers=auth_headers, json={"target_role": "Backend Engineer"})
    assert skill_gap_resp.status_code == 200

    roadmap_resp = client.post(ROADMAP_URL, headers=auth_headers)
    assert roadmap_resp.status_code == 200

    resume_score_resp = _upload(client, RESUME_SCORE_URL, auth_headers, GOOD_RESUME_TEXT.encode())
    assert resume_score_resp.status_code == 200

    recommendations_resp = client.post(RECOMMENDATIONS_URL, headers=auth_headers)
    assert recommendations_resp.status_code == 200
    recommendations = recommendations_resp.json()["recommendations"]
    assert len(recommendations) > 0
    assert all(r["explanation"] for r in recommendations)

    state = _state(db_session, test_user)
    for column in ("profile", "strengths", "suitability", "skill_gap", "roadmap", "resume_score", "recommendations"):
        assert getattr(state, column) is not None


# --------------------------------------------------------------------
# Auth enforcement
# --------------------------------------------------------------------


def test_unauthenticated_request_returns_401(client):
    response = client.post(STRENGTHS_URL)
    assert response.status_code == 401


# --------------------------------------------------------------------
# Prerequisite (409 state_conflict) enforcement
# --------------------------------------------------------------------


def test_strengths_without_profile_returns_409(client, test_user, auth_headers):
    response = client.post(STRENGTHS_URL, headers=auth_headers)

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["error"] == "state_conflict"
    assert detail["missing_prerequisite"] == "profile"


def test_suitability_without_profile_returns_409(client, test_user, auth_headers):
    response = client.post(SUITABILITY_URL, headers=auth_headers, json={})

    assert response.status_code == 409
    assert response.json()["detail"]["missing_prerequisite"] == "profile"


def test_skill_gap_without_suitability_returns_409(client, test_user, auth_headers):
    response = client.post(SKILL_GAP_URL, headers=auth_headers, json={"target_role": "Backend Engineer"})

    assert response.status_code == 409
    assert response.json()["detail"]["missing_prerequisite"] == "suitability"


def test_roadmap_without_skill_gap_returns_409(client, test_user, auth_headers):
    response = client.post(ROADMAP_URL, headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["detail"]["missing_prerequisite"] == "skill_gap"


def test_recommendations_without_any_prior_stage_returns_409_listing_all_missing(client, test_user, auth_headers):
    response = client.post(RECOMMENDATIONS_URL, headers=auth_headers)

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["error"] == "state_conflict"
    for label in ("profile", "strengths", "suitability", "skill gap", "roadmap", "resume score"):
        assert label in detail["message"]


def test_fresh_user_with_no_resume_gets_409_on_every_downstream_route(client, fresh_user, fresh_auth_headers):
    assert client.post(STRENGTHS_URL, headers=fresh_auth_headers).status_code == 409
    assert client.post(SUITABILITY_URL, headers=fresh_auth_headers, json={}).status_code == 409
    assert client.post(ROADMAP_URL, headers=fresh_auth_headers).status_code == 409
    assert client.post(RECOMMENDATIONS_URL, headers=fresh_auth_headers).status_code == 409


# --------------------------------------------------------------------
# Malformed / empty resume text
# --------------------------------------------------------------------


def test_profile_route_with_blank_resume_returns_400(client, test_user, auth_headers):
    response = _upload(client, PROFILE_URL, auth_headers, b"   ")
    assert response.status_code == 400


def test_resume_score_route_with_blank_resume_returns_400(client, test_user, auth_headers):
    response = _upload(client, RESUME_SCORE_URL, auth_headers, b"")
    assert response.status_code == 400


def test_profile_route_unsupported_file_type_returns_400(client, test_user, auth_headers):
    response = _upload(client, PROFILE_URL, auth_headers, b"binary content", filename="resume.exe", content_type="application/octet-stream")
    assert response.status_code == 400


def test_profile_route_oversized_file_returns_413(client, test_user, auth_headers):
    oversized = b"a" * (5 * 1024 * 1024 + 1)
    response = _upload(client, PROFILE_URL, auth_headers, oversized)
    assert response.status_code == 413


# --------------------------------------------------------------------
# skill-gap target_role must have been scored in suitability
# --------------------------------------------------------------------


def test_skill_gap_with_target_role_not_in_suitability_returns_409(client, skills, skill_edges, jobs, test_user, auth_headers):
    _upload(client, PROFILE_URL, auth_headers, GOOD_RESUME_TEXT.encode())
    client.post(SUITABILITY_URL, headers=auth_headers, json={"target_roles": ["Frontend Engineer"]})

    response = client.post(SKILL_GAP_URL, headers=auth_headers, json={"target_role": "Backend Engineer"})

    assert response.status_code == 409
    assert "not among the roles scored" in response.json()["detail"]["message"]


def test_skill_gap_target_role_matches_case_insensitively(client, skills, skill_edges, jobs, test_user, auth_headers):
    _upload(client, PROFILE_URL, auth_headers, GOOD_RESUME_TEXT.encode())
    client.post(SUITABILITY_URL, headers=auth_headers, json={"target_roles": ["Frontend Engineer"]})

    response = client.post(SKILL_GAP_URL, headers=auth_headers, json={"target_role": "FRONTEND ENGINEER"})

    assert response.status_code == 200
