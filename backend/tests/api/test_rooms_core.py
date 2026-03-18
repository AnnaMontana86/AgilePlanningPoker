import pytest


class TestCreateRoom:
    async def test_create_room_with_predefined_card_set(self, client):
        resp = await client.post("/api/rooms", json={
            "name": "Sprint 42",
            "card_set_name": "Fibonacci",
            "owner_nickname": "Alice",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "room_id" in data
        assert "token" in data

    async def test_create_room_with_custom_card_set(self, client):
        resp = await client.post("/api/rooms", json={
            "name": "Custom Room",
            "custom_card_set": {"name": "my-set", "cards": ["S", "M", "L"]},
            "owner_nickname": "Bob",
        })
        assert resp.status_code == 201

    async def test_create_room_unknown_card_set_returns_400(self, client):
        resp = await client.post("/api/rooms", json={
            "name": "Bad Room",
            "card_set_name": "nonexistent",
            "owner_nickname": "Carol",
        })
        assert resp.status_code == 400

    async def test_create_room_no_card_set_returns_400(self, client):
        resp = await client.post("/api/rooms", json={
            "name": "No Cards",
            "owner_nickname": "Dave",
        })
        assert resp.status_code == 400


class TestGetRoom:
    async def test_get_existing_room(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        resp = await client.get(f"/api/rooms/{room_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == room_id

    async def test_get_nonexistent_room_returns_404(self, client):
        resp = await client.get("/api/rooms/does-not-exist")
        assert resp.status_code == 404


class TestJoinRoom:
    async def test_join_room(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        assert resp.status_code == 201
        assert "participant_id" in resp.json()

    async def test_join_nonexistent_room_returns_404(self, client):
        resp = await client.post("/api/rooms/bad-id/join", json={"nickname": "Bob"})
        assert resp.status_code == 404


class TestDuplicateNickname:
    async def test_duplicate_nickname_gets_super_prefix(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        assert join.status_code == 201
        join2 = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        assert join2.status_code == 201
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        nicknames = [p["nickname"] for p in room["participants"].values()]
        assert "Bob" in nicknames
        assert "Super Bob" in nicknames

    async def test_chained_super_prefix(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        join3 = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        assert join3.status_code == 201
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        nicknames = [p["nickname"] for p in room["participants"].values()]
        assert "Super Super Bob" in nicknames
