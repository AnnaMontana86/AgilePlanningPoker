import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.store.memory import store


@pytest.fixture(autouse=True)
def clear_store():
    """Reset in-memory store between tests."""
    store._rooms.clear()
    yield
    store._rooms.clear()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def room_with_owner(client):
    """Creates a room and returns (room_id, owner_token, owner_participant_id)."""
    resp = await client.post("/api/rooms", json={
        "name": "Test Room",
        "card_set_name": "Fibonacci",
        "owner_nickname": "Alice",
    })
    assert resp.status_code == 201
    data = resp.json()
    return data["room_id"], data["token"], data["participant_id"]
