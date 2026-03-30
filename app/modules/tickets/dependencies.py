from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_seats_cache
from app.core.database import get_session
from app.modules.clients.events_face import EventsProviderClient
from app.modules.clients.notification import NotificationClient
from app.modules.events.repository import EventsRepository
from app.modules.events.service import EventService
from app.modules.notifications.repository import OutboxRepository
from app.modules.notifications.service import NotificationService
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.service import TicketService


def get_ticket_repository(session: AsyncSession = Depends(get_session)):
    return TicketRepository(session)


def get_events_repository(session: AsyncSession = Depends(get_session)):
    return EventsRepository(session)


def get_outbox_repository(session: AsyncSession = Depends(get_session)):
    return OutboxRepository(session)


def get_events_provider_client():
    return EventsProviderClient()


def get_notification_client():
    return NotificationClient()


def get_event_service(
    repo: EventsRepository = Depends(get_events_repository),
    client: EventsProviderClient = Depends(get_events_provider_client),
):
    return EventService(repo, client, seats_cache=get_seats_cache())


def get_notification_service(
    repo: OutboxRepository = Depends(get_outbox_repository),
    client: NotificationClient = Depends(get_notification_client),
):
    return NotificationService(repo=repo, notification_client=client)


def get_ticket_service(
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
    event_service: EventService = Depends(get_event_service),
    event_provider_client: EventsProviderClient = Depends(get_events_provider_client),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return TicketService(
        repo=ticket_repo,
        event_service=event_service,
        event_provider_client=event_provider_client,
        notification_service=notification_service,
    )
