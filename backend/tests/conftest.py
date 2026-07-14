"""
Shared test fixtures for the pipeline test suite.

Both unit tests (direct service-function calls) and integration tests
(FastAPI TestClient) run against a real test Postgres database
(careerlens_test) rather than mocks - the 7 stage functions do real
query/graph work (category grouping, graph traversal, prerequisite depth
ordering) that IS their bug surface, so mocking the ORM would mostly test
the mock's own wiring instead.

Env vars are set here, before any `app.*` import in this file (pydantic-
settings resolves `.env` relative to CWD at instantiation time, which
breaks if pytest is ever invoked from somewhere other than backend/ -
setting every required var explicitly sidesteps that entirely).
"""
import os

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://srisaicharanp@localhost:5432/careerlens_test"
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.db.database import get_db  # noqa: E402
from app.db.models import Job, Skill, SkillEdge, User  # noqa: E402
from app.main import app  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def engine():
    return create_engine(settings.DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(engine):
    """Schema is Alembic-managed (see app/main.py's own comment on this) -
    run real migrations against the test DB once per session rather than
    Base.metadata.create_all(), so schema drift can't go unnoticed here
    either."""
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.upgrade(cfg, "head")


@pytest.fixture()
def db_session(engine):
    """Join a Session into an external transaction with a SAVEPOINT that
    auto-restarts on every commit. Route handlers call db.commit()
    internally (get_or_create_state, every stage route) - without the
    restarting SAVEPOINT, the first commit ends the outer transaction and
    fixture/test data leaks into the next test instead of rolling back."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = Session(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------
# Deterministic fixture data - small, hand-built, independent of
# backend/data/seed/*.json (production seed data can change later without
# breaking these tests).
# ---------------------------------------------------------------------


@pytest.fixture()
def skills(db_session):
    rows = {}

    def make(name, category, market_demand, avg_learn_weeks=4):
        skill = Skill(
            name=name,
            aliases=[],
            category=category,
            market_demand=market_demand,
            avg_learn_weeks=avg_learn_weeks,
        )
        db_session.add(skill)
        rows[name] = skill
        return skill

    make("Python", "backend", 0.90, 4)
    make("FastAPI", "backend", 0.80, 3)
    make("React", "frontend", 0.70, 4)
    make("TypeScript", "frontend", 0.75, 3)
    make("SQL", "data", 0.65, 4)
    make("Docker", "devops", 0.60, 6)
    make("Kubernetes", "devops", 0.85, 8)
    make("Helm", "devops", 0.55, 3)
    make("GraphQL", "frontend", 0.50, 4)  # zero edges anywhere - unreachable in graph

    db_session.commit()
    for skill in rows.values():
        db_session.refresh(skill)
    return rows


@pytest.fixture()
def skill_edges(db_session, skills):
    # Two-hop prerequisite chain: Docker -> Kubernetes -> Helm. Keep this
    # acyclic - don't add a reverse/other edge (see roadmap cycle test,
    # which deliberately builds its own separate cycle instead).
    edges = [
        SkillEdge(
            parent_skill_id=skills["Docker"].id,
            child_skill_id=skills["Kubernetes"].id,
            relation_type="prerequisite",
            weight=1.0,
        ),
        SkillEdge(
            parent_skill_id=skills["Kubernetes"].id,
            child_skill_id=skills["Helm"].id,
            relation_type="prerequisite",
            weight=1.0,
        ),
    ]
    db_session.add_all(edges)
    db_session.commit()
    return edges


@pytest.fixture()
def jobs(db_session, skills):
    rows = []

    def make(title, company, description, required_skills):
        job = Job(
            title=title,
            company=company,
            description=description,
            required_skills=required_skills,
            experience_years=1,
            salary_min=50000,
            salary_max=90000,
            location="Remote",
            job_type="full_time",
        )
        db_session.add(job)
        rows.append(job)
        return job

    make(
        "Backend Engineer",
        "Acme Co",
        "Build and maintain scalable backend REST APIs using Python and FastAPI. "
        "Deploy services with Docker and orchestrate with Kubernetes.",
        ["Python", "FastAPI", "Docker", "Kubernetes"],
    )
    make(
        "Backend Engineer",
        "Beta Inc",
        "Manage Kubernetes clusters at scale using Helm charts for templating.",
        ["Helm"],
    )
    make(
        "Frontend Engineer",
        "Acme Co",
        "Build accessible, responsive user interfaces with React, TypeScript, "
        "and modern component patterns.",
        ["React", "TypeScript"],
    )
    make(
        "Data Analyst",
        "Gamma LLC",
        "Write complex SQL queries to analyze large datasets and build "
        "reporting dashboards.",
        ["SQL"],
    )

    db_session.commit()
    return rows


@pytest.fixture()
def test_user(db_session):
    user = User(
        email="pipeline-tester@example.com",
        name="Pipeline Tester",
        hashed_password="not-a-real-hash",
        experience_years=2,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def fresh_user(db_session):
    """A second user with no AnalysisState row at all - for the
    "no resume uploaded yet" prerequisite-violation tests."""
    user = User(
        email="fresh-user@example.com",
        name="Fresh User",
        hashed_password="not-a-real-hash",
        experience_years=0,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_headers_for(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(test_user):
    return _auth_headers_for(test_user)


@pytest.fixture()
def fresh_auth_headers(fresh_user):
    return _auth_headers_for(fresh_user)


GOOD_RESUME_TEXT = (
    "Experienced backend engineer with 2 years building REST APIs in Python "
    "and FastAPI. Deployed services using Docker and Kubernetes. Increased "
    "API throughput by 40% and led a small team of 3 engineers.\n\n"
    "Contact: jane@example.com, (555) 123-4567\n\n"
    "Skills: Python, FastAPI, Docker, Kubernetes\n\n"
    "Experience: Built and maintained backend services for 2 years.\n\n"
    "Education: BS in Computer Science.\n\n"
    "Projects: Led migration of legacy services to Kubernetes."
)
