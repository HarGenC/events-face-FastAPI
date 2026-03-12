import uuid
from datetime import datetime

from app.modules.clients.events_face import EventsProviderClient
from app.modules.clients.events_paginator import EventsPaginator
from app.modules.events.schemas import CreateEvent, CreatePlace
from app.modules.events.service import EventService, PlaceService
from app.modules.sync.repository import SyncRepository
from app.modules.sync.schemas import CreateSyncLog


class SyncService:
    def __init__(
        self,
        repo: SyncRepository,
        event_service: EventService,
        place_service: PlaceService,
        external_client: EventsProviderClient,
    ):
        self.repo = repo
        self.full_sync = datetime.fromisoformat("2000-01-01")
        self.event_service = event_service
        self.place_service = place_service
        self.external_client = external_client

    async def do_sync(self):
        sync_log = await self.repo.get_last_sync()

        if sync_log:
            sync_time = sync_log.sync_at
        else:
            sync_time = self.full_sync

        max_time = sync_time.today()

        async for events in EventsPaginator(EventsProviderClient(), sync_time):
            for event in events["results"]:
                event["place_id"] = event["place"]["id"]
                await self.place_service.create_place(CreatePlace(**(event["place"])))
                await self.event_service.create_event(CreateEvent(**event))
                changed_at = datetime.fromisoformat(event["changed_at"]).today()
                if max_time < changed_at:
                    max_time = changed_at

        await self.repo.create(CreateSyncLog(id=uuid.uuid4(), sync_at=max_time))
