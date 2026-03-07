from fastapi import APIRouter

from app.modules.users.presentation.router import router as users_router

router = APIRouter(prefix="/api")

router.include_router(users_router, prefix="/users", tags=["Users"])


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
