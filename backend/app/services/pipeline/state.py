"""
Shared state-fetch and prerequisite-check helpers for the 7-stage
pipeline routes (app/api/routes/pipeline.py). Centralizing this here
means every route enforces the same "prior stage must exist" rule the
same way, instead of re-deriving the check per endpoint.
"""
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import AnalysisState


def get_or_create_state(db: Session, user_id: UUID) -> AnalysisState:
    state = db.query(AnalysisState).filter(AnalysisState.user_id == user_id).first()
    if state is None:
        state = AnalysisState(user_id=user_id)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def _conflict(missing_stage: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error": "state_conflict",
            "missing_prerequisite": missing_stage,
            "message": message,
        },
    )


def require_stage(state: AnalysisState, column: str, stage_label: str) -> None:
    if getattr(state, column) is None:
        raise _conflict(
            missing_stage=column,
            message=f"Run the {stage_label} stage first.",
        )


def require_all(state: AnalysisState, columns: list[tuple[str, str]]) -> None:
    missing = [(column, label) for column, label in columns if getattr(state, column) is None]
    if missing:
        column, label = missing[0]
        raise _conflict(
            missing_stage=column,
            message=(
                f"Run the {label} stage first "
                f"(missing: {', '.join(label for _, label in missing)})."
            ),
        )


# Which stages become meaningless when a given stage is (re)run. Mirrors
# the prerequisite graph enforced above, transitively closed: profile feeds
# strengths+suitability, suitability feeds skill_gap, skill_gap feeds
# roadmap, and recommendations consumes all six. resume_score is
# independent of the main chain, so nothing upstream invalidates it - but
# it does feed recommendations.
_DOWNSTREAM_OF: dict[str, tuple[str, ...]] = {
    "profile": ("strengths", "suitability", "skill_gap", "roadmap", "recommendations"),
    "strengths": ("recommendations",),
    "suitability": ("skill_gap", "roadmap", "recommendations"),
    "skill_gap": ("roadmap", "recommendations"),
    "roadmap": ("recommendations",),
    "resume_score": ("recommendations",),
    "recommendations": (),
}


def invalidate_downstream(state: AnalysisState, column: str) -> list[str]:
    """
    Clear every stage that was derived from `column`, because re-running it
    just invalidated their inputs.

    Without this, re-running suitability with a different target_roles list
    leaves skill_gap/roadmap holding results for a role that is no longer
    scored. require_all only checks the columns are non-null, so
    /recommendations would then happily combine a fresh suitability set with
    a stale roadmap and emit silently wrong explanations. Same for
    re-uploading a different resume via /profile: everything downstream
    still describes the previous resume's skills.

    Returns the stage names cleared, so the caller can tell the client what
    it now needs to re-run.
    """
    cleared = []
    for downstream in _DOWNSTREAM_OF.get(column, ()):
        if getattr(state, downstream) is not None:
            setattr(state, downstream, None)
            setattr(state, f"{downstream}_updated_at", None)
            cleared.append(downstream)
    return cleared


def require_role_in_suitability(state: AnalysisState, target_role: str) -> None:
    require_stage(state, "suitability", "suitability")

    roles = state.suitability.get("roles", [])
    known_titles = {r["role_title"].lower() for r in roles}
    if target_role.lower() not in known_titles:
        raise _conflict(
            missing_stage="suitability",
            message=(
                f"'{target_role}' was not among the roles scored in the suitability stage. "
                "Re-run suitability including this role, or choose one of the already-scored roles."
            ),
        )
