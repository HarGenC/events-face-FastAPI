from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.sync.enums import SyncStatus


class CreateSyncLog(BaseModel):
    id: UUID
    last_sync_time: datetime
    last_changed_at: datetime
    sync_status: SyncStatus
