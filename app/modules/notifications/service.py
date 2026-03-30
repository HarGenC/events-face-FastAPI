import asyncio
from datetime import datetime, timedelta, timezone

from httpx import HTTPStatusError
from loguru import logger

from app.core.database import AsyncSessionLocal
from app.modules.clients.notification import NotificationClient
from app.modules.notifications.enums import NotificationStatus
from app.modules.notifications.repository import OutboxRepository
from app.modules.notifications.schemas import CreateNotification, UpdateNotification


class NotificationService:
    def __init__(self, repo: OutboxRepository, notification_client: NotificationClient):
        self.repo = repo
        self.semaphore = asyncio.Semaphore(10)
        self.notification_client = notification_client
        self.backoff = 2.0

    async def create_notification(self, data: CreateNotification):
        await self.repo.create(data=data)

    async def send_pending_notifications(self, limit: int = 25):

        while True:
            notifications = await self.repo.claim_notifications(limit)
            if not notifications:
                break
            tasks = [
                self._send_with_limit(notification) for notification in notifications
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_with_limit(self, notification: UpdateNotification):
        async with self.semaphore:
            return await self._send_notification(notification)

    async def _send_notification(self, notification: UpdateNotification):
        async with AsyncSessionLocal() as session:
            repo = OutboxRepository(session)
            try:
                await self.notification_client.send_notification(notification.payload)
                notification.status = NotificationStatus.SENT
            except HTTPStatusError as e:
                if e.response.status_code == 409:
                    notification.status = NotificationStatus.SENT
                else:
                    await self._mark_for_retry(notification)
            except Exception:
                await self._mark_for_retry(notification)
            await repo.update(notification)
            if notification.status == NotificationStatus.SENT:
                logger.info(
                    "Notification sent successfully, idempotency_key=%s",
                    notification.payload["idempotency_key"],
                )
            else:
                logger.info(
                    "Notification failed, idempotency_key=%s",
                    notification.payload["idempotency_key"],
                )

    async def _mark_for_retry(self, notification: UpdateNotification):
        notification.retry_count += 1
        notification.next_retry_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.backoff**notification.retry_count
        )
