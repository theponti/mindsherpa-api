from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.data.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=func.uuid_generate_v4()
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    profile = relationship("Profile", back_populates="user")
    # refresh_tokens = relationship("RefreshToken", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"

# User.

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
    created_at = Column(DateTime, default=datetime.now(UTC))

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
    user = relationship("User", back_populates="profile")

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

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
