FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user. Nothing is written to disk at runtime (resume
# parsing is in-memory), but /app is chowned anyway so CPython can still
# write __pycache__ alongside the sources. uvicorn binds >1024, so it
# needs no privileged port.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

# Shell form (not the JSON array form) so ${PORT:-8000} actually expands -
# Railway injects its own $PORT at runtime; the :-8000 fallback keeps
# local `docker-compose up` (which never sets $PORT) working unchanged.
# `exec` replaces the shell with uvicorn as PID 1 so SIGTERM on
# redeploy/restart reaches uvicorn directly instead of being swallowed by
# the shell wrapper. Only safe at 1 replica - scaling this service would
# race multiple `alembic upgrade head` runs against the same DB on boot.
#
# The seed step is NOT optional: migrations create the skills/jobs/edges
# tables but insert no rows, and every pipeline stage scores against that
# knowledge base. Without it the API comes up healthy and returns 200 with
# empty results for every upload. `app.db.seed` is upsert-keyed (see its
# docstring), so re-running it on each boot/redeploy is idempotent. It is
# chained with && so a seed failure crash-loops loudly rather than
# serving an empty knowledge base silently.
CMD ["sh", "-c", "alembic upgrade head && python -m app.db.seed && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
