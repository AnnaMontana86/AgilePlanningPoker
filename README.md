# Agile Planning Poker

A lightweight, real-time planning poker app for agile teams. No user accounts required — just create a room, share the link, and start estimating.

## Features

- Create rooms with a custom name and card set (Fibonacci, T-shirt sizes, powers of 2, or custom)
- Join via invite link or QR code using a nickname
- Real-time updates via Server-Sent Events (SSE)
- **Owner controls:** reveal cards, start new rounds, revote, set a countdown timer, kick or suspend participants, promote participants to co-owner
- **Co-owner role:** can reveal cards and suspend regular participants
- **Topics / backlog:** add, reorder, and select topics to keep the session focused
- **Shared note:** owner can write a session note (with image attachments) visible to all participants
- **Emoji mood reactions** during voting
- **Focus Music** to keep the team in the zone while thinking
- Vote and retract your vote before cards are revealed
- Highest/lowest vote indicators and numeric average after reveal
- Light and dark mode
- Mobile-friendly layout

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vite, Pinia, Vue Router, Tailwind CSS |
| Backend | Python, FastAPI, sse-starlette |
| Containerization | Docker, docker-compose |
| Reverse proxy | Nginx |

## Project Structure

```
AgilePlanningPoker/
├── backend/
│   ├── app/
│   │   ├── api/        # REST route handlers
│   │   ├── models/     # Pydantic data models
│   │   ├── store/      # In-memory room store with TTL expiry
│   │   └── events/     # SSE broadcaster
│   └── tests/
│       ├── api/        # API endpoint tests
│       ├── store/      # Store unit tests
│       └── models/     # Model unit tests
├── frontend/
│   ├── src/
│   │   ├── pages/       # HomePage, RoomPage
│   │   ├── stores/      # Pinia stores (user, room, theme)
│   │   ├── composables/ # useTimer, useVoteAnalysis, useShare, …
│   │   ├── router/      # Vue Router
│   │   └── components/  # NoteSidebar, TopicsSidebar, TimerDialog, …
│   └── tests/
│       ├── unit/        # Vitest unit tests (stores, components)
│       └── e2e/         # Playwright end-to-end tests
├── docker/
│   └── nginx.conf
├── docker-compose.yml          # Production
├── docker-compose.override.yml # Local dev (hot reload)
└── .env.example
```

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/)

### Run with Docker (recommended)

```bash
# Clone the repository
git clone https://github.com/AnnaMontana86/AgilePlanningPoker.git
cd AgilePlanningPoker

# Optional: copy and adjust environment variables
cp .env.example .env

# Start with hot reload (uses docker-compose.override.yml automatically)
docker compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

For a production-like build (no hot reload, served via Nginx on port 80):

```bash
docker compose -f docker-compose.yml up --build
# → http://localhost
```

### Run without Docker

**Backend**

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

The Vite dev server proxies `/api` requests to the backend on port 8000 automatically.

## Running Tests

**Backend (pytest)**

```bash
cd backend
pip install -e ".[dev]"

pytest                  # all tests
pytest tests/api/       # API tests only
pytest tests/store/     # store tests only
pytest --cov            # with coverage report
```

**Frontend unit tests (Vitest)**

```bash
cd frontend
npm install

npm test                  # run once
npm run test:watch        # watch mode
npm run test:coverage     # with coverage report
```

**Frontend end-to-end tests (Playwright)**

Requires the full stack to be running (`docker compose up`).

```bash
cd frontend

npm run test:e2e          # headless
npm run test:e2e:ui       # Playwright UI mode
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed:

| Variable | Default | Description |
|---|---|---|
| `ROOM_TTL_HOURS` | `3` | Hours of inactivity before a room expires |
| `EXPIRY_CHECK_INTERVAL_SECONDS` | `60` | How often to sweep for expired rooms |
| `ALLOWED_ORIGINS` | `http://localhost` | Comma-separated list of allowed CORS origins |
| `APP_PORT` | `80` | Host port for the production container |

## API Overview

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/card-sets` | List predefined card sets |
| `POST` | `/api/rooms` | Create a room |
| `GET` | `/api/rooms/{id}` | Get room state |
| `POST` | `/api/rooms/{id}/join` | Join a room |
| `POST` | `/api/rooms/{id}/leave` | Leave a room |
| `POST` | `/api/rooms/{id}/vote` | Cast or retract a vote |
| `POST` | `/api/rooms/{id}/reveal` | Reveal cards (owner/co-owner) |
| `POST` | `/api/rooms/{id}/new-round` | Start a new round (owner only) |
| `POST` | `/api/rooms/{id}/retry` | Reset votes for a revote (owner only) |
| `POST` | `/api/rooms/{id}/participants/{pid}/kick` | Kick a participant (owner only) |
| `POST` | `/api/rooms/{id}/participants/{pid}/suspend` | Suspend a participant (owner/co-owner) |
| `POST` | `/api/rooms/{id}/participants/{pid}/promote` | Promote to co-owner (owner only) |
| `POST` | `/api/rooms/{id}/topics` | Add a topic to the backlog |
| `POST` | `/api/rooms/{id}/topics/reorder` | Reorder the topic backlog |
| `POST` | `/api/rooms/{id}/topics/{tid}/select` | Set the active topic |
| `DELETE` | `/api/rooms/{id}/topics/{tid}` | Remove a topic |
| `POST` | `/api/rooms/{id}/note` | Update the shared room note |
| `POST` | `/api/rooms/{id}/timer/start` | Start a countdown timer (owner only) |
| `POST` | `/api/rooms/{id}/timer/stop` | Stop the countdown timer (owner only) |
| `POST` | `/api/rooms/{id}/emoji` | Set or clear your emoji reaction |
| `GET` | `/api/rooms/{id}/events` | SSE stream for real-time room updates |

Full interactive API documentation is available at `/docs` when the backend is running.

## Deployment

The app runs as a single Docker container (Nginx + FastAPI via Gunicorn) and is straightforward to self-host or deploy to any platform that supports Docker.

1. Set `ALLOWED_ORIGINS` to your domain in `.env`
2. Place a TLS-terminating reverse proxy (e.g. Nginx, Traefik, Caddy) in front of the container, or use a platform that handles TLS automatically
3. Run `docker compose -f docker-compose.yml up -d --build`

## License

[MIT](LICENSE)
