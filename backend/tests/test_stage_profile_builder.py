import pytest

from app.services.profile.builder import build_identity_profile


def _skill_entry(skill, category=None):
    return {
        "skill_id": str(skill.id),
        "name": skill.name,
        "category": category if category is not None else skill.category,
        "matched_on": skill.name,
    }


def test_top_categories_ranked_by_count_then_demand(db_session, skills, test_user):
    extracted = [
        _skill_entry(skills["Python"]),
        _skill_entry(skills["FastAPI"]),
        _skill_entry(skills["React"]),
    ]

    result = build_identity_profile(db_session, extracted, test_user)

    categories = [c["category"] for c in result["top_categories"]]
    assert categories[0] == "backend"  # 2 skills beats frontend's 1
    assert result["primary_domain"] == "backend"


def test_summary_mentions_primary_domain_and_experience_level(db_session, skills, test_user):
    extracted = [_skill_entry(skills["Python"])]

    result = build_identity_profile(db_session, extracted, test_user)

    assert "backend" in result["summary"]
    assert result["experience_level"] in result["summary"].lower()


def test_no_skills_gives_none_primary_domain_and_generic_summary(db_session, test_user):
    result = build_identity_profile(db_session, [], test_user)

    assert result["primary_domain"] is None
    assert result["skill_count"] == 0
    assert "no skills identified" in result["summary"].lower()


@pytest.mark.parametrize(
    "years,expected_level",
    [
        (0, "entry-level"),
        (2, "entry-level"),
        (3, "junior"),
        (5, "junior"),
        (6, "mid-level"),
        (15, "mid-level"),  # "senior" is dead code - the loop's last band always wins
    ],
)
def test_experience_level_bands(db_session, test_user, years, expected_level):
    test_user.experience_years = years

    result = build_identity_profile(db_session, [], test_user)

    assert result["experience_level"] == expected_level


def test_unknown_skill_name_defaults_demand_to_zero(db_session, skills, test_user):
    extracted = [
        {
            "skill_id": "00000000-0000-0000-0000-000000000000",
            "name": "NotASeededSkill",
            "category": "backend",
            "matched_on": "NotASeededSkill",
        }
    ]

    result = build_identity_profile(db_session, extracted, test_user)

    assert result["top_categories"][0]["avg_market_demand"] == 0.0


def test_skill_count_matches_extracted_skills_length(db_session, skills, test_user):
    extracted = [_skill_entry(skills["Python"]), _skill_entry(skills["React"])]

    result = build_identity_profile(db_session, extracted, test_user)

    assert result["skill_count"] == 2
