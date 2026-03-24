from app.modules.notifications.repository import OutboxRepository
from app.modules.notifications.schemas import CreateNotification, UpdateNotification


class NotificationService:
    def __init__(self, repo: OutboxRepository):
        self.repo = repo

    async def create_notification(self, data: CreateNotification):
        await self.repo.create(data=data)

    async def update_notification(self, data: UpdateNotification):
        await self.repo.update(data=data)

    async def get_notifications(self, limit: int = 25):
        await self.repo.get_notifications(limit=limit)
