import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import auth, users, jobs, recommendations, roadmap, resume, pipeline
from app.core.config import settings
from app.db.database import get_db
# Schema is managed by Alembic now (see backend/alembic/). Run
# `alembic upgrade head` to create/update tables instead of relying on
# create_all() here — otherwise a missing migration can go unnoticed.

logger = logging.getLogger("careerlens")

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _log_effective_cors() -> None:
    """
    A wrong CORS_ORIGINS fails in the browser, not on the server, so the
    backend looks perfectly healthy while every frontend request is
    blocked. Log the effective list at boot, and say so plainly when a
    production instance is still pointing at a localhost origin.
    """
    origins = settings.cors_origin_list
    logger.info("CORS allowed origins: %s", origins or "(none)")

    if settings.ENVIRONMENT.lower() != "production":
        return

    local = [o for o in origins if (urlparse(o).hostname or "") in _LOCAL_HOSTS]
    if local or not origins:
        logger.warning(
            "ENVIRONMENT=production but CORS_ORIGINS is %s. The deployed "
            "frontend will be blocked by the browser until CORS_ORIGINS is "
            "set to its real URL.",
            f"still localhost-only: {local}" if local else "empty",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log_effective_cors()
    yield


app = FastAPI(title="CareerLens API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["roadmap"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])


@app.get("/")
def root():
    return {"status": "CareerLens API running", "docs": "/docs"}


@app.get("/health")
def health(response: Response, db: Session = Depends(get_db)):
    """
    Readiness probe for the deployment platform. Checks the database
    round-trip rather than just returning 200, so a container that booted
    but cannot reach Postgres is reported as unhealthy instead of being
    sent traffic it will only fail.
    """
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("health check: database round-trip failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "database": "unreachable"}

    return {"status": "ok", "database": "ok"}
