from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.service import EventService, PlaceService
from app.modules.sync.service import SyncService


async def get_sync_service(
    session: AsyncSession = Depends(get_session),
):
    event_service = EventService(EventsRepository(session))
    place_service = PlaceService(PlacesRepository(session))
    return SyncService(session, event_service, place_service)
