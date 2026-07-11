"""
Skill normalization / extraction from raw resume text.

Given free-text extracted from a resume (see resume_parser.py), find which
known skills (from the `skills` table: name + aliases) are mentioned.

Deliberately simple keyword/regex matching for now - no spaCy yet.
That's a later step in the plan (see PROGRESS.md).
"""
import re
from typing import NamedTuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Skill


class SkillTerm(NamedTuple):
    skill_id: UUID
    name: str
    category: str | None
    term: str          # the literal string to match (skill name or one alias)
    pattern: re.Pattern


def _build_pattern(term: str) -> re.Pattern:
    """Case-insensitive, word-boundary regex for a single skill name/alias."""
    escaped = re.escape(term.strip())
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def build_skill_lookup(db: Session) -> list[SkillTerm]:
    """
    Precompute one SkillTerm (with compiled regex) per skill name AND per
    alias, so extract_skills() can just scan this list against the text
    without re-querying or re-compiling per call.
    """
    lookup: list[SkillTerm] = []

    for skill in db.query(Skill).all():
        lookup.append(
            SkillTerm(
                skill_id=skill.id,
                name=skill.name,
                category=skill.category,
                term=skill.name,
                pattern=_build_pattern(skill.name),
            )
        )
        for alias in skill.aliases or []:
            lookup.append(
                SkillTerm(
                    skill_id=skill.id,
                    name=skill.name,
                    category=skill.category,
                    term=alias,
                    pattern=_build_pattern(alias),
                )
            )

    return lookup


def extract_skills(
    raw_text: str,
    skill_lookup: list[SkillTerm],
    db: Session,
) -> list[dict]:
    """
    Match resume text against the precomputed skill lookup.
    Returns one entry per matched skill (deduped - a skill matched via both
    its name and an alias is only returned once, keeping the first match).
    """
    seen_skill_ids: set[UUID] = set()
    matches: list[dict] = []

    for entry in skill_lookup:
        if entry.skill_id in seen_skill_ids:
            continue
        if entry.pattern.search(raw_text):
            seen_skill_ids.add(entry.skill_id)
            matches.append(
                {
                    "skill_id": entry.skill_id,
                    "name": entry.name,
                    "category": entry.category,
                    "matched_on": entry.term,
                }
            )

    return matches
