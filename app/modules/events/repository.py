from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import UUID, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.events.schemas import CreateEvent, CreatePlace

from .models import Events, Place


class EventsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: UUID):
        stmt = (
            select(Events)
            .where(Events.id == event_id)
            .options(joinedload(Events.place))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_page(
        self, page: int, page_size: int, date_from: datetime | None = None
    ):
        if date_from is None:
            results = await self.session.execute(
                select(Events)
                .options(selectinload(Events.place))
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        else:
            results = await self.session.execute(
                select(Events)
                .where(Events.event_time > date_from)
                .options(selectinload(Events.place))
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        return results.scalars().all()

    async def get_count(self, date_from: datetime | None = None):
        if date_from is None:
            result = await self.session.execute(select(func.count(Events.id)))
        else:
            result = await self.session.execute(
                select(func.count(Events.id)).where(Events.event_time > date_from)
            )
        return result.scalar_one()

    async def create(self, data: CreateEvent):
        stmt = (
            insert(Events)
            .values(**data.model_dump())
            .on_conflict_do_nothing(index_elements=["id"])
        )
        await self.session.execute(stmt)
        await self.session.commit()

        result = await self.session.execute(select(Events).where(Events.id == data.id))
        event = result.scalar_one_or_none()

        if event is None:
            raise ValueError(f"Failed to create or retrieve event with id {data.id}")

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
        stmt = (
            insert(Place)
            .values(**data.model_dump())
            .on_conflict_do_nothing(index_elements=["id"])
        )
        await self.session.execute(stmt)
        await self.session.commit()

        result = await self.session.execute(select(Place).where(Place.id == data.id))
        place = result.scalar_one_or_none()

        if place is None:
            raise ValueError(f"Failed to create or retrieve place with id {data.id}")

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
