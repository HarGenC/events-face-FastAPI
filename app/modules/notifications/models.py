import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.modules.notifications.enums import NotificationStatus


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    event_type: Mapped[str]
    payload: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), default=dict)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )
    retry_count: Mapped[int] = mapped_column(default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index(
            "idx_outbox_pending",
            "created_at",
            postgresql_where=("status == 'PENDING'"),
        ),
    )
