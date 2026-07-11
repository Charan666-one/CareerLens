from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.db.models import CandidateProfile, User
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation.engine import score_jobs

router = APIRouter()


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(CandidateProfile)
        .filter(CandidateProfile.user_id == current_user.id)
        .first()
    )

    if profile is None or not profile.extracted_skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload a resume first so we have skills to match against.",
        )

    scored = score_jobs(db, profile.extracted_skills)

    return RecommendationResponse(recommendations=scored, total=len(scored))
