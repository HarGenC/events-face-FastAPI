from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.events.repository import EventsRepository


async def get_event_repository(session: AsyncSession = Depends(get_session)):
    return EventsRepository(session)
