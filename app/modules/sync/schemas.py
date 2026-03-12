from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateSyncLog(BaseModel):
    id: UUID
    sync_at: datetime
