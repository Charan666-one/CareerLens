import pytest

from app.services.resume_score.scorer import score_resume

GOOD_RESUME = (
    "Jane Doe - jane@example.com - (555) 123-4567\n\n"
    "Experience\n"
    "- Led a team of 5 engineers and increased deployment velocity by 40%.\n"
    "- Built and deployed 12 backend services using Python and FastAPI.\n"
    "- Improved API latency by 25% through caching and query optimization.\n"
    "- Automated 3 manual release processes, reducing release time by 50%.\n"
    "- Designed and implemented a new authentication system for 10000 users.\n"
    "- Mentored 2 junior engineers and launched a new internal tooling platform.\n"
    + ("Additional detail about ongoing responsibilities and daily engineering work. " * 40)
    + "\n\nEducation\nBS in Computer Science.\n\nSkills\nPython, FastAPI, Docker.\n\nProjects\nBuilt several internal tools."
)


def test_well_formed_resume_scores_high_with_no_missing_contact_flags():
    result = score_resume(GOOD_RESUME)

    assert result["ats_score"] > 50
    assert "No email address detected." not in result["flagged_issues"]
    assert "No phone number detected." not in result["flagged_issues"]


def test_missing_email_flagged():
    result = score_resume("Some resume text with no contact info at all, just words.")
    assert "No email address detected." in result["flagged_issues"]


def test_missing_phone_flagged():
    result = score_resume("Contact me at jane@example.com for more information.")
    assert "No phone number detected." in result["flagged_issues"]


@pytest.mark.parametrize("section", ["experience", "education", "skills", "projects"])
def test_missing_section_keyword_flagged(section):
    all_sections = "Experience Education Skills Projects"
    text = all_sections.replace(section.capitalize(), "")

    result = score_resume(text)

    assert f"Missing a '{section.capitalize()}' section." in result["flagged_issues"]


def test_short_resume_flagged_and_no_length_bonus():
    short_text = "word " * 50  # well under MIN_WORD_COUNT (300)

    result = score_resume(short_text)

    assert any("short" in issue.lower() for issue in result["flagged_issues"])


def test_long_resume_flagged():
    long_text = "word " * 1300  # over MAX_WORD_COUNT (1200)

    result = score_resume(long_text)

    assert any("long" in issue.lower() for issue in result["flagged_issues"])


def test_no_bullets_clarity_floors_at_thirty():
    result = score_resume("A resume with no bullet points anywhere in the text at all.")

    assert result["clarity_score"] == 30
    assert any("bullet" in issue.lower() for issue in result["flagged_issues"])


def test_no_action_verbs_and_no_numbers_flagged():
    result = score_resume("A plain resume with no strong verbs and no digits present.")

    assert result["impact_score"] == 0
    assert any("action verb" in issue.lower() for issue in result["flagged_issues"])
    assert any("quantifiable" in issue.lower() for issue in result["flagged_issues"])


def test_empty_string_input_does_not_crash():
    result = score_resume("")

    assert result["word_count"] == 0
    assert result["clarity_score"] == 30
    assert isinstance(result["overall_score"], int)
