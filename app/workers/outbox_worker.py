from loguru import logger

from app.core.database import AsyncSessionLocal
from app.modules.clients.notification import NotificationClient
from app.modules.notifications.service import NotificationService, OutboxRepository


async def outbox_worker():
    logger.info("Starting outbox worker")
    try:
        async with AsyncSessionLocal() as session:
            repo = OutboxRepository(session)
            notification_client = NotificationClient()
            notifications_service = NotificationService(repo, notification_client)
            await notifications_service.send_pending_notifications()
    except Exception:
        logger.exception("Outbox processing failed")

    logger.info("Outbox finished")
