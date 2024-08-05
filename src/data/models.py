import enum
from re import S
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from src.data.db import Base


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True)
    full_name = Column(String, nullable=True)
    provider = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Queue(Base):
    __tablename__ = "queues"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)


Queue.profile = relationship("Profile", back_populates="queues")
Profile.queues = relationship("Queue", back_populates="profile")


class Action(Base):
    __tablename__ = "actions"
    id = Column(String, primary_key=True)
    queue_id = Column(String, ForeignKey("queues.id"))
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(Integer)
    deadline = Column(DateTime)
    result = Column(String)
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)


Action.queue = relationship("Queue", back_populates="actions")
Queue.actions = relationship("Action", back_populates="queue")
Action.profile = relationship("Profile", back_populates="actions")
Profile.actions = relationship("Action", back_populates="profile")


class Memory(Base):
    __tablename__ = "memories"
    id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    importance = Column(Float)
    profile_id = Column(String, ForeignKey("profiles.id"))
    last_accessed = Column(DateTime)
    created_at = Column(DateTime)


Memory.profile = relationship("Profile", back_populates="memories")
Profile.memories = relationship("Memory", back_populates="profile")


class Entity(Base):
    __tablename__ = "entities"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    attributes = Column(String)
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)


Entity.profile = relationship("Profile", back_populates="entities")
Profile.entities = relationship("Entity", back_populates="profile")


class EntityMemory(Base):
    __tablename__ = "entity_memories"
    id = Column(String, primary_key=True)
    entity_id = Column(String, ForeignKey("entities.id"))
    memory_id = Column(String, ForeignKey("memories.id"))


EntityMemory.entity = relationship("Entity", back_populates="memories")
EntityMemory.memory = relationship("Memory", back_populates="entities")
Entity.memories = relationship("Memory", secondary="entity_memories")
Memory.entities = relationship("Entity", secondary="entity_memories")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)


Tag.profile = relationship("Profile", back_populates="tags")
Profile.tags = relationship("Tag", back_populates="profile")


class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(String, primary_key=True)
    entity1_id = Column(String, ForeignKey("entities.id"))
    entity2_id = Column(String, ForeignKey("entities.id"))
    relationship_type = Column(String, nullable=False)
    strength = Column(Float)


class Context(Base):
    __tablename__ = "context"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


Context.profile = relationship("Profile", back_populates="contexts")
Profile.contexts = relationship("Context", back_populates="profile")


class SystemState(Base):
    __tablename__ = "system_state"
    id = Column(String, primary_key=True)
    current_focus = Column(String)
    mood = Column(String)
    parameters = Column(String)
    profile_id = Column(String, ForeignKey("profiles.id"))
    updated_at = Column(DateTime)


SystemState.profile = relationship("Profile", back_populates="system_state")
Profile.system_state = relationship("SystemState", back_populates="profile")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)


Chat.profile = relationship("Profile", back_populates="chats")
Profile.chats = relationship("Chat", back_populates="profile")


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    message = Column(String)
    role = Column(String, nullable=False)
    chat_id = Column(String, ForeignKey("chats.id"))
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)


Chat.messages = relationship("Message", back_populates="chat")
Message.chat = relationship("Chat", back_populates="messages")


class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


Note.profile = relationship("Profile", back_populates="notes")
Profile.notes = relationship("Note", back_populates="profile")

# Association table for many-to-many relationship between Memory and Tag
memory_tags = Table(
    "memory_tags",
    Base.metadata,
    Column("memory_id", String, ForeignKey("memories.id")),
    Column("tag_id", String, ForeignKey("tags.id")),
)

# Add relationships
Memory.tags = relationship("Tag", secondary=memory_tags, back_populates="memories")
Tag.memories = relationship("Memory", secondary=memory_tags, back_populates="tags")
Entity.memories = relationship("Memory", secondary="entity_memories")
Memory.entities = relationship("Entity", secondary="entity_memories")

# Note and Tag many-to-many relationship
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", String, ForeignKey("notes.id")),
    Column("tag_id", String, ForeignKey("tags.id")),
)

Note.tags = relationship("Tag", secondary=note_tags, back_populates="notes")
Tag.notes = relationship("Note", secondary=note_tags, back_populates="tags")
