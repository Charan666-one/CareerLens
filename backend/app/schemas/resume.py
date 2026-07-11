from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExtractedSkill(BaseModel):
    skill_id: UUID
    name: str
    category: Optional[str] = None
    matched_on: str


class ResumeParseResponse(BaseModel):
    extracted_skills: list[ExtractedSkill]
    skill_count: int
    raw_text_length: int
    parsed_at: datetime

    class Config:
        from_attributes = True