"""
The 7-stage analysis pipeline. Each endpoint is thin: validate auth,
fetch the user's AnalysisState row, check the prerequisite stage(s) are
present, call the one relevant service-layer function, persist the
result into this stage's column, and return a typed response. No
business/ML logic lives here - see app/services/{profile,recommendation,
graph,roadmap,resume_score}/ for the actual computation.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.pipeline import (
    ProfileStageResponse,
    RecommendationsStageResponse,
    ResumeScoreStageResponse,
    RoadmapStageResponse,
    SkillGapRequest,
    SkillGapStageResponse,
    SuitabilityRequest,
    SuitabilityStageResponse,
    StrengthsStageResponse,
)
from app.services.graph.skill_graph import (
    DEMAND_WEIGHT as SKILL_GAP_DEMAND_WEIGHT,
    PROXIMITY_WEIGHT,
    TEXT_WEIGHT as SKILL_GAP_TEXT_WEIGHT,
    weighted_skill_gap,
)
from app.services.nlp.resume_parser import UnsupportedFileTypeError, extract_text
from app.services.nlp.skill_normalizer import build_skill_lookup, extract_skills
from app.services.pipeline.state import (
    get_or_create_state,
    require_all,
    require_role_in_suitability,
    require_stage,
)
from app.services.profile.builder import build_identity_profile
from app.services.profile.strengths import analyze_strengths
from app.services.recommendation.engine import (
    DEMAND_WEIGHT as SUITABILITY_DEMAND_WEIGHT,
    GRAPH_WEIGHT,
    TEXT_WEIGHT as SUITABILITY_TEXT_WEIGHT,
    score_roles,
)
from app.services.recommendation.explainer import build_recommendations
from app.services.resume_score.scorer import score_resume
from app.services.roadmap.generator import sequence_roadmap

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


async def _extract_uploaded_text(file: UploadFile) -> str:
    file_bytes = await file.read()

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume file too large (max 5 MB).",
        )

    try:
        raw_text = extract_text(file.filename or "", file_bytes)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Couldn't extract any text from that file.",
        )

    return raw_text


@router.post("/profile", response_model=ProfileStageResponse)
async def run_profile_stage(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_text = await _extract_uploaded_text(file)

    skill_lookup = build_skill_lookup(db)
    matched_skills = extract_skills(raw_text, skill_lookup, db)
    extracted_skills = [
        {
            "skill_id": str(s["skill_id"]),
            "name": s["name"],
            "category": s["category"],
            "matched_on": s["matched_on"],
        }
        for s in matched_skills
    ]

    profile_data = build_identity_profile(db, extracted_skills, current_user)

    state = get_or_create_state(db, current_user.id)
    now = datetime.now(timezone.utc)
    state.profile = profile_data
    state.profile_updated_at = now
    # Kept for later stages (suitability, skill_gap) that need the raw
    # text for TF-IDF textual similarity - the profile JSON above only
    # stores the derived summary, not the source text.
    state.resume_text = raw_text
    db.commit()

    return ProfileStageResponse(**profile_data, updated_at=now)


@router.post("/strengths", response_model=StrengthsStageResponse)
def run_strengths_stage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    state = get_or_create_state(db, current_user.id)
    require_stage(state, "profile", "profile")

    result = analyze_strengths(db, state.profile["extracted_skills"])

    now = datetime.now(timezone.utc)
    state.strengths = result
    state.strengths_updated_at = now
    db.commit()

    return StrengthsStageResponse(**result, updated_at=now)


@router.post("/suitability", response_model=SuitabilityStageResponse)
def run_suitability_stage(
    payload: SuitabilityRequest = SuitabilityRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    state = get_or_create_state(db, current_user.id)
    require_stage(state, "profile", "profile")

    roles = score_roles(
        db,
        state.profile["extracted_skills"],
        payload.target_roles,
        resume_text=state.resume_text or "",
    )
    result = {
        "roles": roles,
        "weights": {
            "score_text": SUITABILITY_TEXT_WEIGHT,
            "score_graph": GRAPH_WEIGHT,
            "score_demand": SUITABILITY_DEMAND_WEIGHT,
        },
    }

    now = datetime.now(timezone.utc)
    state.suitability = result
    state.suitability_updated_at = now
    db.commit()

    return SuitabilityStageResponse(**result, updated_at=now)


@router.post("/skill-gap", response_model=SkillGapStageResponse)
def run_skill_gap_stage(
    payload: SkillGapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    state = get_or_create_state(db, current_user.id)
    require_role_in_suitability(state, payload.target_role)

    role = next(
        r for r in state.suitability["roles"]
        if r["role_title"].lower() == payload.target_role.lower()
    )
    user_skill_names = {s["name"] for s in state.profile["extracted_skills"]}
    missing_skills = weighted_skill_gap(
        db,
        user_skill_names,
        role["missing_skills"],
        resume_text=state.resume_text or "",
    )
    result = {
        "target_role": role["role_title"],
        "missing_skills": missing_skills,
        "weights": {
            "score_text": SKILL_GAP_TEXT_WEIGHT,
            "graph_proximity": PROXIMITY_WEIGHT,
            "market_demand": SKILL_GAP_DEMAND_WEIGHT,
        },
    }

    now = datetime.now(timezone.utc)
    state.skill_gap = result
    state.skill_gap_updated_at = now
    db.commit()

    return SkillGapStageResponse(**result, updated_at=now)


@router.post("/roadmap", response_model=RoadmapStageResponse)
def run_roadmap_stage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    state = get_or_create_state(db, current_user.id)
    require_stage(state, "skill_gap", "skill gap")

    sequenced = sequence_roadmap(db, state.skill_gap["missing_skills"])
    result = {"target_role": state.skill_gap["target_role"], **sequenced}

    now = datetime.now(timezone.utc)
    state.roadmap = result
    state.roadmap_updated_at = now
    db.commit()

    return RoadmapStageResponse(**result, updated_at=now)


@router.post("/resume-score", response_model=ResumeScoreStageResponse)
async def run_resume_score_stage(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_text = await _extract_uploaded_text(file)
    result = score_resume(raw_text)

    state = get_or_create_state(db, current_user.id)
    now = datetime.now(timezone.utc)
    state.resume_score = result
    state.resume_score_updated_at = now
    db.commit()

    return ResumeScoreStageResponse(**result, updated_at=now)


@router.post("/recommendations", response_model=RecommendationsStageResponse)
def run_recommendations_stage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    state = get_or_create_state(db, current_user.id)
    require_all(
        state,
        [
            ("profile", "profile"),
            ("strengths", "strengths"),
            ("suitability", "suitability"),
            ("skill_gap", "skill gap"),
            ("roadmap", "roadmap"),
            ("resume_score", "resume score"),
        ],
    )

    recommendations = build_recommendations(
        db,
        state.profile["extracted_skills"],
        state.profile,
        state.strengths,
        state.suitability,
        state.roadmap,
        state.resume_score,
    )

    now = datetime.now(timezone.utc)
    state.recommendations = {"recommendations": recommendations}
    state.recommendations_updated_at = now
    db.commit()

    return RecommendationsStageResponse(recommendations=recommendations, updated_at=now)
