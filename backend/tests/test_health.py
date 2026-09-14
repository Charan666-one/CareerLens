"""
Tests for the deployment probes in app/main.py.

These cover the two things a platform health check actually has to get
right: reporting unhealthy when Postgres is unreachable (rather than
returning 200 and being sent traffic it will only fail), and warning when
a production instance is still configured with the localhost CORS default.
"""
import logging

from app.core.config import settings
from app.db.database import get_db
from app.main import _log_effective_cors, app


def test_health_reports_ok_when_database_is_reachable(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_reports_503_when_database_is_unreachable(client):
    """A booted container that cannot reach Postgres must fail its probe."""

    class UnreachableSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("connection refused")

    def override_get_db():
        yield UnreachableSession()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "database": "unreachable"}


def test_root_still_responds(client):
    assert client.get("/").status_code == 200


def _cors_warnings(caplog, environment, cors_origins):
    original = (settings.ENVIRONMENT, settings.CORS_ORIGINS)
    settings.ENVIRONMENT, settings.CORS_ORIGINS = environment, cors_origins
    try:
        with caplog.at_level(logging.WARNING, logger="careerlens"):
            caplog.clear()
            _log_effective_cors()
            return [r for r in caplog.records if r.levelno >= logging.WARNING]
    finally:
        settings.ENVIRONMENT, settings.CORS_ORIGINS = original


def test_production_with_localhost_cors_warns(caplog):
    warnings = _cors_warnings(caplog, "production", "http://localhost:5173")

    assert len(warnings) == 1
    assert "CORS_ORIGINS" in warnings[0].getMessage()


def test_production_with_empty_cors_warns(caplog):
    assert len(_cors_warnings(caplog, "production", "")) == 1


def test_production_with_a_real_origin_does_not_warn(caplog):
    assert _cors_warnings(caplog, "production", "https://careerlens.example.com") == []


def test_development_with_localhost_cors_does_not_warn(caplog):
    """The localhost default is correct locally - it must not cry wolf."""
    assert _cors_warnings(caplog, "development", "http://localhost:5173") == []


def test_cors_origin_list_splits_and_strips():
    original = settings.CORS_ORIGINS
    settings.CORS_ORIGINS = " https://a.example.com , https://b.example.com ,"
    try:
        assert settings.cors_origin_list == [
            "https://a.example.com",
            "https://b.example.com",
        ]
    finally:
        settings.CORS_ORIGINS = original
