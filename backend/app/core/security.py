from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# bcrypt's cost factor is a deliberate speed/strength trade-off, and it is
# the single biggest component of login and register latency - essentially
# all of it, since the email lookup is an index scan.
#
# Measured on this codebase, per verify:
#     cost 12 -> ~227 ms        cost 11 -> ~131 ms        cost 10 -> ~67 ms
#
# 10 is the floor OWASP recommends for bcrypt, so this stays within current
# guidance while being ~3.4x faster than passlib's default of 12. It matters
# more than it looks on a small instance: bcrypt releases the GIL, so
# hashing parallelises across cores, but on a 1-vCPU container eight
# simultaneous logins cost 8x this number for whoever is last in line.
#
# Raising it is a one-line change here. Existing hashes are unaffected -
# bcrypt stores its cost inside the hash, so passwords hashed at 12 keep
# verifying after this drops to 10; only newly set passwords use the new
# cost.
BCRYPT_ROUNDS = 10

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS,
)

# A real bcrypt hash of a random throwaway string, used only to burn the
# same CPU time as a genuine verify when the submitted email matches no
# user (see verify_dummy_password). It protects nothing and unlocks
# nothing, so it is safe to keep in source.
_DECOY_HASH = "$2b$10$8pJ2QTWui8W0TmbPTAXDLOJ3EGsVl5qe35GRvqj2l/NtFcStzw/oC"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def verify_dummy_password(plain: str) -> None:
    """
    Spend a verify's worth of time against a throwaway hash, always
    returning nothing.

    Without this, a login for an unknown email skips bcrypt entirely and
    answers in ~7 ms, while a wrong password for a *real* account takes
    ~67 ms. That gap is a reliable oracle for whether an email has an
    account, so the login route calls this on the no-such-user path to
    keep both answers the same shape and roughly the same duration.
    """
    pwd_context.verify(plain, _DECOY_HASH)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises jose.JWTError if the token is invalid or expired."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
