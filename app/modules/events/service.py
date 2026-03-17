import re
from datetime import datetime
from urllib.parse import urlencode

from cachetools import TTLCache
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID

from app.core.config import settings
from app.modules.clients.events_face import AsyncEventsProviderClient
from app.modules.events.models import Events
from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.schemas import (
    CreateEvent,
    CreatePlace,
    PageWithEventsOut,
)


class EventService:
    def __init__(self, repo: EventsRepository, seats_cache: TTLCache | None = None):
        self.seats_cache = seats_cache
        self.repo = repo
        self.DEFAULT_PAGE = 1
        self.DEFAULT_PAGE_SIZE = 20

    async def get_event(self, event_id: UUID):
        event = await self.repo.get_by_id(event_id)

        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    async def create_event(self, data: CreateEvent):
        event = await self.repo.get_by_id(data.id)

        if event:
            return await self.repo.update(data.id, data)

        return await self.repo.create(data)

    async def get_page_with_events(
        self, page: int, page_size: int, date_from: datetime | None = None
    ) -> PageWithEventsOut:
        if page_size < 1 or page < 1:
            raise ValueError("Data is not valid")

        count = await self.repo.get_count(date_from)
        offset = (page - 1) * page_size

        if count < offset:
            results = []
        else:
            results = await self.repo.get_page(page, page_size, date_from)

        if count > page * page_size:
            next_page = await self._build_url(page + 1, page_size, date_from)
        else:
            next_page = None

        if page > 1 and count > offset:
            previous_page = await self._build_url(page - 1, page_size, date_from)
        else:
            previous_page = None

        return PageWithEventsOut(
            count=count, next=next_page, previous=previous_page, results=results
        )

    async def _build_url(
        self, page: int, page_size: int, date_from: datetime | None = None
    ):
        params = {"page": page}

        if page_size != self.DEFAULT_PAGE_SIZE:
            params["page_size"] = page_size

        if date_from is not None:
            params["date_from"] = date_from.strftime("%Y-%m-%d")

        query = urlencode(params)
        return f"{settings.HOSTNAME}:{settings.PORT}/api/events?{query}"

    async def get_available_seats(self, event_id: UUID):
        if self.seats_cache is None:
            raise ValueError("Seats cache is not configured")
        if event_id in self.seats_cache:
            return self.seats_cache[event_id]
        event_provider_client = AsyncEventsProviderClient()
        available_seats = sorted(
            await event_provider_client.get_seats(event_id), key=self._seat_key
        )
        self.seats_cache[event_id] = available_seats
        return available_seats

    async def check_event_status(self, event_id: UUID, event: Events | None = None):
        if event is None:
            event = await self.get_event(event_id)
        if event.status != "published":
            raise HTTPException(status_code=400, detail="Event is not published")

    def _seat_key(self, seat: str):
        # Берём буквы в начале и число после них
        match = re.match(r"([A-Z]+)(\d+)", seat)
        if match:
            letter, number = match.groups()
            return (letter, int(number))
        return (seat, 0)


class PlaceService:
    def __init__(self, repo: PlacesRepository):
        self.repo = repo

    async def get_place(self, place_id: UUID):
        place = await self.repo.get_by_id(place_id)

        if place is None:
            raise ValueError("Place not found")

        return place

    async def create_place(self, data: CreatePlace):
        place = await self.repo.get_by_id(data.id)

        if place:
            return await self.repo.update(data.id, data)

        return await self.repo.create(data)
