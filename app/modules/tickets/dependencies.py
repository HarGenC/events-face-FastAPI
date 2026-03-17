from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_seats_cache
from app.core.database import get_session
from app.modules.events.repository import EventsRepository
from app.modules.events.service import EventService
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.service import TicketService


def get_ticket_repository(session: AsyncSession = Depends(get_session)):
    return TicketRepository(session)


def get_ticket_service(session: AsyncSession = Depends(get_session)):
    repo = TicketRepository(session)
    event_service = EventService(
        EventsRepository(session), seats_cache=get_seats_cache()
    )
    return TicketService(repo=repo, event_service=event_service)
