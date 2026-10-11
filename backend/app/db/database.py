from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# pool_pre_ping is not a tuning knob here, it prevents a hard failure.
# A pooled connection that the server has already closed - an idle
# timeout, a database restart, a managed-Postgres failover, all routine
# on a hosted platform - looks alive to the pool. Without the pre-ping,
# the next request to borrow it raises
#     OperationalError: server closed the connection unexpectedly
# and the user sees a failed login that works on a second try. The ping
# is one round trip (~4 ms locally) and transparently replaces a dead
# connection instead.
#
# pool_recycle retires connections before they get old enough for an
# upstream idle timeout to close them, so the pre-ping rarely has to.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
