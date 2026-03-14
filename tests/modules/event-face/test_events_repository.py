from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.repository import EventsRepository
from app.modules.events.schemas import CreateEvent
from tests.factories import create_event, create_place


class TestEventsCreate:
    @pytest.mark.asyncio
    async def test_create_event(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)

        event_data = CreateEvent(
            id=uuid4(),
            name="Конференция по Python",
            place_id=place.id,
            event_time=datetime.fromisoformat("2026-01-11T17:00:00+03:00"),
            registration_deadline=datetime.fromisoformat("2026-01-10T17:00:00+03:00"),
            status="published",
            number_of_visitors=5,
            changed_at=datetime.fromisoformat("2026-01-04T22:28:35.325270+03:00"),
            created_at=datetime.fromisoformat("2026-01-04T22:28:35.325302+03:00"),
            status_changed_at=datetime.fromisoformat(
                "2026-01-04T22:28:35.325386+03:00"
            ),
        )

        event = await repo.create(event_data)

        assert event.id == event_data.id
        assert event.name == event_data.name
        assert event.place_id == event_data.place_id
        assert event.event_time == event_data.event_time
        assert event.registration_deadline == event_data.registration_deadline
        assert event.status == event_data.status
        assert event.number_of_visitors == event_data.number_of_visitors
        assert event.changed_at == event_data.changed_at
        assert event.created_at == event_data.created_at
        assert event.status_changed_at == event_data.status_changed_at

    @pytest.mark.asyncio
    async def test_create_event_twice(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)

        event_data = CreateEvent(
            id=uuid4(),
            name="Конференция по Python",
            place_id=place.id,
            event_time=datetime.fromisoformat("2026-01-11T17:00:00+03:00"),
            registration_deadline=datetime.fromisoformat("2026-01-10T17:00:00+03:00"),
            status="published",
            number_of_visitors=5,
            changed_at=datetime.fromisoformat("2026-01-04T22:28:35.325270+03:00"),
            created_at=datetime.fromisoformat("2026-01-04T22:28:35.325302+03:00"),
            status_changed_at=datetime.fromisoformat(
                "2026-01-04T22:28:35.325386+03:00"
            ),
        )

        event = await repo.create(event_data)
        event = await repo.create(event_data)

        assert event.id == event_data.id
        assert event.name == event_data.name
        assert event.place_id == event_data.place_id
        assert event.event_time == event_data.event_time
        assert event.registration_deadline == event_data.registration_deadline
        assert event.status == event_data.status
        assert event.number_of_visitors == event_data.number_of_visitors
        assert event.changed_at == event_data.changed_at
        assert event.created_at == event_data.created_at
        assert event.status_changed_at == event_data.status_changed_at


class TestEventsGet:
    @pytest.mark.asyncio
    async def test_get_exist_event(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)
        event = await create_event(session, place_id=place.id)

        got_event = await repo.get_by_id(event.id)

        assert got_event.id == event.id
        assert got_event.name == event.name
        assert got_event.place_id == event.place_id
        assert got_event.event_time == event.event_time
        assert got_event.registration_deadline == event.registration_deadline
        assert got_event.status == event.status
        assert got_event.number_of_visitors == event.number_of_visitors
        assert got_event.changed_at == event.changed_at
        assert got_event.created_at == event.created_at
        assert got_event.status_changed_at == event.status_changed_at

    @pytest.mark.asyncio
    async def test_get_not_exist_event(self, session: AsyncSession):
        repo = EventsRepository(session)

        got_event = await repo.get_by_id(uuid4())

        assert got_event is None
