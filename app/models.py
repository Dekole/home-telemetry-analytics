from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Event(BaseModel):
    event_id: UUID
    timestamp: datetime
    device_id: str
    event_type: str
    details: dict[str, Any] | None = None


class EventsResponse(BaseModel):
    events: list[Event]
    total: int
