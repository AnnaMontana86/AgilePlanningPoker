from pydantic import BaseModel, Field
import uuid


# A person who has joined a planning poker room.
# Responsible for holding a participant's display name, current vote,
# owner flag, active emoji reaction, and suspended status.
class Participant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nickname: str = Field(..., min_length=1, max_length=32)
    is_owner: bool = False
    vote: str | None = None
    emoji: str | None = None
    suspended: bool = False
