from loguru import logger

from app.core.database import AsyncSessionLocal
from app.modules.notifications.service import NotificationService, OutboxRepository


async def outbox_worker():

    while True:
        try:
            async with AsyncSessionLocal() as session:
                repo = OutboxRepository(session)
                notifications_service = NotificationService(repo)
                notifications_service.get_notifications()
                pass  # TODO: implement outbox processing logic
        except Exception:
            logger.exception("Outbox processing failed")
