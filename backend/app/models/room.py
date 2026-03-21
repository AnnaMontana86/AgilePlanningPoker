from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from app.models.card_set import CardSet
from app.models.participant import Participant
from app.models.round import Round


# A single agenda item to be estimated in a planning poker room.
# Responsible for storing the topic's short name, optional link,
# and the final estimates and per-participant vote history recorded after
# the round is closed.
class Topic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    short_name: str = Field(..., min_length=1, max_length=100)
    link: str = ""
    estimates: list[str] | None = None  # None = not estimated yet
    participant_votes: dict[str, str] | None = None  # nickname → card


# The central aggregate for a planning poker session.
# Responsible for holding all session state: participants, the active
# card set, the ordered topic list, the current round, timer, music
# preferences, shared note, and the timestamps used for TTL expiry.
class Room(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=80)
    card_set: CardSet
    participants: dict[str, Participant] = {}
    current_round: Round = Field(default_factory=Round)
    topics: list[Topic] = Field(default_factory=list)
    current_topic_index: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)

    timer_ends_at: datetime | None = None

    music_playing: bool = False
    music_volume: float = 0.05

    note: str | None = None

    def touch(self) -> None:
        self.last_activity_at = datetime.utcnow()
