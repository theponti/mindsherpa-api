from datetime import date, UTC, datetime
from pydantic import BaseModel, Field
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import MappedColumn, mapped_column
import strawberry
from typing import Optional
import uuid

from src.data.db import Base

@strawberry.type
class FocusOutputItem:
    id: int
    text: str
    type: str
    task_size: str
    category: str
    priority: str
    sentiment: str
    due_date: Optional[str]
    
class Focus(Base):
    __tablename__ = "focus"
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False, default="general")
    due_date = Column(Date, nullable=True)
    priority = Column(Integer, nullable=False, default=4)
    sentiment = Column(String, nullable=False, default="neutral")
    state = Column(String, nullable=False, default="backlog")
    status = Column(String, nullable=False, default="active")
    task_size = Column(String, nullable=False, default="medium")
    text: MappedColumn[str] = mapped_column(nullable=False)
    type: MappedColumn[str] = mapped_column(nullable=False, default="task")

    # Relationships
    profile_id = Column(UUID, ForeignKey("profiles.id"), nullable=False)

    # Metadata
    created_at = Column(Date, nullable=False, default=datetime.now(UTC))
    updated_at = Column(Date, nullable=False, default=datetime.now(UTC))

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

