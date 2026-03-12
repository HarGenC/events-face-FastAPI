from sqlalchemy.dialects.postgresql import UUID

from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.schemas import CreateEvent, CreatePlace


class EventService:
    def __init__(self, repo: EventsRepository):
        self.repo = repo

    async def get_event(self, event_id: UUID):
        event = await self.repo.get_by_id(event_id)

        if event is None:
            raise ValueError("Event not found")

        return event

    async def create_event(self, data: CreateEvent):
        event = await self.repo.get_by_id(data.id)

        if event:
            return await self.repo.update(data.id, data)

        return await self.repo.create(data)


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
