import uuid
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clients.events_face import EventsProviderClient
from app.modules.clients.events_paginator import EventsPaginator
from app.modules.events.repository import EventsRepository, PlacesRepository
from app.modules.events.schemas import CreateEvent, CreatePlace
from app.modules.events.service import EventService, PlaceService
from app.modules.sync.enums import SyncStatus
from app.modules.sync.repository import SyncRepository
from app.modules.sync.schemas import CreateSyncLog


class SyncService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repo = SyncRepository(session)
        self.full_sync = datetime.fromisoformat("2000-01-01")
        self.event_service = EventService(EventsRepository(session))
        self.place_service = PlaceService(PlacesRepository(session))

    async def do_sync(self):
        logger.info("Starting synchronization process")
        sync_log = await self.repo.get_last_sync()
        id = uuid.uuid4()
        last_sync_time = datetime.now(timezone.utc)

        if sync_log:
            sync_time = sync_log.last_changed_at
        else:
            sync_time = self.full_sync

        max_time = sync_time.today()
        await self.repo.create(
            CreateSyncLog(
                id=id,
                last_changed_at=max_time,
                last_sync_time=last_sync_time,
                sync_status=SyncStatus.PROCESSING,
            )
        )

        try:
            async for events in EventsPaginator(EventsProviderClient(), sync_time):
                for event in events["results"]:
                    event["place_id"] = event["place"]["id"]
                    await self.place_service.create_place(
                        CreatePlace(**(event["place"]))
                    )
                    await self.event_service.create_event(CreateEvent(**event))
                    changed_at = datetime.fromisoformat(event["changed_at"]).today()
                    if max_time < changed_at:
                        max_time = changed_at
        except Exception as e:
            logger.exception(e)
            await self.repo.update(
                CreateSyncLog(
                    id=id,
                    last_changed_at=max_time,
                    last_sync_time=last_sync_time,
                    sync_status=SyncStatus.FAILED,
                )
            )
            logger.warning("Synchronization failed")
            raise

        await self.repo.update(
            CreateSyncLog(
                id=id,
                last_changed_at=max_time,
                last_sync_time=last_sync_time,
                sync_status=SyncStatus.SUCCESS,
            )
        )
        logger.info("Synchronization completed successfully")
