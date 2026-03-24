from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Notification(BaseModel):
    payload: dict


class CreateNotification(Notification):
    event_type: str
    status: str


class UpdateNotification(CreateNotification):
    id: UUID
    retry_count: int
    next_retry_at: datetime | None
