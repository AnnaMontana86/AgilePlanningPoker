from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

from app.models.card_set import CardSet, PREDEFINED_CARD_SETS
from app.models.participant import Participant
from app.models.room import Room, Topic
from app.models.round import Round
from app.store.memory import store
from app.events.broadcaster import broadcaster

router = APIRouter()


# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------

class CreateRoomRequest(BaseModel):
    name: str
    card_set_name: str | None = None
    custom_card_set: CardSet | None = None
    owner_nickname: str


class JoinRoomRequest(BaseModel):
    nickname: str


class VoteRequest(BaseModel):
    participant_id: str
    token: str
    card: str | None  # None = retract vote


class OwnerActionRequest(BaseModel):
    token: str


class KickRequest(BaseModel):
    token: str


class LeaveRequest(BaseModel):
    participant_id: str
    token: str


class AddTopicRequest(BaseModel):
    token: str
    short_name: str
    link: str = ""


class ReorderTopicsRequest(BaseModel):
    token: str
    topic_ids: list[str]


class EditTopicRequest(BaseModel):
    token: str
    short_name: str
    link: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_room_or_404(room_id: str) -> Room:
    room = store.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


def _resolve_card_set(req: CreateRoomRequest) -> CardSet:
    if req.custom_card_set:
        return req.custom_card_set
    if req.card_set_name:
        cards = PREDEFINED_CARD_SETS.get(req.card_set_name)
        if not cards:
            raise HTTPException(status_code=400, detail=f"Unknown card set '{req.card_set_name}'")
        return CardSet(name=req.card_set_name, cards=cards)
    raise HTTPException(status_code=400, detail="Provide either card_set_name or custom_card_set")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/card-sets")
async def list_card_sets():
    return {name: cards for name, cards in PREDEFINED_CARD_SETS.items()}


@router.post("/rooms", status_code=201)
async def create_room(req: CreateRoomRequest):
    card_set = _resolve_card_set(req)
    owner = Participant(nickname=req.owner_nickname, is_owner=True)
    room = Room(name=req.name, card_set=card_set)
    room.participants[owner.id] = owner
    store.save_room(room)
    return {"room_id": room.id, "participant_id": owner.id, "token": owner.id}


@router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    room = _get_room_or_404(room_id)
    return room


@router.post("/rooms/{room_id}/join", status_code=201)
async def join_room(room_id: str, req: JoinRoomRequest):
    room = _get_room_or_404(room_id)
    existing_nicknames = {p.nickname for p in room.participants.values()}
    nickname = req.nickname
    while nickname in existing_nicknames:
        nickname = f"Super {nickname}"
    participant = Participant(nickname=nickname)
    room.participants[participant.id] = participant
    store.save_room(room)
    await broadcaster.broadcast(room_id, "participant_joined", {"participant": participant.model_dump()})
    return {"participant_id": participant.id, "token": participant.id}


@router.post("/rooms/{room_id}/vote")
async def vote(room_id: str, req: VoteRequest):
    room = _get_room_or_404(room_id)
    if room.current_round.revealed:
        raise HTTPException(status_code=409, detail="Round already revealed")
    participant = room.participants.get(req.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if req.token != participant.id:
        raise HTTPException(status_code=403, detail="Invalid token")
    if req.card is not None and req.card not in room.card_set.cards:
        raise HTTPException(status_code=400, detail="Card not in card set")
    participant.vote = req.card
    store.save_room(room)
    event = "vote_cast" if req.card else "vote_retracted"
    await broadcaster.broadcast(room_id, event, {"participant_id": participant.id})
    return {"ok": True}


@router.post("/rooms/{room_id}/reveal")
async def reveal(room_id: str, req: OwnerActionRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can reveal cards")
    if room.current_round.revealed:
        raise HTTPException(status_code=409, detail="Round already revealed")
    room.current_round.revealed = True
    votes = {pid: p.vote for pid, p in room.participants.items()}
    store.save_room(room)
    await broadcaster.broadcast(room_id, "cards_revealed", {"votes": votes})
    return {"ok": True, "votes": votes}


@router.post("/rooms/{room_id}/new-round")
async def new_round(room_id: str, req: OwnerActionRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can start a new round")
    for p in room.participants.values():
        p.vote = None
    room.current_round = Round(number=room.current_round.number + 1)
    if room.topics and room.current_topic_index < len(room.topics) - 1:
        room.current_topic_index += 1
    store.save_room(room)
    await broadcaster.broadcast(room_id, "new_round", {
        "round_number": room.current_round.number,
        "current_topic_index": room.current_topic_index,
    })
    return {"ok": True, "round_number": room.current_round.number}


@router.post("/rooms/{room_id}/retry")
async def retry_round(room_id: str, req: OwnerActionRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can retry a round")
    if not room.current_round.revealed:
        raise HTTPException(status_code=409, detail="Round not yet revealed")
    for p in room.participants.values():
        p.vote = None
    room.current_round = Round(number=room.current_round.number + 1)
    store.save_room(room)
    await broadcaster.broadcast(room_id, "new_round", {
        "round_number": room.current_round.number,
        "current_topic_index": room.current_topic_index,
    })
    return {"ok": True, "round_number": room.current_round.number}


@router.post("/rooms/{room_id}/topics", status_code=201)
async def add_topic(room_id: str, req: AddTopicRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can add topics")
    topic = Topic(short_name=req.short_name, link=req.link)
    room.topics.append(topic)
    store.save_room(room)
    await broadcaster.broadcast(room_id, "topic_added", {"topic": topic.model_dump()})
    return {"topic": topic.model_dump()}


@router.put("/rooms/{room_id}/topics")
async def reorder_topics(room_id: str, req: ReorderTopicsRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can reorder topics")
    topic_map = {t.id: t for t in room.topics}
    if set(req.topic_ids) != set(topic_map.keys()):
        raise HTTPException(status_code=400, detail="Invalid topic IDs")
    room.topics = [topic_map[tid] for tid in req.topic_ids]
    store.save_room(room)
    await broadcaster.broadcast(room_id, "topics_reordered", {"topics": [t.model_dump() for t in room.topics]})
    return {"ok": True}


@router.patch("/rooms/{room_id}/topics/{topic_id}")
async def edit_topic(room_id: str, topic_id: str, req: EditTopicRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can edit topics")
    topic = next((t for t in room.topics if t.id == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic.short_name = req.short_name
    topic.link = req.link
    store.save_room(room)
    await broadcaster.broadcast(room_id, "topic_updated", {"topic": topic.model_dump()})
    return {"topic": topic.model_dump()}


@router.delete("/rooms/{room_id}/topics/{topic_id}")
async def delete_topic(room_id: str, topic_id: str, req: KickRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can remove topics")
    idx = next((i for i, t in enumerate(room.topics) if t.id == topic_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    room.topics.pop(idx)
    if idx < room.current_topic_index:
        room.current_topic_index -= 1
    room.current_topic_index = max(0, min(room.current_topic_index, len(room.topics) - 1)) if room.topics else 0
    store.save_room(room)
    await broadcaster.broadcast(room_id, "topic_removed", {
        "topic_id": topic_id,
        "current_topic_index": room.current_topic_index,
    })
    return {"ok": True}


@router.delete("/rooms/{room_id}/participants/{participant_id}")
async def kick_participant(room_id: str, participant_id: str, req: KickRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can kick participants")
    if participant_id not in room.participants:
        raise HTTPException(status_code=404, detail="Participant not found")
    if room.participants[participant_id].is_owner:
        raise HTTPException(status_code=400, detail="Cannot kick the room owner")
    del room.participants[participant_id]
    store.save_room(room)
    await broadcaster.broadcast(room_id, "participant_kicked", {"participant_id": participant_id})
    return {"ok": True}


@router.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, req: LeaveRequest):
    room = _get_room_or_404(room_id)
    participant = room.participants.get(req.participant_id)
    if not participant or req.token != participant.id:
        raise HTTPException(status_code=403, detail="Invalid token")

    # Last participant — delete room silently
    if len(room.participants) == 1:
        store.delete_room(room_id)
        return {"ok": True}

    new_owner_id = None
    if participant.is_owner:
        next_participant = next(p for p in room.participants.values() if p.id != req.participant_id)
        next_participant.is_owner = True
        new_owner_id = next_participant.id

    del room.participants[req.participant_id]
    store.save_room(room)
    await broadcaster.broadcast(room_id, "participant_left", {
        "participant_id": req.participant_id,
        "new_owner_id": new_owner_id,
    })
    return {"ok": True}


@router.get("/rooms/{room_id}/events")
async def room_events(room_id: str, request: Request):
    _get_room_or_404(room_id)

    async def event_stream():
        q = broadcaster.subscribe(room_id)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            broadcaster.unsubscribe(room_id, q)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
