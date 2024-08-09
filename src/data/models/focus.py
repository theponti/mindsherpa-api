from datetime import UTC, datetime
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Date
from src.data.db import Base


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
    text = Column(String(255), nullable=False)
    type = Column(String, nullable=False, default="task")

    # Relationships
    profile_id = Column(UUID, ForeignKey("profiles.id"), nullable=False)

    # Metadata
    created_at = Column(Date, nullable=False, default=datetime.now(UTC))
    updated_at = Column(Date, nullable=False, default=datetime.now(UTC))
