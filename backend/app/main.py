import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import rooms
from app.limiter import limiter
from app.store.memory import store

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost").split(",")

app = FastAPI(title="Agile Planning Poker", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# SlowAPIMiddleware must be added before CORSMiddleware — Starlette applies
# middleware in reverse registration order, so CORS ends up outermost and
# handles OPTIONS preflight before rate-limit logic runs.
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(rooms.router, prefix="/api")


@app.on_event("startup")
async def startup():
    await store.start_expiry_task()


@app.on_event("shutdown")
async def shutdown():
    await store.stop_expiry_task()


@app.get("/api/health")
@limiter.limit("120/minute")
async def health(request):  # noqa: ANN001
    return {"status": "ok"}
