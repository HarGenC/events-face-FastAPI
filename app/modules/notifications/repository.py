from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Outbox
from app.modules.notifications.schemas import CreateNotification, UpdateNotification


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_notifications(self, limit: int):
        notifications = await self.session.execute(
            select(Outbox)
            .where(
                Outbox.status == "pending",
                Outbox.retry_count < 5,
                or_(Outbox.next_retry_at is None, Outbox.next_retry_at <= func.now()),
            )
            .order_by(Outbox.created_at)
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        return notifications.scalars().all()

    async def create(self, data: CreateNotification):
        outbox_item = Outbox(**(data.model_dump()))
        self.session.add(outbox_item)
        await self.session.flush()
        await self.session.refresh(outbox_item)
        return outbox_item

    async def update(self, data: UpdateNotification):
        result = await self.session.execute(
            select(Outbox).where(Outbox.id == data.id).with_for_update()
        )
        outbox_item = result.scalar_one_or_none()

        if outbox_item is None:
            raise ValueError("Notification not found")

        for key, value in data.model_dump().items():
            setattr(outbox_item, key, value)

        await self.session.refresh(outbox_item)
        return outbox_item
