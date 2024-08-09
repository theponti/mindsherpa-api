from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class Context(Base):
    __tablename__ = "context"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC))

    def __repr__(self):
        return f"<Context(id={self.id}, name={self.name})>"


class SystemState(Base):
    __tablename__ = "system_state"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    current_focus = Column(String)
    mood = Column(String)
    parameters = Column(String)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    updated_at = Column(DateTime, default=datetime.now(UTC))

    def __repr__(self):
        return f"<SystemState(id={self.id}, current_focus={self.current_focus})>"


Context.profile = relationship("Profile", back_populates="contexts")
SystemState.profile = relationship("Profile", back_populates="system_state")
