from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class Queue(Base):
    __tablename__ = "queues"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    name = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Queue(id={self.id}, name={self.name})>"


Queue.profile = relationship("Profile", back_populates="queues")
Queue.actions = relationship("Action", back_populates="queue")
