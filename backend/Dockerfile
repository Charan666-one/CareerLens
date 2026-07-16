FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Shell form (not the JSON array form) so ${PORT:-8000} actually expands -
# Railway injects its own $PORT at runtime; the :-8000 fallback keeps
# local `docker-compose up` (which never sets $PORT) working unchanged.
# `exec` replaces the shell with uvicorn as PID 1 so SIGTERM on
# redeploy/restart reaches uvicorn directly instead of being swallowed by
# the shell wrapper. Only safe at 1 replica - scaling this service would
# race multiple `alembic upgrade head` runs against the same DB on boot.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
