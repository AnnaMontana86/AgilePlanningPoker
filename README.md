# Agile Planning Poker

A lightweight, real-time planning poker app for agile teams. No user accounts required — just create a room, share the link, and start estimating.

## Features

- Create rooms with a custom name and card set (Fibonacci, T-shirt sizes, powers of 2, or custom)
- Join via invite link using a nickname
- Real-time updates via Server-Sent Events (SSE)
- Owner controls: reveal cards, start new rounds, kick participants
- Vote and retract your vote before cards are revealed
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
│   │   ├── pages/      # HomePage, RoomPage
│   │   ├── stores/     # Pinia stores (user, room)
│   │   ├── router/     # Vue Router
│   │   └── components/ # Reusable components
│   └── tests/
│       └── unit/
│           ├── stores/     # Store unit tests
│           └── components/ # Component tests
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
git clone https://github.com/your-username/AgilePlanningPoker.git
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

**Backend**

```bash
cd backend
pip install -e ".[dev]"

pytest                  # all tests
pytest tests/api/       # API tests only
pytest tests/store/     # store tests only
pytest --cov            # with coverage report
```

**Frontend**

```bash
cd frontend
npm install

npm test                  # run once
npm run test:watch        # watch mode
npm run test:coverage     # with coverage report
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
| `POST` | `/api/rooms/{id}/vote` | Cast or retract a vote |
| `POST` | `/api/rooms/{id}/reveal` | Reveal cards (owner only) |
| `POST` | `/api/rooms/{id}/new-round` | Start a new round (owner only) |
| `DELETE` | `/api/rooms/{id}/participants/{pid}` | Kick a participant (owner only) |
| `GET` | `/api/rooms/{id}/events` | SSE stream for real-time room updates |

Full interactive API documentation is available at `/docs` when the backend is running.

## Deployment

The app is designed to run on a single machine via docker-compose and is ready for on-premise or cloud hosting. For production:

1. Set `ALLOWED_ORIGINS` to your domain in `.env`
2. Place a TLS-terminating reverse proxy (e.g. Nginx, Traefik, Caddy) in front of the container
3. Run `docker compose -f docker-compose.yml up -d --build`

## License

[MIT](LICENSE)
