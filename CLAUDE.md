# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgilePlanningPoker is a real-time planning poker app for agile teams.
- **Frontend**: Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS
- **Backend**: Python, FastAPI, SSE via `sse-starlette`
- **Deployment**: Docker + docker-compose, Nginx reverse proxy

## Directory Structure

```
backend/         FastAPI app + pytest tests
  app/
    api/         Route handlers
    models/      Pydantic models (Room, Participant, Round, CardSet)
    store/       In-memory store with TTL expiry
    events/      SSE broadcaster
  tests/
    api/         API endpoint tests
    store/       Store unit tests
    models/      Model unit tests

frontend/        Vue 3 app + Vitest tests
  src/
    pages/       HomePage.vue, RoomPage.vue
    stores/      Pinia stores (user, room)
    router/      Vue Router
    components/  Reusable components (to be added)
  tests/
    unit/
      stores/    Store unit tests
      components/ Component tests

docker/          nginx.conf
docker-compose.yml          Production
docker-compose.override.yml Local dev (hot reload)
.env.example                Environment variable docs
```

## Running Locally (Development)

```bash
# Start everything with hot reload
docker compose up

# OR run services individually:

# Backend
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
# → http://localhost:5173 (proxies /api to :8000)
```

## Running Tests

```bash
# Backend (from /backend)
pip install -e ".[dev]"
pytest                        # all tests
pytest tests/api/             # API tests only
pytest tests/store/           # store tests only
pytest --cov                  # with coverage

# Frontend (from /frontend)
npm install
npm test                      # run once
npm run test:watch            # watch mode
npm run test:coverage         # with coverage
```

## Production Build

```bash
docker compose -f docker-compose.yml up --build
# → http://localhost (port configurable via APP_PORT in .env)
```

## Environment Variables

Copy `.env.example` to `.env` and adjust. Key variables:
- `ROOM_TTL_HOURS` — room expiry in hours (default: 3)
- `EXPIRY_CHECK_INTERVAL_SECONDS` — expiry sweep interval (default: 60)
- `ALLOWED_ORIGINS` — comma-separated CORS origins
- `APP_PORT` — host port for the app (default: 80)
