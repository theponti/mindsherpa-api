from datetime import datetime
from sqlalchemy import (
    UUID,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Table,
    func,
)
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
Profile.queues = relationship("Queue", back_populates="profile")


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


Action.queue = relationship("Queue", back_populates="actions")
Queue.actions = relationship("Action", back_populates="queue")
Action.profile = relationship("Profile", back_populates="actions")
Profile.actions = relationship("Action", back_populates="profile")


class Memory(Base):
    __tablename__ = "memories"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    content = Column(String, nullable=False)
    importance = Column(Float)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Memory(id={self.id}, content={self.content})>"


Memory.profile = relationship("Profile", back_populates="memories")
Memory.entities = relationship("EntityMemory", back_populates="memory")
Profile.memories = relationship("Memory", back_populates="profile")


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
Profile.entities = relationship("Entity", back_populates="profile")
Entity.memories = relationship("EntityMemory", back_populates="entity")


class EntityMemory(Base):
    __tablename__ = "entity_memories"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id"))

    def __repr__(self):
        return f"<EntityMemory(id={self.id}, entity_id={self.entity_id}, memory_id={self.memory_id})>"


EntityMemory.entity = relationship("Entity", back_populates="memories")
EntityMemory.memory = relationship("Memory", back_populates="entities")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    name = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


Tag.profile = relationship("Profile", back_populates="tags")
Profile.tags = relationship("Tag", back_populates="profile")


class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    entity1_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    entity2_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    relationship_type = Column(String, nullable=False)
    strength = Column(Float)

    def __repr__(self):
        return f"<Relationship(id={self.id}, entity1_id={self.entity1_id}, entity2_id={self.entity2_id})>"


class Context(Base):
    __tablename__ = "context"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Context(id={self.id}, name={self.name})>"


Context.profile = relationship("Profile", back_populates="contexts")
Profile.contexts = relationship("Context", back_populates="profile")


class SystemState(Base):
    __tablename__ = "system_state"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    current_focus = Column(String)
    mood = Column(String)
    parameters = Column(String)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SystemState(id={self.id}, current_focus={self.current_focus})>"


SystemState.profile = relationship("Profile", back_populates="system_state")
Profile.system_state = relationship("SystemState", back_populates="profile")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    title = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Chat(id={self.id}, title={self.title})>"


Chat.profile = relationship("Profile", back_populates="chats")
Profile.chats = relationship("Chat", back_populates="profile")


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
Message.chat = relationship("Chat", back_populates="messages")


class Note(Base):
    __tablename__ = "notes"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    content = Column(String, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Note(id={self.id}, content={self.content})>"


Note.profile = relationship("Profile", back_populates="notes")
Profile.notes = relationship("Note", back_populates="profile")

# Association table for many-to-many relationship between Memory and Tag
memory_tags = Table(
    "memory_tags",
    Base.metadata,
    Column("memory_id", UUID(as_uuid=True), ForeignKey("memories.id")),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id")),
)


# Add relationships
Memory.tags = relationship("Tag", secondary=memory_tags, back_populates="memories")
Tag.memories = relationship("Memory", secondary=memory_tags, back_populates="tags")


# Note and Tag many-to-many relationship
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", UUID(as_uuid=True), ForeignKey("notes.id")),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id")),
)

Note.tags = relationship("Tag", secondary=note_tags, back_populates="notes")
Tag.notes = relationship("Note", secondary=note_tags, back_populates="tags")
