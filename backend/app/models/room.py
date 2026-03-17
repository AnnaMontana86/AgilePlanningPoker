from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from app.models.card_set import CardSet
from app.models.participant import Participant
from app.models.round import Round


class Topic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    short_name: str = Field(..., min_length=1, max_length=100)
    link: str = ""
    estimates: list[str] | None = None  # None = not estimated yet


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

    def touch(self) -> None:
        self.last_activity_at = datetime.utcnow()
