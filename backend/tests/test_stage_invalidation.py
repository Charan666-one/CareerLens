"""
Re-running a stage must invalidate everything derived from it.

Before this, each route wrote only its own column. Re-running suitability
with a different target_roles list left skill_gap/roadmap holding results
for a role that was no longer scored, and require_all only checks the
columns are non-null - so /recommendations combined a fresh suitability set
with a stale roadmap and emitted silently wrong explanations, all 200s.
"""
from app.db.models import AnalysisState
from tests.conftest import GOOD_RESUME_TEXT

PROFILE_URL = "/api/pipeline/profile"
STRENGTHS_URL = "/api/pipeline/strengths"
SUITABILITY_URL = "/api/pipeline/suitability"
SKILL_GAP_URL = "/api/pipeline/skill-gap"
ROADMAP_URL = "/api/pipeline/roadmap"
RESUME_SCORE_URL = "/api/pipeline/resume-score"
RECOMMENDATIONS_URL = "/api/pipeline/recommendations"


def _upload(client, url, headers, content: bytes, filename="resume.txt"):
    return client.post(url, headers=headers, files={"file": (filename, content, "text/plain")})


def _state(db_session, user):
    db_session.expire_all()
    return db_session.query(AnalysisState).filter(AnalysisState.user_id == user.id).first()


def _run_chain_to_roadmap(client, auth_headers, role):
    """profile -> suitability(role) -> skill-gap(role) -> roadmap"""
    _upload(client, PROFILE_URL, auth_headers, GOOD_RESUME_TEXT.encode())
    client.post(SUITABILITY_URL, headers=auth_headers, json={"target_roles": [role]})
    client.post(SKILL_GAP_URL, headers=auth_headers, json={"target_role": role})
    client.post(ROADMAP_URL, headers=auth_headers)


def test_rerunning_suitability_clears_skill_gap_and_roadmap(
    client, db_session, skills, skill_edges, jobs, test_user, auth_headers
):
    _run_chain_to_roadmap(client, auth_headers, "Backend Engineer")

    before = _state(db_session, test_user)
    assert before.skill_gap["target_role"] == "Backend Engineer"
    assert before.roadmap["target_role"] == "Backend Engineer"

    # re-scope suitability to a different role - the old skill_gap/roadmap
    # now describe a role that is no longer scored
    client.post(SUITABILITY_URL, headers=auth_headers, json={"target_roles": ["Frontend Engineer"]})

    after = _state(db_session, test_user)
    assert after.suitability is not None
    assert after.skill_gap is None
    assert after.skill_gap_updated_at is None
    assert after.roadmap is None
    assert after.roadmap_updated_at is None


def test_recommendations_rejects_orphaned_state_instead_of_mixing_roles(
    client, db_session, skills, skill_edges, jobs, test_user, auth_headers
):
    _run_chain_to_roadmap(client, auth_headers, "Backend Engineer")
    client.post(STRENGTHS_URL, headers=auth_headers)
    _upload(client, RESUME_SCORE_URL, auth_headers, GOOD_RESUME_TEXT.encode())

    # everything present -> recommendations works
    assert client.post(RECOMMENDATIONS_URL, headers=auth_headers).status_code == 200

    client.post(SUITABILITY_URL, headers=auth_headers, json={"target_roles": ["Frontend Engineer"]})

    # skill_gap/roadmap were cleared, so this must now 409 rather than
    # silently blending Frontend suitability with a Backend roadmap
    response = client.post(RECOMMENDATIONS_URL, headers=auth_headers)
    assert response.status_code == 409
    assert response.json()["detail"]["error"] == "state_conflict"


def test_reuploading_a_resume_clears_the_whole_derived_chain(
    client, db_session, skills, skill_edges, jobs, test_user, auth_headers
):
    _run_chain_to_roadmap(client, auth_headers, "Backend Engineer")
    client.post(STRENGTHS_URL, headers=auth_headers)

    _upload(client, PROFILE_URL, auth_headers, b"Totally different resume mentioning react and typescript.")

    after = _state(db_session, test_user)
    assert after.profile is not None
    for stage in ("strengths", "suitability", "skill_gap", "roadmap"):
        assert getattr(after, stage) is None, f"{stage} should have been invalidated"


def test_resume_score_is_independent_of_the_profile_chain(
    client, db_session, skills, skill_edges, jobs, test_user, auth_headers
):
    _upload(client, RESUME_SCORE_URL, auth_headers, GOOD_RESUME_TEXT.encode())
    _upload(client, PROFILE_URL, auth_headers, GOOD_RESUME_TEXT.encode())

    # profile must not wipe resume_score - they're independent tracks
    assert _state(db_session, test_user).resume_score is not None


def test_rerunning_resume_score_only_clears_recommendations(
    client, db_session, skills, skill_edges, jobs, test_user, auth_headers
):
    _run_chain_to_roadmap(client, auth_headers, "Backend Engineer")
    client.post(STRENGTHS_URL, headers=auth_headers)
    _upload(client, RESUME_SCORE_URL, auth_headers, GOOD_RESUME_TEXT.encode())
    client.post(RECOMMENDATIONS_URL, headers=auth_headers)

    _upload(client, RESUME_SCORE_URL, auth_headers, GOOD_RESUME_TEXT.encode())

    after = _state(db_session, test_user)
    assert after.recommendations is None       # depends on resume_score
    assert after.skill_gap is not None          # does not
    assert after.roadmap is not None
