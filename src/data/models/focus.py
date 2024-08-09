from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date
from src.data.db import Base


class Focus(Base):
    __tablename__ = "focus"
    id = Column(Integer, primary_key=True)
    type = Column(
        Enum("event", "task", "goal", "reminder", "note", "feeling", "request"),
        nullable=False,
    )
    state = Column(Enum("backlog", "not_completed", "completed"), nullable=False)
    task_size = Column(Enum("small", "medium", "large", "epic"), nullable=False)
    text = Column(String(255), nullable=False)
    category = Column(
        Enum(
            "career",
            "personal_development",
            "health",
            "mental_health",
            "finance",
            "education",
            "relationships",
            "home",
            "interests",
            "adventure",
            "technology",
            "spirituality",
            "social",
            "productivity",
            "creativity",
            "culture",
            "legal",
            "events",
            "projects",
        ),
        nullable=False,
    )
    priority = Column(Integer, nullable=False)
    sentiment = Column(Enum("positive", "neutral", "negative"), nullable=False)
    due_date = Column(Date, nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)
