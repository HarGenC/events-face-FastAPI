from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.modules.tickets.dependencies import get_ticket_service
from app.modules.tickets.schemas import RegistrationInfoIn
from app.modules.tickets.service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", summary="Register and get ticket", status_code=HTTPStatus.CREATED)
async def register_for_event(
    registration_info: RegistrationInfoIn,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    result = await ticket_service.register_for_event(registration_info)
    if isinstance(result, dict) and "status_code" in result and "detail" in result:
        raise HTTPException(
            status_code=result.get("status_code"), detail=result.get("detail")
        )

    return {"ticket_id": result}


@router.delete("/{ticket_id}", summary="cancel registration")
async def unregister_ticket(
    ticket_id: UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    result = await ticket_service.cancel_registration(ticket_id)
    if result is None:
        return {"success": True}
    raise HTTPException(
        status_code=result.get("status_code"), detail=result.get("detail")
    )
