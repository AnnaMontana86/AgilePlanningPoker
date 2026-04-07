from datetime import datetime, timedelta, timezone

import pytest

from app.models.card_set import CardSet
from app.models.room import Room
from app.store.memory import InMemoryStore


def _make_room(**kwargs) -> Room:
    defaults = dict(name="Test", card_set=CardSet(name="fib", cards=["1", "2", "3"]))
    defaults.update(kwargs)
    return Room(**defaults)


class TestInMemoryStore:
    def setup_method(self):
        self.store = InMemoryStore()

    def test_save_and_get_room(self):
        room = _make_room()
        self.store.save_room(room)
        assert self.store.get_room(room.id) is room

    def test_get_nonexistent_room_returns_none(self):
        assert self.store.get_room("no-such-id") is None

    def test_delete_room(self):
        room = _make_room()
        self.store.save_room(room)
        self.store.delete_room(room.id)
        assert self.store.get_room(room.id) is None

    def test_delete_nonexistent_room_is_safe(self):
        self.store.delete_room("ghost")  # should not raise

    @pytest.mark.anyio
    async def test_expired_rooms_are_evicted(self):
        room = _make_room()
        self.store.save_room(room)
        # Backdate last activity beyond TTL
        room.last_activity_at = datetime.now(timezone.utc) - timedelta(hours=4)
        await self.store._evict_expired()
        assert self.store.get_room(room.id) is None

    @pytest.mark.anyio
    async def test_active_rooms_survive_eviction(self):
        room = _make_room()
        self.store.save_room(room)
        await self.store._evict_expired()
        assert self.store.get_room(room.id) is not None

    def test_all_rooms(self):
        r1, r2 = _make_room(), _make_room()
        self.store.save_room(r1)
        self.store.save_room(r2)
        assert len(self.store.all_rooms()) == 2
