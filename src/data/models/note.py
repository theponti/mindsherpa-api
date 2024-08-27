import uuid
from datetime import UTC, datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.db import Base


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    profile_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id")
    )
    profile = relationship("Profile", back_populates="notes")
    tags = relationship("Tag", secondary="note_tags", back_populates="notes")
    created_at = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at = mapped_column(DateTime, default=datetime.now(UTC))

    def __repr__(self):
        return f"<Note(id={self.id}, content={self.content})>"
