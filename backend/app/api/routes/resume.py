from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.db.models import CandidateProfile, User
from app.schemas.resume import ResumeParseResponse
from app.services.nlp.resume_parser import UnsupportedFileTypeError, extract_text
from app.services.nlp.skill_normalizer import build_skill_lookup, extract_skills

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/upload", response_model=ResumeParseResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    skill_lookup = build_skill_lookup(db)
    matched_skills = extract_skills(raw_text, skill_lookup, db)

    # one profile per user - update in place if it already exists
    profile = (
        db.query(CandidateProfile)
        .filter(CandidateProfile.user_id == current_user.id)
        .first()
    )
    extracted_skills_payload = [
        {
            "skill_id": str(s["skill_id"]),
            "name": s["name"],
            "category": s["category"],
            "matched_on": s["matched_on"],
        }
        for s in matched_skills
    ]

    if profile is None:
        profile = CandidateProfile(
            user_id=current_user.id,
            raw_resume_text=raw_text,
            extracted_skills=extracted_skills_payload,
        )
        db.add(profile)
    else:
        profile.raw_resume_text = raw_text
        profile.extracted_skills = extracted_skills_payload

    db.commit()
    db.refresh(profile)

    return ResumeParseResponse(
        extracted_skills=matched_skills,
        skill_count=len(matched_skills),
        raw_text_length=len(raw_text),
        parsed_at=profile.parsed_at,
    )