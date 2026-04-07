import pytest


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

    async def test_co_owner_can_reveal(self, client, room_with_owner):
        room_id, token, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        bob_token = join.json()["token"]
        await client.post(
            f"/api/rooms/{room_id}/participants/{bob_id}/promote",
            json={"token": token},
        )
        resp = await client.post(f"/api/rooms/{room_id}/reveal", json={"token": bob_token})
        assert resp.status_code == 200

    async def test_participant_id_is_not_accepted_as_token(self, client, room_with_owner):
        room_id, _, owner_id = room_with_owner
        # owner_id is the public participant UUID — must not work as auth token
        resp = await client.post(f"/api/rooms/{room_id}/reveal", json={"token": owner_id})
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



class TestLeaveRoom:
    async def test_non_owner_can_leave(self, client, room_with_owner):
        room_id, _, _ = room_with_owner
        join = await client.post(f"/api/rooms/{room_id}/join", json={"nickname": "Bob"})
        bob_id = join.json()["participant_id"]
        bob_token = join.json()["token"]
        resp = await client.post(f"/api/rooms/{room_id}/leave", json={
            "participant_id": bob_id,
            "token": bob_token,
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
