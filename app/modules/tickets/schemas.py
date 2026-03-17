from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegistrationInfoIn(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    seat: str


class CreateRegistration(RegistrationInfoIn):
    ticket_id: UUID
