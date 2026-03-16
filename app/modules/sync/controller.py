from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.sync.service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(session: AsyncSession = Depends(get_session)):
    sync_service = SyncService(session)
    await sync_service.do_sync()
    return {"message": "Synchronization triggered successfully"}
