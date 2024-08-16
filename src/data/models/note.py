from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid


from src.data.db import Base


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    profile_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    profile = relationship("Profile", back_populates="notes")
    tags = relationship("Tag", secondary="note_tags", back_populates="notes")
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Note(id={self.id}, content={self.content})>"


