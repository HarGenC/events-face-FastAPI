from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.repository import EventsRepository
from app.modules.events.schemas import CreateEvent
from tests.factories import create_event, create_place

pytestmark = pytest.mark.usefixtures("clean_tables")


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


class TestEventsGetPage:
    @pytest.mark.asyncio
    async def test_get_page_without_filter(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)

        events = [
            await create_event(session, place_id=place.id),
            await create_event(session, place_id=place.id),
            await create_event(session, place_id=place.id),
        ]

        got_events = await repo.get_page(page=1, page_size=2)

        assert len(got_events) == 2
        assert got_events[0].id == events[0].id
        assert got_events[1].id == events[1].id

    @pytest.mark.asyncio
    async def test_get_page_with_filter(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)

        events = [
            await create_event(
                session,
                place_id=place.id,
                event_time=datetime.fromisoformat("2026-01-11T17:00:00+03:00"),
            ),
            await create_event(
                session,
                place_id=place.id,
                event_time=datetime.fromisoformat("2026-01-12T17:00:00+03:00"),
            ),
            await create_event(
                session,
                place_id=place.id,
                event_time=datetime.fromisoformat("2026-01-13T17:00:00+03:00"),
            ),
        ]

        got_events = await repo.get_page(
            page=1,
            page_size=2,
            date_from=datetime.fromisoformat("2026-01-12T00:00:00+03:00"),
        )

        assert len(got_events) == 2
        assert got_events[0].id == events[1].id
        assert got_events[1].id == events[2].id


class TestEventsUpdate:
    @pytest.mark.asyncio
    async def test_update_event(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)
        event = await create_event(session, place_id=place.id)

        update_data = CreateEvent(
            id=event.id,
            name="Конференция по FastAPI",
            status="finished",
            place_id=event.place_id,
            event_time=event.event_time,
            registration_deadline=event.registration_deadline,
            number_of_visitors=event.number_of_visitors,
            changed_at=event.changed_at,
            created_at=event.created_at,
            status_changed_at=datetime.fromisoformat(
                "2026-01-05T22:28:35.325386+03:00"
            ),
        )

        await repo.update(event.id, update_data)

        got_event = await repo.get_by_id(event.id)

        assert got_event.id == event.id
        assert got_event.name == update_data.name
        assert got_event.place_id == event.place_id
        assert got_event.event_time == event.event_time
        assert got_event.registration_deadline == event.registration_deadline
        assert got_event.status == update_data.status
        assert got_event.number_of_visitors == update_data.number_of_visitors
        assert got_event.changed_at == event.changed_at
        assert got_event.created_at == event.created_at
        assert got_event.status_changed_at == event.status_changed_at


class TestEventsGetCount:
    @pytest.mark.asyncio
    async def test_get_count_without_filter(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)

        await create_event(session, place_id=place.id)
        await create_event(session, place_id=place.id)
        await create_event(session, place_id=place.id)

        count = await repo.get_count()

        assert count == 3

    @pytest.mark.asyncio
    async def test_get_count_with_filter(self, session: AsyncSession):
        repo = EventsRepository(session)

        place = await create_place(session)

        await create_event(
            session,
            place_id=place.id,
            event_time=datetime.fromisoformat("2026-01-11T17:00:00+03:00"),
        )
        await create_event(
            session,
            place_id=place.id,
            event_time=datetime.fromisoformat("2026-01-12T17:00:00+03:00"),
        )
        await create_event(
            session,
            place_id=place.id,
            event_time=datetime.fromisoformat("2026-01-13T17:00:00+03:00"),
        )

        count = await repo.get_count(
            date_from=datetime.fromisoformat("2026-01-12T00:00:00+03:00")
        )

        assert count == 2
