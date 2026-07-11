from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoadmapSkill(BaseModel):
    name: str
    category: Optional[str] = None
    avg_learn_weeks: int
    unlocks_jobs: int   # how many currently-partial jobs this skill helps complete


class RoadmapResponse(BaseModel):
    target_role: Optional[str] = None
    missing_skills: list[RoadmapSkill]
    estimated_weeks: int
    jobs_unlocked: int
    created_at: datetime

    class Config:
        from_attributes = True
