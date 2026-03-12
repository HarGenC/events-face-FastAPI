from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.clients.events_face import EventsProviderClient
from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.service import EventService, PlaceService
from app.modules.sync.repository import SyncRepository
from app.modules.sync.service import SyncService

router = APIRouter()


@router.post("/trigger")
async def trigger_sync(session: AsyncSession = Depends(get_session)):
    repo_sync = SyncRepository(session)
    event_service = EventService(EventsRepository(session))
    place_service = PlaceService(PlacesRepository(session))
    external_client = EventsProviderClient()
    sync_service = SyncService(
        repo=repo_sync,
        event_service=event_service,
        place_service=place_service,
        external_client=external_client,
    )
    await sync_service.do_sync()
    return {"message": "Synchronization triggered successfully"}
