from fastapi import APIRouter

from app.modules.events.controller import router as events_router
from app.modules.sync.controller import router as sync_router
from app.modules.users.controller import router as users_router

router = APIRouter(prefix="/api")

router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(events_router, prefix="/events", tags=["events"])
router.include_router(sync_router, prefix="/sync", tags=["sync"])


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
