# Render deployment steps

## Overview

This project contains a `backend` (FastAPI) and a `frontend` (Vite + React). We'll deploy both to Render using Docker images built from the provided `Dockerfile`s.

## High-level steps

1. Create a Render account and log in.
2. Create a PostgreSQL managed database on Render (note the DATABASE_URL).
3. Create a Redis instance on Render (note REDIS_URL) or use an external Redis.
4. Create a new Web Service for the `backend`:
   - Connect your GitHub repo and select the `backend` folder.
   - Build command: (Render will use the Dockerfile) — no additional build command required.
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers`
   - Env vars to set (in Render dashboard):
     - `DATABASE_URL` (from managed Postgres)
     - `REDIS_URL` (optional)
     - `SECRET_KEY` (random secret)
     - `ALLOWED_HOSTS` (your domain)
     - Any other settings in `app/core/config.py`

5. Create a Static Site for the `frontend` (recommended) or a Web Service using Docker:
   - Static Site: connect repo, set root to `/frontend`, build command `npm ci && npm run build`, publish directory `frontend/dist`.
   - Or Web Service: use `frontend/Dockerfile` (then Render will build and serve via nginx).

6. Run database migrations on startup (recommended):
   - Option A: add a startup command to run alembic migrations before starting the app in the `backend` service.
   - Option B: run migrations manually from a one-off shell on Render.

## Notes on production readiness

- Ensure `backend/requirements.txt` lists all runtime packages (updated with `qrcode` and `pillow`).
- If you need uploads or persistent files, use object storage (S3) or Render hooks.
- Configure domain and DNS in Render; enable automatic HTTPS.

## Commands (local Docker build test)

Build backend image locally for a quick smoke test:

```bash
cd backend
docker build -t ticket-backend:local .
docker run -p 8001:8000 --env-file .env -e DATABASE_URL="sqlite:///./test.db" ticket-backend:local
```

Build frontend image locally:

```bash
cd frontend
docker build -t ticket-frontend:local .
docker run -p 8080:80 ticket-frontend:local
```

If you want, I can create a `render.yaml` to define both services as code — tell me and I will add it.
