import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Union

import strawberry
from langchain.pydantic_v1 import BaseModel, Field
from sqlalchemy import UUID, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.types import DateTime

from src.data.db import Base


@strawberry.enum
class FocusState(Enum):
    backlog = "backlog"
    active = "active"
    completed = "completed"
    deleted = "deleted"


class ItemType(str, Enum):
    event = "event"
    task = "task"
    goal = "goal"
    reminder = "reminder"
    note = "note"
    feeling = "feeling"
    request = "request"
    question = "question"


class TaskSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"
    epic = "epic"


class Category(str, Enum):
    career = "career"
    personal_development = "personal_development"
    physical_health = "physical_health"
    mental_health = "mental_health"
    finance = "finance"
    education = "education"
    relationships = "relationships"
    home = "home"
    shopping = "shopping"
    interests = "interests"
    adventure = "adventure"
    technology = "technology"
    spirituality = "spirituality"
    productivity = "productivity"
    creativity = "creativity"
    culture = "culture"
    legal = "legal"
    events = "events"
    projects = "projects"


class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class DueDate(BaseModel):
    month: Union[str, int]
    day: Union[str, int]
    year: Union[str, int]
    time: Union[str, int]


class FocusItemBase(BaseModel):
    type: ItemType
    task_size: TaskSize
    text: str
    category: Category = Field(
        description="Shopping, grocery shopping, fashion, beauty, and personal style. Also includes items related to buying and selling.",
    )
    priority: int = Field(ge=1, le=5)
    sentiment: Sentiment
    due_date: Optional[str] = Field(
        None,
        description="The deadline for completing the item in YYYY-MM-DDTHH:MM format. Example: due_date: 2023-01-01T12:00",
    )


class FocusItem(FocusItemBase):
    id: int
    due_date: Optional[str]
    profile_id: uuid.UUID
    state: FocusState
    created_at: datetime
    updated_at: datetime


class Focus(Base):
    __tablename__ = "focus"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String, nullable=False, default="general")
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    sentiment: Mapped[str] = mapped_column(String, nullable=False, default="neutral")
    state: Mapped[FocusState] = mapped_column(String, nullable=False, default=FocusState.backlog.value)
    task_size: Mapped[str] = mapped_column(String, nullable=False, default="medium")
    text: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False, default="task")

    # Relationships
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("profiles.id"), nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(UTC))

    def to_json(self):
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "task_size": self.task_size,
            "category": self.category,
            "priority": self.priority,
            "profile_id": self.profile_id,
            "sentiment": self.sentiment,
            "state": self.state,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def get_focus_by_profile_id(session: Session, profile_id: uuid.UUID):
    return session.query(Focus).filter(Focus.profile_id == profile_id).all()


def get_focus_by_id(session: Session, focus_id: int) -> Focus:
    return session.query(Focus).filter(Focus.id == focus_id).first()


def create_focus(session: Session, text: str, profile_id: uuid.UUID) -> Focus:
    focus = Focus(text=text, profile_id=profile_id)
    session.add(focus)
    session.commit()
    session.flush()
    return focus


def complete_focus(session: Session, focus_id: int) -> Focus:
    focus = get_focus_by_id(session, focus_id)
    focus.state = FocusState.completed
    session.commit()
    session.flush()
    return focus
