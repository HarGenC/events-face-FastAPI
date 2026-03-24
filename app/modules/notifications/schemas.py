from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateNotification(BaseModel):
    event_type: str
    payload: dict
    status: str


class UpdateNotification(CreateNotification):
    id: UUID
    retry_count: int
    next_retry_at: datetime | None
