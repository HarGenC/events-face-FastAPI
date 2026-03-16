from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sync.enums import SyncStatus
from app.modules.sync.repository import SyncRepository
from app.modules.sync.schemas import CreateSyncLog
from tests.factories import create_sync_log

UTC = timezone.utc


@pytest.mark.asyncio
async def test_create_sync_log(session: AsyncSession):
    repo = SyncRepository(session)

    sync_log_data = CreateSyncLog(
        id="650e8400-e29b-41d4-a716-446655440001",
        last_changed_at=datetime.now(UTC),
        last_sync_time=datetime.now(UTC),
        sync_status=SyncStatus.SUCCESS,
    )

    sync_log = await repo.create(sync_log_data)

    assert sync_log.id == sync_log_data.id
    assert sync_log.last_changed_at == sync_log_data.last_changed_at
    assert sync_log.last_sync_time == sync_log_data.last_sync_time
    assert sync_log.sync_status == sync_log_data.sync_status


class TestSyncLogGet:
    @pytest.mark.asyncio
    async def test_get_one_sync_log(self, session: AsyncSession):
        repo = SyncRepository(session)
        id = uuid4()
        last_changed_at = datetime.now(UTC)
        last_sync_time = datetime.now(UTC)

        await create_sync_log(
            session,
            id=id,
            last_changed_at=last_changed_at,
            last_sync_time=last_sync_time,
        )

        got_sync_log = await repo.get_last_sync()

        assert got_sync_log.id == id
        assert got_sync_log.last_changed_at == last_changed_at
        assert got_sync_log.last_sync_time == last_sync_time

    @pytest.mark.asyncio
    async def test_get_last_sync_log(self, session: AsyncSession):
        repo = SyncRepository(session)
        now = datetime.now(UTC)
        three_hours_later = datetime.now(UTC) + timedelta(hours=3)
        one_hour_later = datetime.now(UTC) + timedelta(hours=1)

        await create_sync_log(session, last_changed_at=now, last_sync_time=now)
        id = uuid4()
        await create_sync_log(
            session,
            id=id,
            last_changed_at=three_hours_later,
            last_sync_time=three_hours_later,
        )
        await create_sync_log(
            session, last_changed_at=one_hour_later, last_sync_time=one_hour_later
        )
        got_sync_log = await repo.get_last_sync()

        assert got_sync_log.id == id
        assert got_sync_log.last_changed_at == three_hours_later

    @pytest.mark.asyncio
    async def test_get_not_exist_sync_log(self, session: AsyncSession):
        repo = SyncRepository(session)

        got_sync_log = await repo.get_last_sync()

        assert got_sync_log is None
