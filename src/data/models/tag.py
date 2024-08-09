from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class Tag(Base):
    __tablename__ = "tags"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    name = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


Tag.profile = relationship("Profile", back_populates="tags")
Tag.memories = relationship("Memory", secondary="memory_tags", back_populates="tags")
Tag.notes = relationship("Note", secondary="note_tags", back_populates="tags")
