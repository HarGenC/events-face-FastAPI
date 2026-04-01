from fastapi import APIRouter

from app.modules.events.controller import router as events_router
from app.modules.sync.controller import router as sync_router
from app.modules.tickets.controller import router as tickets_router

router = APIRouter(prefix="/api")

router.include_router(events_router)
router.include_router(sync_router)
router.include_router(tickets_router)


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
