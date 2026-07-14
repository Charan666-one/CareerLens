from sqlalchemy import Column, String, Float, Integer, Text, ARRAY, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class Skill(Base):
    __tablename__ = "skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    aliases = Column(ARRAY(String), default=[])
    category = Column(String)
    market_demand = Column(Float, default=0.0)
    avg_learn_weeks = Column(Integer, default=4)

class SkillEdge(Base):
    __tablename__ = "skill_edges"
    parent_skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True)
    child_skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True)
    relation_type = Column(String)
    weight = Column(Float, default=1.0)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    company = Column(String)
    description = Column(Text)
    required_skills = Column(JSON, default=[])
    experience_years = Column(Integer, default=0)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    location = Column(String)
    job_type = Column(String)
    tfidf_vector = Column(JSON)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    target_role = Column(String)
    experience_years = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    profiles = relationship("CandidateProfile", back_populates="user")

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    raw_resume_text = Column(Text)
    extracted_skills = Column(JSON, default=[])
    skill_timeline = Column(JSON, default={})
    parsed_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="profiles")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    score_semantic = Column(Float)
    score_graph = Column(Float)
    score_demand = Column(Float)
    final_score = Column(Float)
    explanation = Column(JSON)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class Roadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    target_role = Column(String)
    missing_skills = Column(JSON)
    estimated_weeks = Column(Integer)
    jobs_unlocked = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalysisState(Base):
    """
    One row per user holding the full 7-stage pipeline state. Each stage
    owns exactly one JSON column + one `_updated_at` timestamp column, and
    a stage's route only ever touches its own column(s) - running a later
    stage never overwrites an earlier one.
    """
    __tablename__ = "analysis_states"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    profile = Column(JSON)
    profile_updated_at = Column(DateTime(timezone=True))
    # Raw resume text captured at the profile stage - later stages
    # (suitability, skill_gap) reuse it for TF-IDF textual similarity
    # scoring instead of re-deriving it from the profile JSON summary.
    resume_text = Column(Text)

    strengths = Column(JSON)
    strengths_updated_at = Column(DateTime(timezone=True))

    suitability = Column(JSON)
    suitability_updated_at = Column(DateTime(timezone=True))

    skill_gap = Column(JSON)
    skill_gap_updated_at = Column(DateTime(timezone=True))

    roadmap = Column(JSON)
    roadmap_updated_at = Column(DateTime(timezone=True))

    resume_score = Column(JSON)
    resume_score_updated_at = Column(DateTime(timezone=True))

    recommendations = Column(JSON)
    recommendations_updated_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
