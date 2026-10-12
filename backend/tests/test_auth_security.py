"""
Tests for the cost and timing characteristics of the auth routes.

These pin down three things that are easy to regress silently: the bcrypt
cost factor (which is essentially all of login/register latency), the fact
that lowering it did not invalidate passwords hashed at the old cost, and
that a login for an unknown email still spends bcrypt time so it cannot be
distinguished from a wrong password.

Deliberately no wall-clock assertions - those are flaky on shared CI
runners. Each property is asserted structurally instead.
"""
from passlib.context import CryptContext

from app.api.routes import auth as auth_route
from app.core.security import (
    BCRYPT_ROUNDS,
    hash_password,
    verify_dummy_password,
    verify_password,
)
from app.db.database import engine


def _cost_of(hashed: str) -> int:
    """bcrypt stores its cost factor as the third $-delimited field."""
    return int(hashed.split("$")[2])


def test_new_hashes_use_the_configured_cost():
    assert BCRYPT_ROUNDS == 10, "raising this is fine, but it is the whole login latency"
    assert _cost_of(hash_password("a-real-password-123")) == BCRYPT_ROUNDS


def test_passwords_hashed_at_the_previous_cost_still_verify():
    """Lowering the cost must not lock out anyone who registered before it.

    bcrypt reads the cost from the stored hash, so old hashes keep working;
    this test is what proves the change was backward compatible rather than
    a silent mass password reset."""
    legacy = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12).hash("a-real-password-123")

    assert _cost_of(legacy) == 12
    assert verify_password("a-real-password-123", legacy) is True
    assert verify_password("the-wrong-password", legacy) is False


def test_dummy_verify_runs_and_returns_nothing():
    assert verify_dummy_password("anything-at-all") is None


def test_register_signs_the_new_user_straight_in(client):
    """Registering returns a working token, so there is no second sign-in.

    Asserts the token actually authenticates rather than merely being
    present - a well-formed but unusable token would pass a shape check
    and still leave the user stuck at the login form."""
    created = client.post(
        "/api/auth/register",
        json={"email": "straight.in@example.com", "password": "a-real-password-123", "name": "SI"},
    )
    assert created.status_code == 201

    token = created.json()["access_token"]
    assert created.json()["token_type"] == "bearer"

    whoami = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert whoami.status_code == 200
    assert whoami.json()["email"] == "straight.in@example.com"


def test_register_still_returns_every_user_field_it_used_to(client):
    """The token fields were added to the response, not swapped in for the
    user payload - anything reading id or email keeps working."""
    body = client.post(
        "/api/auth/register",
        json={"email": "additive@example.com", "password": "a-real-password-123", "name": "Add"},
    ).json()

    for field in ("id", "email", "name", "target_role", "experience_years", "created_at"):
        assert field in body, f"register response lost {field}"
    assert body["email"] == "additive@example.com"
    assert body["name"] == "Add"


def test_register_then_login_round_trip(client):
    body = {"email": "round.trip@example.com", "password": "a-real-password-123", "name": "RT"}

    created = client.post("/api/auth/register", json=body)
    assert created.status_code == 201

    signed_in = client.post(
        "/api/auth/login", json={"email": body["email"], "password": body["password"]}
    )
    assert signed_in.status_code == 200
    assert signed_in.json()["access_token"]


def test_login_for_unknown_email_still_spends_a_verify(client, monkeypatch):
    """The timing-oracle guard.

    Returning early for a missing user answered in ~7 ms against ~67 ms for
    a wrong password on a real account, which reliably leaks whether an
    email is registered. Assert the dummy verify is actually reached."""
    calls = []
    monkeypatch.setattr(
        auth_route, "verify_dummy_password", lambda plain: calls.append(plain)
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "no.such.user@example.com", "password": "a-real-password-123"},
    )

    assert response.status_code == 401
    assert calls == ["a-real-password-123"]


def test_wrong_password_and_unknown_email_are_indistinguishable(client):
    client.post(
        "/api/auth/register",
        json={"email": "real.user@example.com", "password": "a-real-password-123", "name": "R"},
    )

    wrong_password = client.post(
        "/api/auth/login",
        json={"email": "real.user@example.com", "password": "the-wrong-password"},
    )
    unknown_email = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "the-wrong-password"},
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_engine_pre_pings_so_a_dropped_connection_does_not_surface(client):
    """Without this, a connection closed server-side (idle timeout, database
    restart, failover) raises OperationalError on the next request and the
    user sees a login that only works on the second try."""
    assert engine.pool._pre_ping is True
