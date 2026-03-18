from http import HTTPStatus

from fastapi import APIRouter, Depends, Response

from app.modules.tickets.dependencies import get_ticket_service
from app.modules.tickets.schemas import RegistrationInfoIn
from app.modules.tickets.service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", summary="Register and get ticket")
async def register_for_event(
    registration_info: RegistrationInfoIn,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    ticket_id = await ticket_service.register_for_event(registration_info)
    return Response(
        content={"ticket_id": ticket_id},
        media_type="application/json",
        status_code=HTTPStatus.CREATED,
    )
