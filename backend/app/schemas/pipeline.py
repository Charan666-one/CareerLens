from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.resume import ExtractedSkill


class CategoryBreakdown(BaseModel):
    category: str
    skill_count: int
    avg_market_demand: float


class ProfileStageResponse(BaseModel):
    extracted_skills: list[ExtractedSkill]
    primary_domain: Optional[str] = None
    experience_level: str
    top_categories: list[CategoryBreakdown]
    skill_count: int
    summary: str
    updated_at: datetime


class WeaknessOut(BaseModel):
    category: str
    missing_high_demand_skills: list[str]


class StrengthsStageResponse(BaseModel):
    strengths: list[CategoryBreakdown]
    weaknesses: list[WeaknessOut]
    updated_at: datetime


class SuitabilityRequest(BaseModel):
    target_roles: Optional[list[str]] = None


class RoleSuitabilityOut(BaseModel):
    role_title: str
    matched_skills: list[str]
    missing_skills: list[str]
    score_overlap: float
    score_demand: float
    final_score: float


class SuitabilityStageResponse(BaseModel):
    roles: list[RoleSuitabilityOut]
    updated_at: datetime


class SkillGapRequest(BaseModel):
    target_role: str


class SkillGapItemOut(BaseModel):
    name: str
    category: Optional[str] = None
    market_demand: float
    avg_learn_weeks: int
    graph_proximity: float
    importance_score: float


class SkillGapStageResponse(BaseModel):
    target_role: str
    missing_skills: list[SkillGapItemOut]
    updated_at: datetime


class RoadmapSkillOut(BaseModel):
    name: str
    category: Optional[str] = None
    order: int
    avg_learn_weeks: int
    cumulative_weeks: int
    importance_score: float


class RoadmapStageResponse(BaseModel):
    target_role: str
    sequenced_skills: list[RoadmapSkillOut]
    total_estimated_weeks: int
    updated_at: datetime


class ResumeScoreStageResponse(BaseModel):
    ats_score: int
    clarity_score: int
    impact_score: int
    overall_score: int
    word_count: int
    flagged_issues: list[str]
    updated_at: datetime


class JobRecommendationOut(BaseModel):
    job_id: UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    final_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


class RecommendationsStageResponse(BaseModel):
    recommendations: list[JobRecommendationOut]
    updated_at: datetime
