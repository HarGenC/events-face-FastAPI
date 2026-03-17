from datetime import datetime

from fastapi import HTTPException
from loguru import logger

from app.modules.clients.events_face import EventsProviderClient
from app.modules.events.service import EventService
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.schemas import CreateRegistration, RegistrationInfoIn


class TicketService:
    def __init__(self, repo: TicketRepository, event_service: EventService):
        self.repo = repo
        self.event_service = event_service

    async def register_for_event(self, registration_info: RegistrationInfoIn):
        event_provider_client = EventsProviderClient()
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

        result = await event_provider_client.register(registration_info)
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
            )
        )
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

    async def create_registration(self, data: CreateRegistration):
        await self.repo.create_registration(data)
