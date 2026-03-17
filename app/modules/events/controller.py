from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.events.dependencies import get_event_service
from app.modules.events.schemas import EventOut, RegistrationInfoIn, SeatsOut
from app.modules.events.service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", summary="Get page with events")
async def get_events(
    date_from: datetime = None,
    page: int = 1,
    page_size: int = 20,
    event_service: EventService = Depends(get_event_service),
):
    result = await event_service.get_page_with_events(
        page=page, page_size=page_size, date_from=date_from
    )
    return result


@router.get("/{event_id}", response_model=Optional[EventOut], summary="Get event by ID")
async def get_event_detail(
    event_id: UUID, event_service: EventService = Depends(get_event_service)
):
    result = await event_service.get_event(event_id)

    return result


@router.get("/{event_id}/seats", response_model=SeatsOut)
async def get_seats(
    event_id: UUID, event_service: EventService = Depends(get_event_service)
):
    await event_service.check_event_status(event_id)
    result = await event_service.get_available_seats(event_id)

    return SeatsOut(event_id=event_id, available_seats=result)


@router.post("/{event_id}/register/", response_model=UUID)
async def register_for_event(
    event_id: UUID,
    registration_info: RegistrationInfoIn,
    event_service: EventService = Depends(get_event_service),
):
    ticket_id = await event_service.register_for_event(event_id, registration_info)

    return {"ticket_id": ticket_id}
