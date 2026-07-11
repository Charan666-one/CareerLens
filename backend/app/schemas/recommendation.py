from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class JobRecommendation(BaseModel):
    job_id: UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    matched_skills: list[str]
    missing_skills: list[str]
    score_overlap: float       # fraction of required_skills the user has (0-1)
    score_demand: float        # avg market_demand of the user's matched skills (0-1)
    final_score: float         # current combined score (overlap + demand blend)


class RecommendationResponse(BaseModel):
    recommendations: list[JobRecommendation]
    total: int
