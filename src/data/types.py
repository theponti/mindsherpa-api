from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    id: UUID = Field(..., alias="id")
    email: str
    name: Optional[str] = None
    created_at: datetime


class RefreshToken(BaseModel):
    id: UUID = Field(..., alias="id")
    user_id: UUID
    token: str
    revoked: Optional[datetime] = None
    created_at: datetime


class Profile(BaseModel):
    id: UUID = Field(..., alias="id")
    full_name: Optional[str] = None
    provider: str
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    queues: List["Queue"] = []
    actions: List["Action"] = []
    memories: List["Memory"] = []
    entities: List["Entity"] = []
    tags: List["Tag"] = []
    contexts: List["Context"] = []
    system_state: Optional["SystemState"] = None
    chats: List["Chat"] = []
    notes: List["Note"] = []


class Queue(BaseModel):
    id: UUID = Field(..., alias="id")
    name: str
    profile_id: UUID
    created_at: datetime
    profile: "Profile"
    actions: List["Action"] = []


class Action(BaseModel):
    id: UUID = Field(..., alias="id")
    queue_id: Optional[UUID] = None
    type: str
    content: str
    status: str
    priority: Optional[int] = None
    deadline: Optional[datetime] = None
    result: Optional[str] = None
    profile_id: UUID
    created_at: datetime
    queue: Optional["Queue"] = None
    profile: "Profile"


class Memory(BaseModel):
    id: UUID = Field(..., alias="id")
    content: str
    importance: Optional[float] = None
    profile_id: UUID
    last_accessed: Optional[datetime] = None
    created_at: datetime
    profile: "Profile"
    entities: List["EntityMemory"] = []
    tags: List["Tag"] = []


class Entity(BaseModel):
    id: UUID = Field(..., alias="id")
    name: str
    type: str
    attributes: Optional[str] = None
    profile_id: UUID
    created_at: datetime
    profile: "Profile"
    memories: List["EntityMemory"] = []


class EntityMemory(BaseModel):
    id: UUID = Field(..., alias="id")
    entity_id: UUID
    memory_id: UUID
    entity: "Entity"
    memory: "Memory"


class Tag(BaseModel):
    id: UUID = Field(..., alias="id")
    name: str
    profile_id: UUID
    created_at: datetime
    profile: "Profile"
    memories: List["Memory"] = []
    notes: List["Note"] = []


class Relationship(BaseModel):
    id: UUID = Field(..., alias="id")
    entity1_id: UUID
    entity2_id: UUID
    relationship_type: str
    strength: Optional[float] = None


class Context(BaseModel):
    id: UUID = Field(..., alias="id")
    name: str
    content: str
    profile_id: UUID
    created_at: datetime
    updated_at: datetime
    profile: "Profile"


class SystemState(BaseModel):
    id: UUID = Field(..., alias="id")
    current_focus: Optional[str] = None
    mood: Optional[str] = None
    parameters: Optional[str] = None
    profile_id: UUID
    updated_at: datetime
    profile: "Profile"


class Chat(BaseModel):
    id: UUID = Field(..., alias="id")
    title: str
    profile_id: UUID
    created_at: datetime
    profile: "Profile"
    messages: List["Message"] = []


class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(..., alias="id")
    message: str
    role: str
    chat_id: UUID
    profile_id: UUID
    created_at: datetime
    chat: "Chat"


class Note(BaseModel):
    id: UUID = Field(..., alias="id")
    content: str
    profile_id: UUID
    created_at: datetime
    updated_at: datetime
    profile: "Profile"
    tags: List["Tag"] = []


# Set up forward references
Profile.model_rebuild()
Queue.model_rebuild()
Action.model_rebuild()
Memory.model_rebuild()
Entity.model_rebuild()
EntityMemory.model_rebuild()
Tag.model_rebuild()
Context.model_rebuild()
SystemState.model_rebuild()
Chat.model_rebuild()
Message.model_rebuild()
Note.model_rebuild()
