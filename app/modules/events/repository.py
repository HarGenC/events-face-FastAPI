from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.schemas import CreateEvent, CreatePlace

from .models import Events, Place


class EventsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: UUID):
        result = await self.session.execute(select(Events).where(Events.id == event_id))
        return result.scalar_one_or_none()

    async def create(self, data: CreateEvent):
        event = Events(**data.model_dump())

        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def update(self, event_id: UUID, data: CreateEvent):
        result = await self.session.execute(
            select(Events).where(Events.id == event_id).with_for_update()
        )
        event = result.scalar_one_or_none()

        if event is None:
            raise ValueError("Event not found")

        for key, value in data.model_dump().items():
            setattr(event, key, value)

        await self.session.commit()
        await self.session.refresh(event)
        return event


class PlacesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, place_id: UUID):
        result = await self.session.execute(select(Place).where(Place.id == place_id))
        return result.scalar_one_or_none()

    async def create(self, data: CreatePlace):
        place = Place(**data.model_dump())

        self.session.add(place)
        await self.session.commit()
        await self.session.refresh(place)
        return place

    async def update(self, place_id: UUID, data: CreatePlace):
        result = await self.session.execute(
            select(Place).where(Place.id == place_id).with_for_update()
        )
        place = result.scalar_one_or_none()

        if place is None:
            raise ValueError("Place not found")

        for key, value in data.model_dump().items():
            setattr(place, key, value)

        await self.session.commit()
        await self.session.refresh(place)
        return place
