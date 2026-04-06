import asyncio
import os
from datetime import datetime, timedelta

from app.models.room import Room

ROOM_TTL_HOURS = float(os.getenv("ROOM_TTL_HOURS", "3"))
EXPIRY_CHECK_INTERVAL = int(os.getenv("EXPIRY_CHECK_INTERVAL_SECONDS", "60"))


# The application's runtime room registry.
# Responsible for storing, retrieving, and expiring Room objects in
# process memory, and for running the background TTL sweep that evicts
# rooms whose last_activity_at has passed the configured threshold.
class InMemoryStore:
    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._task: asyncio.Task | None = None

    def _get_or_create_lock(self, room_id: str) -> asyncio.Lock:
        if room_id not in self._locks:
            self._locks[room_id] = asyncio.Lock()
        return self._locks[room_id]

    def get_room(self, room_id: str) -> Room | None:
        return self._rooms.get(room_id)

    def save_room(self, room: Room) -> None:
        self._get_or_create_lock(room.id)  # ensure lock exists before any handler uses it
        room.touch()
        self._rooms[room.id] = room

    def delete_room(self, room_id: str) -> None:
        self._rooms.pop(room_id, None)
        self._locks.pop(room_id, None)

    def all_rooms(self) -> list[Room]:
        return list(self._rooms.values())

    async def start_expiry_task(self) -> None:
        self._task = asyncio.create_task(self._expiry_loop())

    async def stop_expiry_task(self) -> None:
        if self._task:
            self._task.cancel()

    async def _expiry_loop(self) -> None:
        while True:
            await asyncio.sleep(EXPIRY_CHECK_INTERVAL)
            await self._evict_expired()

    async def _evict_expired(self) -> None:
        cutoff = datetime.utcnow() - timedelta(hours=ROOM_TTL_HOURS)
        expired = [
            room_id
            for room_id, room in self._rooms.items()
            if room.last_activity_at < cutoff
        ]
        for room_id in expired:
            async with self._get_or_create_lock(room_id):
                # Double-check: a handler may have updated activity or deleted the room
                # between the snapshot above and acquiring the lock.
                if room_id in self._rooms and self._rooms[room_id].last_activity_at < cutoff:
                    del self._rooms[room_id]
                    self._locks.pop(room_id, None)


store = InMemoryStore()
