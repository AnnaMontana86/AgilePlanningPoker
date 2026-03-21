from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from datetime import timedelta

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

# Request body for creating a new planning poker room.
# Responsible for carrying the room name, the owner's nickname, and
# the chosen card set (either a predefined name or a custom definition).
class CreateRoomRequest(BaseModel):
    name: str
    card_set_name: str | None = None
    custom_card_set: CardSet | None = None
    owner_nickname: str


# Request body for joining an existing room.
# Responsible for carrying the nickname the participant wants to use.
class JoinRoomRequest(BaseModel):
    nickname: str


# Request body for casting or retracting a vote.
# Responsible for carrying the participant's identity token and the
# selected card value (None to retract an existing vote).
class VoteRequest(BaseModel):
    participant_id: str
    token: str
    card: str | None  # None = retract vote


# Request body for owner-only actions that require no extra data.
# Responsible for carrying the owner's identity token to authorise the
# action (used for reveal, new-round, retry, and stop-timer).
class OwnerActionRequest(BaseModel):
    token: str


# Request body for kicking a participant or deleting a topic.
# Responsible for carrying the owner's identity token to authorise
# the destructive action.
class KickRequest(BaseModel):
    token: str


# Request body for voluntarily leaving a room.
# Responsible for carrying the leaving participant's ID and token so
# the server can verify identity and transfer ownership if needed.
class LeaveRequest(BaseModel):
    participant_id: str
    token: str


# Request body for setting or clearing a participant's emoji reaction.
# Responsible for carrying the participant's identity token and the
# chosen emoji (None to clear the current reaction).
class EmojiRequest(BaseModel):
    participant_id: str
    token: str
    emoji: str | None  # None = clear emoji


# Request body for adding a new topic to the room's backlog.
# Responsible for carrying the owner token, the topic's short name,
# and an optional reference link.
class AddTopicRequest(BaseModel):
    token: str
    short_name: str
    link: str = ""


# Request body for reordering the room's topic list.
# Responsible for carrying the owner token and the complete ordered
# list of topic IDs that defines the new sequence.
class ReorderTopicsRequest(BaseModel):
    token: str
    topic_ids: list[str]


# Request body for editing an existing topic's metadata.
# Responsible for carrying the owner token, the updated short name,
# and the updated reference link.
class EditTopicRequest(BaseModel):
    token: str
    short_name: str
    link: str = ""


# Request body for switching the room's active topic.
# Responsible for carrying the owner token that authorises the
# topic selection.
class SelectTopicRequest(BaseModel):
    token: str


# Request body for updating the room's shared note.
# Responsible for carrying the owner token and the new note content
# (None to clear the note).
class NoteRequest(BaseModel):
    token: str
    note: str | None = None  # None = clear note


ALLOWED_EMOJIS = {"🤔", "😄", "😢", "❤️", "☕", "🍺"}


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
    was_suspended = participant.suspended
    if req.card is not None and was_suspended:
        participant.suspended = False
    participant.vote = req.card
    store.save_room(room)
    if was_suspended and req.card is not None:
        await broadcaster.broadcast(room_id, "participant_unsuspended", {"participant_id": participant.id})
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
    # Save estimates to current topic before advancing
    estimated_topic = None
    if room.topics and room.current_topic_index < len(room.topics):
        topic = room.topics[room.current_topic_index]
        card_order = {card: i for i, card in enumerate(room.card_set.cards)}
        voted = [(p.nickname, p.vote) for p in room.participants.values() if p.vote is not None]
        topic.estimates = sorted([v for _, v in voted], key=lambda v: card_order.get(v, len(room.card_set.cards)))
        topic.participant_votes = {nickname: vote for nickname, vote in voted}
        estimated_topic = topic.model_dump()
    for p in room.participants.values():
        p.vote = None
    room.current_round = Round(number=room.current_round.number + 1)
    if room.topics and room.current_topic_index < len(room.topics) - 1:
        room.current_topic_index += 1
    music_was_playing = room.music_playing
    room.music_playing = False
    store.save_room(room)
    await broadcaster.broadcast(room_id, "new_round", {
        "round_number": room.current_round.number,
        "current_topic_index": room.current_topic_index,
        "estimated_topic": estimated_topic,
    })
    if music_was_playing:
        await broadcaster.broadcast(room_id, "music_updated", {"playing": False})
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
    music_was_playing = room.music_playing
    room.music_playing = False
    store.save_room(room)
    await broadcaster.broadcast(room_id, "new_round", {
        "round_number": room.current_round.number,
        "current_topic_index": room.current_topic_index,
    })
    if music_was_playing:
        await broadcaster.broadcast(room_id, "music_updated", {"playing": False})
    return {"ok": True, "round_number": room.current_round.number}


@router.post("/rooms/{room_id}/topics", status_code=201)
async def add_topic(room_id: str, req: AddTopicRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can add topics")
    if any(t.short_name == req.short_name for t in room.topics):
        raise HTTPException(status_code=409, detail="A topic with this short name already exists in the room")
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
    if req.short_name != topic.short_name and any(t.short_name == req.short_name for t in room.topics):
        raise HTTPException(status_code=409, detail="A topic with this short name already exists in the room")
    topic.short_name = req.short_name
    topic.link = req.link
    topic.estimates = None
    topic.participant_votes = None
    votes_reset = not room.current_round.revealed
    if votes_reset:
        for p in room.participants.values():
            p.vote = None
    store.save_room(room)
    await broadcaster.broadcast(room_id, "topic_updated", {"topic": topic.model_dump()})
    if votes_reset:
        await broadcaster.broadcast(room_id, "votes_reset", {})
    return {"topic": topic.model_dump()}


@router.post("/rooms/{room_id}/topics/{topic_id}/select")
async def select_topic(room_id: str, topic_id: str, req: SelectTopicRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can select topics")
    idx = next((i for i, t in enumerate(room.topics) if t.id == topic_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    room.current_topic_index = idx
    votes_reset = not room.current_round.revealed
    if votes_reset:
        for p in room.participants.values():
            p.vote = None
    store.save_room(room)
    await broadcaster.broadcast(room_id, "topic_selected", {"current_topic_index": idx})
    if votes_reset:
        await broadcaster.broadcast(room_id, "votes_reset", {})
    return {"ok": True, "current_topic_index": idx}


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


@router.post("/rooms/{room_id}/participants/{participant_id}/suspend")
async def suspend_participant(room_id: str, participant_id: str, req: OwnerActionRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can suspend participants")
    if participant_id not in room.participants:
        raise HTTPException(status_code=404, detail="Participant not found")
    if room.participants[participant_id].is_owner:
        raise HTTPException(status_code=400, detail="Cannot suspend the room owner")
    participant = room.participants[participant_id]
    participant.suspended = True
    participant.vote = None
    store.save_room(room)
    await broadcaster.broadcast(room_id, "participant_suspended", {"participant_id": participant_id})
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


@router.post("/rooms/{room_id}/emoji")
async def set_emoji(room_id: str, req: EmojiRequest):
    room = _get_room_or_404(room_id)
    participant = room.participants.get(req.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if req.token != participant.id:
        raise HTTPException(status_code=403, detail="Invalid token")
    if req.emoji is not None and req.emoji not in ALLOWED_EMOJIS:
        raise HTTPException(status_code=400, detail="Emoji not allowed")
    participant.emoji = req.emoji
    store.save_room(room)
    await broadcaster.broadcast(room_id, "emoji_updated", {
        "participant_id": participant.id,
        "emoji": participant.emoji,
    })
    return {"ok": True}


# Request body for starting the room countdown timer.
# Responsible for carrying the owner token and the requested timer
# duration in seconds.
class TimerRequest(BaseModel):
    token: str
    duration_seconds: int


# Request body for controlling the room's ambient music.
# Responsible for carrying the owner token, the desired play/pause
# state, and an optional volume level.
class MusicRequest(BaseModel):
    token: str
    playing: bool
    volume: float | None = None


@router.post("/rooms/{room_id}/music")
async def set_music(room_id: str, req: MusicRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the owner can control music")
    room.music_playing = req.playing
    if req.volume is not None:
        room.music_volume = max(0.0, min(1.0, req.volume))
    store.save_room(room)
    await broadcaster.broadcast(room_id, "music_updated", {"playing": req.playing, "volume": room.music_volume})
    return {"ok": True}


@router.post("/rooms/{room_id}/timer")
async def start_timer(room_id: str, req: TimerRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can set the timer")
    if req.duration_seconds < 1:
        raise HTTPException(status_code=400, detail="Duration must be at least 1 second")
    from datetime import datetime
    room.timer_ends_at = datetime.utcnow() + timedelta(seconds=req.duration_seconds)
    store.save_room(room)
    ends_at = room.timer_ends_at.isoformat()
    await broadcaster.broadcast(room_id, "timer_started", {"ends_at": ends_at})
    return {"ok": True, "ends_at": ends_at}


@router.delete("/rooms/{room_id}/timer")
async def stop_timer(room_id: str, req: OwnerActionRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can stop the timer")
    room.timer_ends_at = None
    store.save_room(room)
    await broadcaster.broadcast(room_id, "timer_stopped", {})
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


@router.patch("/rooms/{room_id}/note")
async def update_note(room_id: str, req: NoteRequest):
    room = _get_room_or_404(room_id)
    owner = next((p for p in room.participants.values() if p.is_owner), None)
    if not owner or req.token != owner.id:
        raise HTTPException(status_code=403, detail="Only the room owner can update the note")
    note = req.note.strip() if req.note else None
    room.note = note or None
    store.save_room(room)
    await broadcaster.broadcast(room_id, "note_updated", {"note": room.note})
    return {"ok": True, "note": room.note}


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
