from loguru import logger

from app.core.database import AsyncSessionLocal
from app.modules.clients.events_face import EventsProviderClient
from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.service import EventService, PlaceService
from app.modules.sync.service import SyncService


async def sync_worker():
    try:
        async with AsyncSessionLocal() as session:
            events_provider_client = EventsProviderClient()
            event_service = EventService(
                EventsRepository(session), events_provider_client
            )
            place_service = PlaceService(PlacesRepository(session))
            service = SyncService(session, event_service, place_service)
            await service.do_sync()
    except Exception:
        logger.exception("Sync failed")
