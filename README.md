# Ticket Booking System

A full-stack portfolio project for ticket booking and event management built with FastAPI, SQLAlchemy, PostgreSQL, Redis, and React/Vite.

## What is included

- FastAPI backend with authentication, venues, events, and booking endpoints
- SQLAlchemy models and repository/service layering
- JWT-based role authorization
- Redis-backed seat hold logic with a local in-memory fallback for development
- React + Vite frontend scaffold for local interaction
- Docker Compose orchestration for backend, frontend, PostgreSQL, and Redis

## Project structure

- `backend/` — FastAPI application and Python services
- `frontend/` — React + Vite UI
- `docker-compose.yml` — start the full stack together
- `docs/` — project documentation and diagrams

## Run the full stack

### Option 1: Docker Compose

```bash
docker compose up --build
```

This starts:

- PostgreSQL on port `5432`
- Redis on port `6379`
- Backend on port `8000`
- Frontend on port `5173`

### Option 2: Local development

Backend:

```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Verify the backend

```bash
cd backend
.venv\Scripts\python.exe -m pytest -q
```

## Verify the frontend

```bash
cd frontend
npm run build
```

## Health check

```bash
curl http://127.0.0.1:8000/health
```

## Deploy to Render (quick)

1. Push this repository to GitHub.
2. Create a Render account and a managed Postgres database; copy the `DATABASE_URL`.
3. Import the GitHub repo into Render or use the `render.yaml` manifest included in this repo.
4. Backend:
   - Create a Web Service using the `backend` folder and Docker. Render will use `backend/Dockerfile`.
   - Start command:
     ```
     sh -lc "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"
     ```
   - Set environment variables in the Render service (see `.env.template`).
5. Frontend:
   - Create a Static Site in Render using the `frontend` folder.
   - Build command: `npm ci && npm run build` and publish directory: `frontend/dist`.
6. Add a custom domain in Render and enable HTTPS. Share the frontend URL in the README for evaluators.

See `DEPLOY_RENDER.md` for detailed steps and `render.yaml` to deploy services as code.
