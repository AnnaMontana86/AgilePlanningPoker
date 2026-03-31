import base64
import pytest

# Minimal valid 1×1 JPEG (332 bytes decoded)
_TINY_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U"
    "HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA"
    "/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9"
    "AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0"
    "NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWW"
    "l5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx"
    "8vP09fb3+Pn6/9oACAEBAAA/APvT/9k="
)
TINY_JPEG_DATA_URL = f"data:image/jpeg;base64,{_TINY_JPEG_B64}"


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


class TestImageUpload:
    async def test_owner_can_upload_image(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        resp = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": TINY_JPEG_DATA_URL})
        assert resp.status_code == 201
        assert "image_id" in resp.json()

    async def test_non_owner_cannot_upload(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_token = join.json()["participant_id"]
        resp = await client.post(f"/api/rooms/{room_id}/images", json={"token": bob_token, "data_url": TINY_JPEG_DATA_URL})
        assert resp.status_code == 403

    async def test_uploaded_image_is_gettable(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        upload = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": TINY_JPEG_DATA_URL})
        image_id = upload.json()["image_id"]
        resp = await client.get(f"/api/rooms/{room_id}/images/{image_id}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/jpeg"

    async def test_unauthenticated_get_is_allowed(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        upload = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": TINY_JPEG_DATA_URL})
        image_id = upload.json()["image_id"]
        resp = await client.get(f"/api/rooms/{room_id}/images/{image_id}")
        assert resp.status_code == 200

    async def test_image_limit_is_enforced(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        for _ in range(10):
            resp = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": TINY_JPEG_DATA_URL})
            assert resp.status_code == 201
        resp = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": TINY_JPEG_DATA_URL})
        assert resp.status_code == 409

    async def test_invalid_mime_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        bad = "data:application/pdf;base64," + base64.b64encode(b"fake pdf").decode()
        resp = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": bad})
        assert resp.status_code == 422

    async def test_oversized_image_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        big = "data:image/png;base64," + base64.b64encode(b"\x00" * (501 * 1024)).decode()
        resp = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": big})
        assert resp.status_code == 422

    async def test_invalid_base64_is_rejected(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        bad = "data:image/jpeg;base64,THIS IS NOT VALID BASE64!!!"
        resp = await client.post(f"/api/rooms/{room_id}/images", json={"token": token, "data_url": bad})
        assert resp.status_code == 422

    async def test_get_nonexistent_image_returns_404(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        resp = await client.get(f"/api/rooms/{room_id}/images/does-not-exist")
        assert resp.status_code == 404
