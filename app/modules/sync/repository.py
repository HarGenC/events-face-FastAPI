from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sync.models import SyncLogs
from app.modules.sync.schemas import CreateSyncLog


class SyncRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_last_sync(self):
        result = await self.session.execute(
            select(SyncLogs).order_by(desc(SyncLogs.last_changed_at)).limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, data: CreateSyncLog):
        sync_log = SyncLogs(**(data.model_dump()))
        self.session.add(sync_log)
        await self.session.commit()
        await self.session.refresh(sync_log)
        return sync_log

    async def update(self, data: CreateSyncLog):
        result = await self.session.execute(
            select(SyncLogs).where(SyncLogs.id == data.id).with_for_update()
        )
        sync_log = result.scalar_one_or_none()

        if sync_log is None:
            raise ValueError("Sync log not found")

        for key, value in data.model_dump().items():
            setattr(sync_log, key, value)

        await self.session.commit()
        await self.session.refresh(sync_log)
        return sync_log
