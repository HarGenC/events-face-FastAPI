from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BasePlace(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: str


class BaseEvent(BaseModel):
    id: UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class CreatePlace(BasePlace):
    changed_at: datetime
    created_at: datetime


class CreateEvent(BaseEvent):
    place_id: UUID
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime


class PlaceOut(BasePlace):
    model_config = ConfigDict(from_attributes=True)


class EventOut(BaseEvent):
    model_config = ConfigDict(from_attributes=True)

    place: PlaceOut


class PageWithEventsOut(BaseModel):
    counts: int
    next: str | None
    previous: str | None
    results: list[EventOut]
