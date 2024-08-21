from datetime import date, UTC, datetime
from enum import Enum
from typing import Optional
import uuid

from pydantic import BaseModel, Field
import pydantic
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import mapped_column, Mapped, Session
import strawberry

from src.data.db import Base

@strawberry.enum
class FocusState(Enum):
    backlog = "backlog"
    active = "active"
    completed = "completed"
    deleted = "deleted"

@strawberry.type
class FocusOutputItem:
    id: int
    category: str
    due_date: Optional[date]
    priority: int
    profile_id: uuid.UUID
    sentiment: str
    state: FocusState
    task_size: str
    text: str
    type: str
    created_at: datetime
    updated_at: datetime


class Focus(Base):
    __tablename__ = "focus"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String, nullable=False, default="general")
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    sentiment: Mapped[str] = mapped_column(String, nullable=False, default="neutral")
    state: Mapped[str] = mapped_column(String, nullable=False, default=FocusState.backlog.value)
    task_size: Mapped[str] = mapped_column(String, nullable=False, default="medium")
    text: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False, default="task")

    # Relationships
    profile_id = Column(UUID, ForeignKey("profiles.id"), nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(Date, nullable=False, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(Date, nullable=False, default=datetime.now(UTC))

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

    def to_output_item(self) -> FocusOutputItem:
        json = self.to_json()
        return FocusOutputItem(**{
            key: json[key]
            for key in json
        })


def get_focus_by_profile_id(session: Session, profile_id):
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
    focus.state = FocusState.completed.value
    session.commit()
    session.flush()
    return focus
