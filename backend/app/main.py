import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import rooms
from app.store.memory import store

app = FastAPI(title="Agile Planning Poker", version="0.1.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms.router, prefix="/api")


@app.on_event("startup")
async def startup():
    await store.start_expiry_task()


@app.on_event("shutdown")
async def shutdown():
    await store.stop_expiry_task()


@app.get("/api/health")
async def health():
    return {"status": "ok"}
