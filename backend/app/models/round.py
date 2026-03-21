from datetime import datetime
from pydantic import BaseModel, Field
import uuid


# A single voting round within a planning poker room.
# Responsible for tracking whether cards have been revealed and
# recording when the round started and when it was revealed.
class Round(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    number: int = 1
    revealed: bool = False
    started_at: datetime = Field(default_factory=datetime.utcnow)
    revealed_at: datetime | None = None

    # Future: JIRA/Confluence ticket reference
    # ticket_url: str | None = None
    # ticket_title: str | None = None

    # Future: statistics computed on reveal
    # vote_distribution: dict[str, int] = {}
    # average: float | None = None
