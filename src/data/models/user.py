from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    # apple_id = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )
    token = Column(String, unique=True, nullable=False)
    revoked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    full_name = Column(String, nullable=True)
    provider = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Profile(id={self.id}, full_name={self.full_name})>"


Profile.actions = relationship("Action", back_populates="profile")
Profile.chats = relationship("Chat", back_populates="profile")
Profile.entities = relationship("Entity", back_populates="profile")
Profile.queues = relationship("Queue", back_populates="profile")
Profile.memories = relationship("Memory", back_populates="profile")
Profile.notes = relationship("Note", back_populates="profile")
Profile.tags = relationship("Tag", back_populates="profile")

# State
Profile.contexts = relationship("Context", back_populates="profile")
Profile.system_state = relationship("SystemState", back_populates="profile")
