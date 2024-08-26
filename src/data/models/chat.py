import datetime
import enum
import uuid

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.db import Base
from src.utils.logger import logger


class ChatState(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ENDED = "ENDED"


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("profiles.id"))
    state: Mapped[ChatState] = mapped_column(
        String, nullable=False, default=ChatState.ACTIVE.value
    )

    # Metadata
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.UTC)
    )

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "profile_id": self.profile_id,
            "state": self.state,
            "created_at": self.created_at,
        }

    def __repr__(self):
        return f"<Chat(id={self.id}, title={self.title})>"


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    message: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, nullable=False)
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chats.id")
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.UTC)
    )

    def __repr__(self):
        return f"<Message(id={self.id}, message={self.message})>"


Chat.messages = relationship("Message", back_populates="chat")
Chat.profile = relationship("Profile", back_populates="chats")
Message.chat = relationship("Chat", back_populates="messages")
