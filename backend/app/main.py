from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, jobs, recommendations, roadmap, resume, pipeline
from app.core.config import settings
# Schema is managed by Alembic now (see backend/alembic/). Run
# `alembic upgrade head` to create/update tables instead of relying on
# create_all() here — otherwise a missing migration can go unnoticed.

app = FastAPI(title="CareerLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
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
