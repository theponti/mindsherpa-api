from datetime import date, UTC, datetime
from enum import Enum
from typing import Optional
import uuid

from pydantic import BaseModel, Field
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import mapped_column, Mapped, Session
import strawberry

from src.data.db import Base

class FocusState(Enum):
    backlog = "backlog"
    active = "active"
    completed = "completed"
    deleted = "deleted"

@strawberry.type
class FocusOutputItem:
    id: int
    text: str
    type: str
    task_size: str
    category: str
    priority: int
    sentiment: str
    due_date: Optional[date]

class Focus(Base):
    __tablename__ = "focus"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String, nullable=False, default="general")
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    sentiment: Mapped[str] = mapped_column(String, nullable=False, default="neutral")
    state: Mapped[FocusState] = mapped_column(String, nullable=False, default="backlog")
    task_size: Mapped[str] = mapped_column(String, nullable=False, default="medium")
    text: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False, default="task")

    # Relationships
    profile_id = Column(UUID, ForeignKey("profiles.id"), nullable=False)

    # Metadata
    created_at = Column(Date, nullable=False, default=datetime.now(UTC))
    updated_at = Column(Date, nullable=False, default=datetime.now(UTC))

    def to_json(self):
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "task_size": self.task_size,
            "category": self.category,
            "priority": self.priority,
            "sentiment": self.sentiment,
            "due_date": self.due_date,
        }

    def to_output_item(self) -> FocusOutputItem:
        return FocusOutputItem(
            id=self.id,
            type=self.type,
            task_size=self.task_size,
            text=self.text,
            category=self.category,
            priority=self.priority,
            sentiment=self.sentiment,
            due_date=self.due_date,
        )

class FocusType(BaseModel):
    id: int
    category: str = Field(default="general")
    due_date: Optional[date]
    priority: int = Field(default=4)
    sentiment: str = Field(default="neutral")
    state: str = Field(default="backlog")
    status: str = Field(default="active")
    task_size: str = Field(default="medium")
    text: str
    type: str = Field(default="task")
    profile_id: uuid.UUID
    created_at: date = Field(default_factory=datetime.now(UTC).date)
    updated_at: date = Field(default_factory=datetime.now(UTC).date)


def get_focus_by_profile_id(session: Session, profile_id):
    return session.query(Focus).filter(Focus.profile_id == profile_id).all()
