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


class TestPromoteParticipant:
    async def test_owner_can_promote_participant_to_co_owner(self, client, room_with_owner):
        room_id, token, owner_id = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/promote",
            json={"token": token},
        )
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][bob_id]["is_co_owner"] is True
        assert room["participants"][bob_id]["is_owner"] is False
        assert room["participants"][owner_id]["is_owner"] is True

    async def test_cannot_promote_already_owner(self, client, room_with_owner):
        room_id, token, owner_id = room_with_owner
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{owner_id}/promote",
            json={"token": token},
        )
        assert resp.status_code == 400

    async def test_cannot_promote_already_co_owner(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        await client.post(f"/api/rooms/{room_id}/participants/{bob_id}/promote", json={"token": token})
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/promote",
            json={"token": token},
        )
        assert resp.status_code == 400

    async def test_cannot_promote_nonexistent_participant(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/fake-id/promote",
            json={"token": token},
        )
        assert resp.status_code == 404

    async def test_wrong_token_returns_403(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/promote",
            json={"token": "wrong-token"},
        )
        assert resp.status_code == 403

    async def test_co_owner_cannot_promote(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        join_bob = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join_bob.json()["participant_id"]
        bob_token = join_bob.json()["token"]
        join_carol = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Carol"})
        carol_id = join_carol.json()["participant_id"]
        # promote Bob to co-owner
        await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/promote",
            json={"token": token},
        )
        # Bob (co-owner) tries to promote Carol — must be denied
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{carol_id}/promote",
            json={"token": bob_token},
        )
        assert resp.status_code == 403

    async def test_owner_leaving_promotes_co_owner_to_full_owner(self, client, room_with_owner):
        room_id, token, owner_id = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        # promote Bob to co-owner
        await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/promote",
            json={"token": token},
        )
        # original owner leaves — Bob is the only remaining participant so he becomes full owner
        resp = await client.post(f"/api/rooms/{room_id}/leave", json={
            "participant_id": owner_id,
            "token": token,
        })
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert owner_id not in room["participants"]
        assert room["participants"][bob_id]["is_owner"] is True


class TestKickParticipant:
    async def test_owner_can_kick_regular_participant(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/kick",
            json={"token": token},
        )
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert bob_id not in room["participants"]

    async def test_owner_can_kick_co_owner(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        await client.post(f"/api/rooms/{room_id}/participants/{bob_id}/promote", json={"token": token})
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/kick",
            json={"token": token},
        )
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert bob_id not in room["participants"]

    async def test_cannot_kick_the_owner(self, client, room_with_owner):
        room_id, token, owner_id = room_with_owner
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{owner_id}/kick",
            json={"token": token},
        )
        assert resp.status_code == 400

    async def test_kick_nonexistent_participant_returns_404(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/fake-id/kick",
            json={"token": token},
        )
        assert resp.status_code == 404

    async def test_wrong_token_returns_403(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/kick",
            json={"token": "wrong-token"},
        )
        assert resp.status_code == 403

    async def test_co_owner_cannot_kick(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        join_bob = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join_bob.json()["participant_id"]
        bob_token = join_bob.json()["token"]
        join_carol = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Carol"})
        carol_id = join_carol.json()["participant_id"]
        await client.post(f"/api/rooms/{room_id}/participants/{bob_id}/promote", json={"token": token})
        resp = await client.post(
            f"/api/rooms/{room_id}/participants/{carol_id}/kick",
            json={"token": bob_token},
        )
        assert resp.status_code == 403
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert carol_id in room["participants"]
