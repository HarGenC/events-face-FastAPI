import uuid

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Registrations(Base):
    __tablename__ = "registrations"

    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id")
    )
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    seat: Mapped[str]

    __table_args__ = (
        PrimaryKeyConstraint("event_id", "ticket_id", name="pk_event_ticket"),
        UniqueConstraint("event_id", "seat", name="uix_event_seat"),
    )
