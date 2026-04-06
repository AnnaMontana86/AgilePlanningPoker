from pydantic import BaseModel, Field
import uuid


# A person who has joined a planning poker room.
# Responsible for holding a participant's display name, current vote,
# owner flag, active emoji reaction, and suspended status.
class Participant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Secret auth token — separate from the public participant ID.
    # exclude=True keeps it out of all API responses (GET /rooms/{id}, etc.)
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), exclude=True)
    nickname: str = Field(..., min_length=1, max_length=32)
    is_owner: bool = False
    vote: str | None = None
    emoji: str | None = None
    suspended: bool = False
