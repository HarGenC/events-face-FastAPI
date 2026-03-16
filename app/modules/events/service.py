from datetime import datetime
from urllib.parse import urlencode

from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID

from app.core.config import settings
from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.schemas import CreateEvent, CreatePlace, PageWithEventsOut


class EventService:
    def __init__(self, repo: EventsRepository):
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
        return f"http://{settings.HOSTNAME}:{settings.PORT}/api/events?{query}"


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
