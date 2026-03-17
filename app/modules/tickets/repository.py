from httpx import delete
from sqlalchemy.dialects.postgresql import UUID, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Registrations
from .schemas import CreateRegistration


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_registration(self, data: CreateRegistration):
        stmt = insert(Registrations).values(**data.model_dump())
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_registration(self, event_id: UUID, ticket_id: UUID):
        stmt = delete(Registrations).where(
            Registrations.event_id == event_id, Registrations.ticket_id == ticket_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
