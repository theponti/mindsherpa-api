from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class Memory(Base):
    __tablename__ = "memories"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    content = Column(String, nullable=False)
    importance = Column(Float)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Memory(id={self.id}, content={self.content})>"


Memory.profile = relationship("Profile", back_populates="memories")
Memory.entities = relationship("EntityMemory", back_populates="memory")
Memory.tags = relationship("Tag", secondary="memory_tags", back_populates="memories")
