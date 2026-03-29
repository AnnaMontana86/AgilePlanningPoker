import pytest


class TestNote:
    async def test_note_within_limit_is_accepted(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.patch(f"/api/rooms/{room_id}/note", json={"token": token, "note": "hello"})
        assert resp.status_code == 200

    async def test_note_at_max_length_is_accepted(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.patch(f"/api/rooms/{room_id}/note", json={"token": token, "note": "x" * 3000})
        assert resp.status_code == 200

    async def test_note_exceeding_max_length_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.patch(f"/api/rooms/{room_id}/note", json={"token": token, "note": "x" * 3001})
        assert resp.status_code == 422

    async def test_note_with_script_tag_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.patch(f"/api/rooms/{room_id}/note", json={"token": token, "note": "<script>alert(1)</script>"})
        assert resp.status_code == 422

    async def test_note_with_uppercase_script_tag_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.patch(f"/api/rooms/{room_id}/note", json={"token": token, "note": "<SCRIPT>evil()</SCRIPT>"})
        assert resp.status_code == 422

    async def test_note_can_be_cleared(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.patch(f"/api/rooms/{room_id}/note", json={"token": token, "note": None})
        assert resp.status_code == 200


class TestTimer:
    async def test_valid_duration_is_accepted(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/timer", json={"token": token, "duration_seconds": 300})
        assert resp.status_code == 200

    async def test_max_duration_is_accepted(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/timer", json={"token": token, "duration_seconds": 10_800})
        assert resp.status_code == 200

    async def test_duration_exceeding_max_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/timer", json={"token": token, "duration_seconds": 10_801})
        assert resp.status_code == 422

    async def test_zero_duration_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/timer", json={"token": token, "duration_seconds": 0})
        assert resp.status_code == 422

    async def test_negative_duration_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/timer", json={"token": token, "duration_seconds": -1})
        assert resp.status_code == 422
