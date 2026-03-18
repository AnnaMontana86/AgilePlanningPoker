import pytest


class TestEmoji:
    async def test_participant_can_set_emoji(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/emoji", json={
            "participant_id": pid, "token": token, "emoji": "🤔",
        })
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][pid]["emoji"] == "🤔"

    async def test_participant_can_clear_emoji(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        await client.post(f"/api/rooms/{room_id}/emoji", json={
            "participant_id": pid, "token": token, "emoji": "😄",
        })
        resp = await client.post(f"/api/rooms/{room_id}/emoji", json={
            "participant_id": pid, "token": token, "emoji": None,
        })
        assert resp.status_code == 200
        room = (await client.get(f"/api/rooms/{room_id}")).json()
        assert room["participants"][pid]["emoji"] is None

    async def test_disallowed_emoji_returns_400(self, client, room_with_owner):
        room_id, token, pid = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/emoji", json={
            "participant_id": pid, "token": token, "emoji": "🎉",
        })
        assert resp.status_code == 400

    async def test_wrong_token_returns_403(self, client, room_with_owner):
        room_id, _, pid = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/emoji", json={
            "participant_id": pid, "token": "bad-token", "emoji": "☕",
        })
        assert resp.status_code == 403
