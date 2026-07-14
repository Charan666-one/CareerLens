# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

CareerLens: FastAPI + PostgreSQL backend, React/TypeScript/Vite frontend. Users upload a resume and run it
through a 7-stage analysis pipeline that extracts skills, scores role suitability, finds skill gaps, and
generates a learning roadmap and job recommendations. Backend is the mature half of the codebase; the
frontend is still an early UI shell not yet wired to the pipeline endpoints.

`README.md` at the repo root has a detailed, actively-maintained status dashboard (feature completion %,
known bugs, next tasks) — check it for current project state before making claims about what is or isn't
implemented. Ignore `README_AI.md`; it describes an early scaffolding stage that predates the pipeline
implementation and is stale.

## Commands

### Backend (from `backend/`, with venv active)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head              # apply migrations
alembic revision --autogenerate -m "message"   # create a new migration after model changes
python -m app.db.seed             # load seed skills/edges/jobs into the DB

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000   # dev server, docs at /docs

pytest                            # run all tests
pytest tests/test_engine_scoring.py            # single file
pytest tests/test_engine_scoring.py::test_final_score_matches_manual_weighted_sum  # single test
```

Postgres must be running first: `docker compose up -d postgres` (from repo root). Backend config is loaded
from `backend/.env` via `pydantic-settings` (`app/core/config.py`); required vars: `DATABASE_URL`,
`SECRET_KEY`. See `.env.example` at repo root.

### Frontend (from `frontend/`)

```bash
npm install
npm run dev       # Vite dev server on :5173
npm run build     # tsc typecheck + production build
```

No frontend test runner or lint script is configured in `package.json`.

### Full stack via Docker

```bash
docker compose up --build
```

## Architecture

### The 7-stage pipeline (the core of the backend)

This is the thing most work will touch. All logic lives under `backend/app/services/`; routes in
`backend/app/api/routes/pipeline.py` are intentionally thin — they only validate auth, fetch state, check
prerequisites, call one service function, persist, and return. **Business logic never lives in the route
file.**

State is a single row per user in `AnalysisState` (`app/db/models.py`), not separate tables per stage. Each
stage owns exactly one JSON column plus a `_updated_at` timestamp, and a stage's route only ever writes its
own column — running a later stage never overwrites an earlier one's data. The raw resume text is captured
once (`resume_text` column) during the profile stage and reused by later stages for TF-IDF similarity
scoring, instead of being re-derived from the profile JSON.

Stages, in dependency order (`POST /api/pipeline/<stage>`):

1. **profile** — upload resume file → `nlp/resume_parser.py` extracts text → `nlp/skill_normalizer.py`
   matches skills against the seeded skill lookup → `profile/builder.py` builds the identity profile.
2. **strengths** — requires `profile`. `profile/strengths.py` analyzes the extracted skills.
3. **suitability** — requires `profile`. `recommendation/engine.py::score_roles` scores candidate roles
   using a weighted blend of text similarity (TF-IDF, `nlp/text_similarity.py`), skill-graph proximity
   (`graph/skill_graph.py`), and market demand. Weights are named constants (`TEXT_WEIGHT`, `GRAPH_WEIGHT`,
   `DEMAND_WEIGHT`) that must sum to 1.0 — see `tests/test_engine_scoring.py`.
4. **skill-gap** — requires the target role to have been scored in `suitability`
   (`pipeline/state.py::require_role_in_suitability`). `graph/skill_graph.py::weighted_skill_gap` combines
   text, graph-proximity, and demand weights (its own separate set of constants) to rank missing skills.
5. **roadmap** — requires `skill_gap`. `roadmap/generator.py::sequence_roadmap` orders missing skills into
   a learning sequence.
6. **resume-score** — independent of the other stages (only needs an uploaded file).
   `resume_score/scorer.py` scores resume quality directly.
7. **recommendations** — requires all six prior stages present (profile, strengths, suitability, skill_gap,
   roadmap, resume_score). `recommendation/explainer.py::build_recommendations` assembles the final
   explained job recommendations.

Prerequisite checks are centralized in `app/services/pipeline/state.py` (`require_stage`, `require_all`,
`require_role_in_suitability`) so every route enforces "prior stage must exist" the same way. A missing
prerequisite raises `409` with `{"error": "state_conflict", "missing_prerequisite": ..., "message": ...}`.

When adding a new stage or changing an existing one's output shape: update the JSON column's implicit
schema, the corresponding Pydantic response model in `app/schemas/pipeline.py`, and any stage that consumes
it downstream (e.g. changing `profile`'s `extracted_skills` shape affects strengths, suitability, and
skill-gap).

### Legacy / non-pipeline routes

`app/api/routes/resume.py`, `recommendations.py`, `roadmap.py` predate the pipeline and implement a simpler,
non-stateful version of similar functionality directly against `CandidateProfile`/`Recommendation`/`Roadmap`
tables (as opposed to `AnalysisState`). `jobs.py` and `users.py` are still empty stub routers (just
`APIRouter()`, no endpoints) — mounted in `main.py` but non-functional.

### Database

SQLAlchemy models in `app/db/models.py`; **schema is managed by Alembic, not `Base.metadata.create_all()`**
(see the comment in `app/main.py`) — always add a migration when changing a model. `alembic/env.py` reads
`DATABASE_URL` from the app's own settings rather than a separate copy in `alembic.ini`.

Seed data (`backend/data/seed/{skills,jobs,edges}.json`) is the knowledge base the pipeline scores against:
skills with market demand/learn-time, jobs with required skills, and `edges.json` defining prerequisite
relationships between skills (consumed by `graph/skill_graph.py` via `networkx`).

### Auth

JWT bearer tokens. `app/core/security.py` has hash/verify/encode/decode helpers; `app/core/deps.py`'s
`get_current_user` is the dependency every protected route uses. Token subject (`sub`) is the user's UUID.

### Frontend

Routing shell in `App.tsx` (React Router) with placeholder pages under `src/pages/`
(Dashboard/Jobs/Login/Register/Roadmap). Auth state in `src/store/auth.ts` (Zustand). API calls go through
the shared axios instance in `src/services/api.ts`, which attaches the bearer token. Pages are not yet
wired to the pipeline endpoints — this is the main gap between backend and frontend maturity.
