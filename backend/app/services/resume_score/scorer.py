"""
Resume "intelligence" scoring for the resume-score pipeline stage.

Rule-based checks only (no NLP model), matching the rest of the
codebase's current heuristic approach: contact info, section headers,
bullet density, action-verb usage, and quantifiable achievements.
"""
import re

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\-\s()]{8,}\d)")
BULLET_PATTERN = re.compile(r"^\s*[-•*]", re.MULTILINE)
NUMBER_PATTERN = re.compile(r"\b\d+(\.\d+)?%?\b")

SECTION_KEYWORDS = ["experience", "education", "skills", "projects"]
ACTION_VERBS = [
    "led", "built", "developed", "designed", "implemented", "improved",
    "created", "managed", "optimized", "launched", "automated", "reduced",
    "increased", "architected", "deployed", "delivered", "mentored",
]

MIN_WORD_COUNT = 300
MAX_WORD_COUNT = 1200


def _count_action_verbs(text_lower: str) -> int:
    return sum(
        len(re.findall(rf"\b{verb}\b", text_lower))
        for verb in ACTION_VERBS
    )


def score_resume(raw_text: str) -> dict:
    text_lower = raw_text.lower()
    word_count = len(raw_text.split())

    has_email = bool(EMAIL_PATTERN.search(raw_text))
    has_phone = bool(PHONE_PATTERN.search(raw_text))
    sections_found = [kw for kw in SECTION_KEYWORDS if kw in text_lower]
    bullet_count = len(BULLET_PATTERN.findall(raw_text))
    action_verb_count = _count_action_verbs(text_lower)
    quantifiable_count = len(NUMBER_PATTERN.findall(raw_text))

    flagged_issues = []

    # ATS compatibility: contact info + section coverage + sane length
    ats_points = 0
    if has_email:
        ats_points += 25
    else:
        flagged_issues.append("No email address detected.")
    if has_phone:
        ats_points += 15
    else:
        flagged_issues.append("No phone number detected.")
    ats_points += 15 * len(sections_found)
    for kw in SECTION_KEYWORDS:
        if kw not in sections_found:
            flagged_issues.append(f"Missing a '{kw.capitalize()}' section.")
    if word_count < MIN_WORD_COUNT:
        flagged_issues.append(f"Resume is short ({word_count} words) - aim for at least {MIN_WORD_COUNT}.")
    elif word_count > MAX_WORD_COUNT:
        flagged_issues.append(f"Resume is long ({word_count} words) - consider trimming below {MAX_WORD_COUNT}.")
    else:
        ats_points += 10
    ats_score = min(100, ats_points)

    # Clarity: bullet-driven, not wall-of-text
    if bullet_count == 0:
        clarity_score = 30
        flagged_issues.append("No bullet points detected - use bullets to improve readability.")
    else:
        bullet_ratio = min(1.0, bullet_count / max(1, word_count / 40))
        clarity_score = round(40 + 60 * bullet_ratio)

    # Impact: action verbs + quantifiable achievements
    impact_score = min(100, action_verb_count * 6 + quantifiable_count * 4)
    if action_verb_count == 0:
        flagged_issues.append("No strong action verbs detected (e.g. 'led', 'built', 'improved').")
    if quantifiable_count == 0:
        flagged_issues.append("No quantifiable achievements (numbers/percentages) found.")

    overall_score = round((ats_score + clarity_score + impact_score) / 3)

    return {
        "ats_score": ats_score,
        "clarity_score": clarity_score,
        "impact_score": impact_score,
        "overall_score": overall_score,
        "word_count": word_count,
        "flagged_issues": flagged_issues,
    }
