import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import strawberry

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
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    title = Column(String, nullable=False)
    profile_id: Mapped[UUID] = mapped_column(ForeignKey("profiles.id"))
    state: Mapped[ChatState] = mapped_column(nullable=False, default="active")

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

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
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    message = Column(String)
    role = Column(String, nullable=False)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"))
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message(id={self.id}, message={self.message})>"


Chat.messages = relationship("Message", back_populates="chat")
Chat.profile = relationship("Profile", back_populates="chats")
Message.chat = relationship("Chat", back_populates="messages")
