from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.db.models import CandidateProfile, Roadmap, User
from app.schemas.roadmap import RoadmapResponse
from app.services.roadmap.engine import generate_roadmap

router = APIRouter()


@router.get("", response_model=RoadmapResponse)
def get_roadmap(
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
            detail="Upload a resume first so we have skills to build a roadmap from.",
        )

    result = generate_roadmap(db, profile.extracted_skills, current_user.target_role)

    existing = db.query(Roadmap).filter(Roadmap.user_id == current_user.id).first()
    if existing:
        existing.target_role = result["target_role"]
        existing.missing_skills = result["missing_skills"]
        existing.estimated_weeks = result["estimated_weeks"]
        existing.jobs_unlocked = result["jobs_unlocked"]
        roadmap_row = existing
    else:
        roadmap_row = Roadmap(
            user_id=current_user.id,
            target_role=result["target_role"],
            missing_skills=result["missing_skills"],
            estimated_weeks=result["estimated_weeks"],
            jobs_unlocked=result["jobs_unlocked"],
        )
        db.add(roadmap_row)

    db.commit()
    db.refresh(roadmap_row)

    return roadmap_row
