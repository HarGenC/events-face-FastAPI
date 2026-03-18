from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.tickets.dependencies import get_ticket_service
from app.modules.tickets.schemas import RegistrationInfoIn
from app.modules.tickets.service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", summary="Register and get ticket", status_code=HTTPStatus.CREATED)
async def register_for_event(
    registration_info: RegistrationInfoIn,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    ticket_id = await ticket_service.register_for_event(registration_info)
    return {"ticket_id": ticket_id}


@router.delete("/{ticket_id}", summary="cancel registration")
async def unregister_ticket(
    ticket_id: UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    await ticket_service.cancel_registration(ticket_id)
    return {"success": True}
