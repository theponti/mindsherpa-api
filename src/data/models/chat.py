import enum
import datetime
from sqlalchemy import DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import strawberry
import uuid

from src.data.db import Base
from src.utils.logger import logger

@strawberry.type
class ChatOutput:
    id: str
    title: str
    created_at: str

class ChatState(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ENDED = "ended"

class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("profiles.id"))
    state: Mapped[ChatState] = mapped_column(nullable=False, default="active")

    # Metadata
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.UTC))

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "profile_id": self.profile_id,
            "state": self.state,
            "created_at": self.created_at,
        }
    
    def to_gql(self) -> ChatOutput:
        try:
            return ChatOutput(
                **{field: getattr(self, field) for field in ["id", "title", "created_at"]}
            )
        except AttributeError as e:
            logger.error(f"Error converting ChatModel to Chat: {e}")
            raise ValueError("Invalid ChatModel data")

    def __repr__(self):
        return f"<Chat(id={self.id}, title={self.title})>"


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    message: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, nullable=False)
    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chats.id"))
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.UTC))

    def __repr__(self):
        return f"<Message(id={self.id}, message={self.message})>"


Chat.messages = relationship("Message", back_populates="chat")
Chat.profile = relationship("Profile", back_populates="chats")
Message.chat = relationship("Chat", back_populates="messages")
