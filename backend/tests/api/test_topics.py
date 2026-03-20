import pytest


class TestAddTopic:
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

    async def test_duplicate_short_name_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        resp = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        assert resp.status_code == 409


class TestReorderTopics:
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


class TestDeleteTopic:
    async def test_owner_can_delete_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        resp = await client.request("DELETE", f"/api/rooms/{room_id}/topics/{topic_id}", json={"token": token})
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert len(room["topics"]) == 0


class TestEditTopic:
    async def test_owner_can_edit_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "Old Name"})
        topic_id = r.json()["topic"]["id"]
        resp = await client.patch(f"/api/rooms/{room_id}/topics/{topic_id}", json={
            "token": token, "short_name": "New Name", "link": "https://example.com",
        })
        assert resp.status_code == 200
        assert resp.json()["topic"]["short_name"] == "New Name"
        assert resp.json()["topic"]["link"] == "https://example.com"

    async def test_non_owner_cannot_edit_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_token = join.json()["token"]
        resp = await client.patch(f"/api/rooms/{room_id}/topics/{topic_id}", json={
            "token": bob_token, "short_name": "Hacked",
        })
        assert resp.status_code == 403

    async def test_duplicate_short_name_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        r2 = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        topic2_id = r2.json()["topic"]["id"]
        resp = await client.patch(f"/api/rooms/{room_id}/topics/{topic2_id}", json={"token": token, "short_name": "T1"})
        assert resp.status_code == 409

    async def test_same_name_is_allowed(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        resp = await client.patch(f"/api/rooms/{room_id}/topics/{topic_id}", json={"token": token, "short_name": "T1"})
        assert resp.status_code == 200

    async def test_before_reveal_resets_votes(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.patch(f"/api/rooms/{room_id}/topics/{topic_id}", json={"token": token, "short_name": "T1 edited"})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][pid]["vote"] is None

    async def test_after_reveal_preserves_votes(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.patch(f"/api/rooms/{room_id}/topics/{topic_id}", json={"token": token, "short_name": "T1 edited"})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][pid]["vote"] == "5"

    async def test_clears_saved_estimates(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/new-round", json={"token": token})
        await client.patch(f"/api/rooms/{room_id}/topics/{topic_id}", json={"token": token, "short_name": "T1 edited"})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["topics"][0]["estimates"] is None


class TestSelectTopic:
    async def test_owner_can_select_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        r2 = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        topic2_id = r2.json()["topic"]["id"]
        resp = await client.post(f"/api/rooms/{room_id}/topics/{topic2_id}/select", json={"token": token})
        assert resp.status_code == 200
        assert resp.json()["current_topic_index"] == 1
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["current_topic_index"] == 1

    async def test_non_owner_cannot_select_topic(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_token = join.json()["token"]
        resp = await client.post(f"/api/rooms/{room_id}/topics/{topic_id}/select", json={"token": bob_token})
        assert resp.status_code == 403

    async def test_nonexistent_topic_returns_404(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/topics/nonexistent/select", json={"token": token})
        assert resp.status_code == 404

    async def test_before_reveal_resets_votes(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        r2 = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        topic2_id = r2.json()["topic"]["id"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/topics/{topic2_id}/select", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][pid]["vote"] is None

    async def test_after_reveal_preserves_votes(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        r2 = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        topic2_id = r2.json()["topic"]["id"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/topics/{topic2_id}/select", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][pid]["vote"] == "5"


class TestTopicEstimates:
    async def test_new_round_saves_estimates_to_topic(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        bob_token = join.json()["token"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": bob_id, "token": bob_token, "card": "3"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/new-round", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        t1 = room["topics"][0]
        assert t1["estimates"] is not None
        assert set(t1["estimates"]) == {"5", "3"}

    async def test_new_round_saves_participant_votes(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        owner_nickname = (await client.get(f"/api/rooms/{room_id}")).json()["participants"][pid]["nickname"]
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        bob_token = join.json()["token"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": bob_id, "token": bob_token, "card": "3"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/new-round", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        pv = room["topics"][0]["participant_votes"]
        assert pv is not None
        assert pv[owner_nickname] == "5"
        assert pv["Bob"] == "3"

    async def test_edit_topic_clears_participant_votes(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        r = await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        topic_id = r.json()["topic"]["id"]
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T2"})
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        bob_token = join.json()["token"]
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": bob_id, "token": bob_token, "card": "3"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/new-round", json={"token": token})
        await client.patch(f"/api/rooms/{room_id}/topics/{topic_id}", json={"token": token, "short_name": "T1 edited"})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["topics"][0]["participant_votes"] is None

    async def test_retry_does_not_save_participant_votes(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/retry", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["topics"][0]["participant_votes"] is None

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

    async def test_retry_does_not_save_estimates(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/topics", json={"token": token, "short_name": "T1"})
        await client.post(f"/api/rooms/{room_id}/vote", json={"participant_id": pid, "token": token, "card": "5"})
        await client.post(f"/api/rooms/{room_id}/reveal", json={"token": token})
        await client.post(f"/api/rooms/{room_id}/retry", json={"token": token})
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["topics"][0]["estimates"] is None

    async def test_retry_requires_revealed_round(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/retry", json={"token": token})
        assert resp.status_code == 409
