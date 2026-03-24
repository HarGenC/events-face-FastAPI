from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_seats_cache
from app.core.database import get_session
from app.modules.clients.events_face import EventsProviderClient
from app.modules.events.repository import EventsRepository
from app.modules.events.service import EventService
from app.modules.notifications.repository import OutboxRepository
from app.modules.notifications.service import NotificationService
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.service import TicketService


def get_ticket_repository(session: AsyncSession = Depends(get_session)):
    return TicketRepository(session)


def get_ticket_service(session: AsyncSession = Depends(get_session)):
    ticket_repo = TicketRepository(session)
    outbox_repo = OutboxRepository(session)
    event_service = EventService(
        EventsRepository(session), seats_cache=get_seats_cache()
    )
    event_provider_client = EventsProviderClient()
    notification_service = NotificationService(repo=outbox_repo)
    return TicketService(
        repo=ticket_repo,
        event_service=event_service,
        event_provider_client=event_provider_client,
        notification_service=notification_service,
    )
