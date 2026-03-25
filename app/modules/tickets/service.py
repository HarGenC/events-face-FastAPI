from datetime import datetime
from uuid import UUID, uuid4

from fastapi import HTTPException
from loguru import logger

from app.modules.clients.events_face import EventsProviderClient
from app.modules.events.service import EventService
from app.modules.notifications.enums import NotificationStatus
from app.modules.notifications.schemas import CreateNotification
from app.modules.notifications.service import NotificationService
from app.modules.tickets.models import Registrations
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.schemas import CreateRegistration, RegistrationInfoIn


class TicketService:
    def __init__(
        self,
        repo: TicketRepository,
        event_service: EventService,
        event_provider_client: EventsProviderClient,
        notification_service: NotificationService,
    ):
        self.repo = repo
        self.notification_service = notification_service
        self.event_service = event_service
        self.event_provider_client = event_provider_client

    async def register_for_event(self, registration_info: RegistrationInfoIn):
        registration = await self.repo.get_registration_by_idempotency_key(
            registration_info.idempotency_key
        )
        if registration:
            if await self.is_same_registration(registration_info, registration):
                return registration.ticket_id
            else:
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency key already used with different payload",
                )

        event = await self.event_service.get_event(registration_info.event_id)
        if event.registration_deadline < datetime.now(
            event.registration_deadline.tzinfo
        ):
            raise HTTPException(
                status_code=400, detail="Registration deadline has passed"
            )

        await self.event_service.check_event_status(registration_info.event_id, event)

        if not await self._seat_exists(
            registration_info.seat, event.place.seats_pattern
        ):
            raise HTTPException(status_code=400, detail="Seat does not exist")

        available_seats = await self.event_service.get_available_seats(
            registration_info.event_id
        )
        if registration_info.seat not in available_seats:
            raise HTTPException(status_code=400, detail="Seat is not available")

        result = await self.event_provider_client.register(registration_info)
        ticket_id = result["ticket_id"]
        logger.info(
            f"Registered for event {registration_info.event_id} with ticket {ticket_id}"
        )

        await self.repo.create_registration(
            CreateRegistration(
                event_id=registration_info.event_id,
                ticket_id=ticket_id,
                seat=registration_info.seat,
                first_name=registration_info.first_name,
                last_name=registration_info.last_name,
                email=registration_info.email,
                idempotency_key=registration_info.idempotency_key,
            )
        )
        payload = {
            "message": f"Вы успешно зарегестрированы на мероприятие - {event.name}",
            "reference_id": str(ticket_id),
            "idempotency_key": str(uuid4()),
        }
        await self.notification_service.create_notification(
            CreateNotification(
                event_type="notification",
                payload=payload,
                status=NotificationStatus.PENDING,
            )
        )
        await self.repo.session.commit()

        return ticket_id

    async def _seat_exists(self, seat: str, seats_pattern: str) -> bool:
        row = seat[0]
        try:
            number = int(seat[1:])
        except ValueError:
            return False

        for part in seats_pattern.split(","):
            part_row = part[0]
            try:
                start, end = map(int, part[1:].split("-"))
            except ValueError:
                continue

            if row == part_row and start <= number <= end:
                return True

        return False

    async def cancel_registration(self, ticket_id: UUID):
        registration = await self.repo.get_registration_by_ticket_id(ticket_id)
        if registration is None:
            raise HTTPException(status_code=404, detail="Registration not found")
        event = await self.event_service.get_event(registration.event_id)
        if event.event_time < datetime.now(event.event_time.tzinfo):
            raise HTTPException(
                status_code=400, detail="The cancellation deadline has expired"
            )

        (
            await self.event_provider_client.cancel_registration(
                registration.event_id, ticket_id
            ),
        )
        await self.repo.delete_registration(registration.event_id, ticket_id)

    async def is_same_registration(
        self, registration_info: RegistrationInfoIn, current_registration: Registrations
    ):
        return not any(
            getattr(registration_info, field) != getattr(current_registration, field)
            for field in ("email", "first_name", "last_name", "seat")
        )
