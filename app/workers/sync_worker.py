import asyncio

from loguru import logger

from app.core.database import AsyncSessionLocal
from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.service import EventService, PlaceService
from app.modules.sync.service import SyncService


async def sync_worker():
    DAY = 60 * 60 * 24

    while True:
        try:
            async with AsyncSessionLocal() as session:
                event_service = EventService(EventsRepository(session))
                place_service = PlaceService(PlacesRepository(session))
                service = SyncService(session, event_service, place_service)
                await service.do_sync()
        except Exception:
            logger.exception("Sync failed")
        await asyncio.sleep(DAY)
