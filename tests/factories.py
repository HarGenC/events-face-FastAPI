from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.events.models import Events, Place
from app.modules.sync.enums import SyncStatus
from app.modules.sync.models import SyncLogs

UTC = timezone.utc


async def create_place(
    session: AsyncSession,
    *,
    id: UUID | None = None,
    name: str = "Конференц-зал Технопарк",
    city: str = "Москва",
    address: str = "ул. Ленина, д. 1",
    seats_pattern: str = "A1-1000,B1-2000",
    changed_at: datetime = datetime.fromisoformat("2025-01-01T03:00:00+03:00"),
    created_at: datetime = datetime.fromisoformat("2025-01-01T03:00:00+03:00"),
) -> Place:

    place = Place(
        id=id or uuid4(),
        name=name,
        city=city,
        address=address,
        seats_pattern=seats_pattern,
        changed_at=changed_at,
        created_at=created_at,
    )

    session.add(place)
    await session.flush()
    return place


async def create_event(
    session: AsyncSession,
    *,
    id: UUID | None = None,
    name: str = "Конференция по Python",
    place_id: UUID,
    event_time: datetime = datetime.fromisoformat("2025-01-03T03:00:00+03:00"),
    registration_deadline: datetime = datetime.fromisoformat(
        "2025-01-02T03:00:00+03:00"
    ),
    status: str = "published",
    number_of_visitors: int = 0,
    created_at: datetime = datetime.fromisoformat("2025-01-01T03:00:00+03:00"),
    changed_at: datetime = datetime.fromisoformat("2025-01-01T03:00:00+03:00"),
    status_changed_at: datetime = datetime.fromisoformat("2025-01-01T03:00:00+03:00"),
) -> Events:

    event = Events(
        id=id or uuid4(),
        place_id=place_id,
        name=name,
        event_time=event_time,
        registration_deadline=registration_deadline,
        status=status,
        number_of_visitors=number_of_visitors,
        created_at=created_at,
        changed_at=changed_at,
        status_changed_at=status_changed_at,
    )

    session.add(event)
    await session.flush()
    return event


async def create_sync_log(
    session: AsyncSession,
    *,
    id: UUID | None = None,
    last_changed_at: datetime | None = None,
    last_sync_time: datetime | None = None,
    sync_status: SyncStatus = SyncStatus.SUCCESS,
) -> SyncLogs:

    if id is None:
        id = uuid4()
    if last_changed_at is None:
        last_changed_at = datetime.now(UTC)
    if last_sync_time is None:
        last_sync_time = datetime.now(UTC)
    sync_log = SyncLogs(
        id=id,
        last_changed_at=last_changed_at,
        last_sync_time=last_sync_time,
        sync_status=sync_status,
    )

    session.add(sync_log)
    await session.flush()
    return sync_log
