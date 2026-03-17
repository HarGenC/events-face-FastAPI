from fastapi import APIRouter, Depends

from app.modules.sync.dependencies import get_sync_service
from app.modules.sync.service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(sync_service: SyncService = Depends(get_sync_service)):
    await sync_service.do_sync()
    return {"message": "Synchronization triggered successfully"}
