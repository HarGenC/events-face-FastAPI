from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.repository import PlacesRepository
from app.modules.events.schemas import CreatePlace
from tests.factories import create_place


class TestPlaceCreate:
    @pytest.mark.asyncio
    async def test_create_place(self, session: AsyncSession):
        repo = PlacesRepository(session)

        place_data = CreatePlace(
            id="650e8400-e29b-41d4-a716-446655440001",
            name="Конференц-зал Технопарк",
            city="Москва",
            address="ул. Ленина, д. 1",
            seats_pattern="A1-1000,B1-2000",
            changed_at="2025-01-01T03:00:00+03:00",
            created_at="2025-01-01T03:00:00+03:00",
        )

        place = await repo.create(place_data)

        assert place.id == place_data.id
        assert place.name == place_data.name
        assert place.city == place_data.city
        assert place.address == place_data.address
        assert place.seats_pattern == place_data.seats_pattern
        assert place.changed_at == place_data.changed_at
        assert place.created_at == place_data.created_at

    @pytest.mark.asyncio
    async def test_create_place_twice(self, session: AsyncSession):
        repo = PlacesRepository(session)

        place_data = CreatePlace(
            id="650e8400-e29b-41d4-a716-446655440001",
            name="Конференц-зал Технопарк",
            city="Москва",
            address="ул. Ленина, д. 1",
            seats_pattern="A1-1000,B1-2000",
            changed_at="2025-01-01T03:00:00+03:00",
            created_at="2025-01-01T03:00:00+03:00",
        )

        place = await repo.create(place_data)
        place = await repo.create(place_data)

        assert place.id == place_data.id
        assert place.name == place_data.name
        assert place.city == place_data.city
        assert place.address == place_data.address
        assert place.seats_pattern == place_data.seats_pattern
        assert place.changed_at == place_data.changed_at
        assert place.created_at == place_data.created_at


class TestPlaceGet:
    @pytest.mark.asyncio
    async def test_get_exist_event(self, session: AsyncSession):
        repo = PlacesRepository(session)

        place = await create_place(session)

        got_place = await repo.get_by_id(place.id)

        assert got_place.id == place.id
        assert got_place.name == place.name
        assert got_place.city == place.city
        assert got_place.address == place.address
        assert got_place.seats_pattern == place.seats_pattern
        assert got_place.changed_at == place.changed_at
        assert got_place.created_at == place.created_at

    @pytest.mark.asyncio
    async def test_get_not_exist_event(self, session: AsyncSession):
        repo = PlacesRepository(session)

        got_place = await repo.get_by_id(uuid4())

        assert got_place is None
