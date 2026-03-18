from sqlalchemy import delete, select
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

    async def get_registration(self, ticket_id: UUID):
        result = await self.session.execute(
            select(Registrations).where(Registrations.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def delete_registration(self, event_id: UUID, ticket_id: UUID):
        stmt = delete(Registrations).where(
            Registrations.event_id == event_id, Registrations.ticket_id == ticket_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
