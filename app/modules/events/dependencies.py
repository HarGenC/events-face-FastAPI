from cachetools import TTLCache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_seats_cache
from app.core.database import get_session
from app.modules.clients.events_face import EventsProviderClient
from app.modules.events.repository import EventsRepository
from app.modules.events.service import EventService


def get_event_repository(session: AsyncSession = Depends(get_session)):
    return EventsRepository(session)


def get_event_service(
    seats_cache: TTLCache = Depends(get_seats_cache),
    repo: EventsRepository = Depends(get_event_repository),
):
    events_provider_client = EventsProviderClient()
    return EventService(
        repo=repo, event_provider_client=events_provider_client, seats_cache=seats_cache
    )
