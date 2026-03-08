from pydantic import BaseModel, Field
import uuid


class Participant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nickname: str = Field(..., min_length=1, max_length=32)
    is_owner: bool = False
    vote: str | None = None

    # Future: emoji status for presence/mood sharing
    # emoji_status: str | None = None
