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


class TestVoting:
    async def test_cast_vote(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/vote", json={
            "participant_id": pid,
            "token": token,
            "card": "5",
        })
        assert resp.status_code == 200

    async def test_retract_vote(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        resp = await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": None})
        assert resp.status_code == 200

    async def test_vote_invalid_card_returns_400(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/vote", json={
            "participant_id": pid,
            "token": token,
            "card": "999",
        })
        assert resp.status_code == 400

    async def test_vote_wrong_token_returns_403(self, client, room_with_owner):
        room_id, _, pid = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/vote", json={
            "participant_id": pid,
            "token": "wrong-token",
            "card": "5",
        })
        assert resp.status_code == 403


class TestReveal:
    async def test_owner_can_reveal(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        assert resp.status_code == 200

    async def test_non_owner_cannot_reveal(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Eve"})
        non_owner_token = join.json()["token"]
        resp = await client.post(f"/api/rooms/{room_id}/reveal", json={"token": non_owner_token})
        assert resp.status_code == 403

    async def test_cannot_reveal_twice(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        resp = await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        assert resp.status_code == 409


class TestNewRound:
    async def test_owner_can_start_new_round(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        resp = await client.post(f"/api/rooms/{room_id}/new-round", json={"token": token})
        assert resp.status_code == 200
        assert resp.json()["round_number"] == 2

    async def test_votes_reset_on_new_round(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/new-round", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][pid]["vote"] is None


class TestKick:
    async def test_owner_can_kick_participant(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Mallory"})
        victim_id = join.json()["participant_id"]
        resp = await client.request("DELETE", f"/api/rooms/{room_id}/participants/{victim_id}",
                                    json={"token": token})
        assert resp.status_code == 200

    async def test_owner_cannot_kick_themselves(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        resp = await client.request("DELETE", f"/api/rooms/{room_id}/participants/{pid}",
                                    json={"token": token})
        assert resp.status_code == 400


class TestLeaveRoom:
    async def test_non_owner_can_leave(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        resp = await client.post(f"/api/rooms/{room_id}/leave", json={
            "participant_id": bob_id,
            "token": bob_id,
        })
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert bob_id not in room["participants"]

    async def test_owner_leaving_transfers_ownership(self, client, room_with_owner):
        room_id, token, owner_id = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        resp = await client.post(f"/api/rooms/{room_id}/leave", json={
            "participant_id": owner_id,
            "token": token,
        })
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert owner_id not in room["participants"]
        assert room["participants"][bob_id]["is_owner"] is True

    async def test_last_participant_leaving_deletes_room(self, client, room_with_owner):
        room_id, token, owner_id = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/leave", json={
            "participant_id": owner_id,
            "token": token,
        })
        assert resp.status_code == 200
        assert (await client.get(f"/api/rooms/{room_id}")).status_code == 404

    async def test_leave_with_wrong_token_returns_403(self, client, room_with_owner):
        room_id, _, owner_id = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/leave", json={
            "participant_id": owner_id,
            "token": "wrong-token",
        })
        assert resp.status_code == 403


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


class TestTopics:
    async def test_owner_can_add_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/topics", json={
            "token": token, "short_name": "Sprint 1", "link": "https://example.com",
        })
        assert resp.status_code == 201
        assert resp.json()["topic"]["short_name"] == "Sprint 1"

    async def test_non_owner_cannot_add_topic(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_token = join.json()["token"]
        resp = await client.post(f"/api/rooms/{room_id}/topics", json={
            "token": bob_token, "short_name": "Bad topic",
        })
        assert resp.status_code == 403

    async def test_topic_appears_in_room(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert len(room["topics"]) == 2
        assert room["topics"][0]["short_name"] == "T1"

    async def test_owner_can_reorder_topics(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        r1 = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        r2 = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        id1 = r1.json()["topic"]["id"]
        id2 = r2.json()["topic"]["id"]
        resp = await client.put(f"/api/rooms/{room_id}/topics", json={"token": token, "topic_ids": [id2, id1]})
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["topics"][0]["short_name"] == "T2"

    async def test_owner_can_delete_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        resp = await client.request("DELETE", f"/api/rooms/{room_id}/topics/{topic_id}", json={"token": token})
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert len(room["topics"]) == 0

    async def test_new_round_advances_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/new-round", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["current_topic_index"] == 1

    async def test_retry_keeps_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        resp = await client.post(f"/api/rooms/{room_id}/retry", json={"token": token})
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["current_topic_index"] == 0

    async def test_retry_requires_revealed_round(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/retry", json={"token": token})
        assert resp.status_code == 409
