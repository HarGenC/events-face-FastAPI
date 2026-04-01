from fastapi import APIRouter, Depends, Response
from prometheus_client import REGISTRY, generate_latest

from app.dependencies.metrics import get_event_repository
from app.modules.events.repository import EventsRepository
from app.observability.metrics import events_total

router = APIRouter()


@router.get("/metrics")
async def metrics(repo: EventsRepository = Depends(get_event_repository)):
    events_total.set(await repo.get_count())
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain",
    )
