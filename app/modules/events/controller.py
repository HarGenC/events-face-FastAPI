from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.events.repository import EventsRepository
from app.modules.events.schemas import EventOut
from app.modules.events.service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", summary="Get page with events")
async def get_events(
    date_from: datetime = None,
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_session),
):
    event_service = EventService(EventsRepository(session))
    result = await event_service.get_page_with_events(
        page=page, page_size=page_size, date_from=date_from
    )
    return result


@router.get("/{event_id}", response_model=Optional[EventOut], summary="Get event by ID")
async def get_event(event_id: UUID, session: AsyncSession = Depends(get_session)):
    event_service = EventService(EventsRepository(session))
    result = await event_service.get_event(event_id)

    return result
