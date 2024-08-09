from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class Action(Base):
    __tablename__ = "actions"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    queue_id = Column(UUID(as_uuid=True), ForeignKey("queues.id"))
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(Integer)
    deadline = Column(DateTime)
    result = Column(String)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Action(id={self.id}, type={self.type})>"


Action.profile = relationship("Profile", back_populates="actions")
Action.queue = relationship("Queue", back_populates="actions")
