from http import HTTPStatus

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
