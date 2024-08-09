from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class Entity(Base):
    __tablename__ = "entities"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    attributes = Column(String)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Entity(id={self.id}, name={self.name})>"


Entity.profile = relationship("Profile", back_populates="entities")
Entity.memories = relationship("EntityMemory", back_populates="entity")
