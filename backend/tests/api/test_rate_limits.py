"""Rate limit boundary tests for groups A (30/min) and C (60/min).

Each test uses a distinct X-Real-IP header so counters don't bleed between
test cases even if the autouse clear_store fixture hasn't run yet.
"""
import pytest


ROOM_PAYLOAD = {"name": "RL Room", "card_set_name": "Fibonacci", "owner_nickname": "Alice"}


class TestCreateRoomRateLimit:
    """POST /rooms — Group A: 30/minute."""

    async def test_requests_within_limit_succeed(self, client):
        ip = "10.0.1.1"
        for _ in range(5):
            resp = await client.post(
                "/api/rooms", json=ROOM_PAYLOAD, headers={"X-Real-IP": ip}
            )
            assert resp.status_code == 201

    async def test_request_exceeding_limit_returns_429(self, client):
        ip = "10.0.1.2"
        for _ in range(30):
            await client.post("/api/rooms", json=ROOM_PAYLOAD, headers={"X-Real-IP": ip})
        resp = await client.post(
            "/api/rooms", json=ROOM_PAYLOAD, headers={"X-Real-IP": ip}
        )
        assert resp.status_code == 429


class TestJoinRoomRateLimit:
    """POST /rooms/{id}/join — Group A: 30/minute."""

    async def _make_room(self, client):
        resp = await client.post("/api/rooms", json=ROOM_PAYLOAD, headers={"X-Real-IP": "10.0.2.0"})
        assert resp.status_code == 201
        return resp.json()["room_id"]

    async def test_request_exceeding_limit_returns_429(self, client):
        room_id = await self._make_room(client)
        ip = "10.0.2.1"
        for i in range(30):
            await client.post(
                f"/api/rooms/{room_id}/join",
                json={"nickname": f"u{i}"},
                headers={"X-Real-IP": ip},
            )
        resp = await client.post(
            f"/api/rooms/{room_id}/join",
            json={"nickname": "overflow"},
            headers={"X-Real-IP": ip},
        )
        assert resp.status_code == 429


class TestVoteRateLimit:
    """POST /rooms/{id}/vote — Group C: 60/minute."""

    async def _setup(self, client):
        ip_owner = "10.0.3.0"
        resp = await client.post("/api/rooms", json=ROOM_PAYLOAD, headers={"X-Real-IP": ip_owner})
        assert resp.status_code == 201
        data = resp.json()
        return data["room_id"], data["token"], data["participant_id"]

    async def test_requests_within_limit_succeed(self, client):
        room_id, token, pid = await self._setup(client)
        ip = "10.0.3.1"
        for _ in range(5):
            resp = await client.post(
                f"/api/rooms/{room_id}/vote",
                json={"participant_id": pid, "token": token, "card": "3"},
                headers={"X-Real-IP": ip},
            )
            assert resp.status_code == 200

    async def test_request_exceeding_limit_returns_429(self, client):
        room_id, token, pid = await self._setup(client)
        ip = "10.0.3.2"
        for _ in range(60):
            await client.post(
                f"/api/rooms/{room_id}/vote",
                json={"participant_id": pid, "token": token, "card": "3"},
                headers={"X-Real-IP": ip},
            )
        resp = await client.post(
            f"/api/rooms/{room_id}/vote",
            json={"participant_id": pid, "token": token, "card": "5"},
            headers={"X-Real-IP": ip},
        )
        assert resp.status_code == 429
