from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, UUID, func
from sqlalchemy.orm import relationship

from src.data.db import Base


class ChatState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Chat(Base):
    __tablename__ = "chats"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    title = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    state = Column(ChatState, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

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
