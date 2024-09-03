from datetime import datetime, time
from enum import Enum
from typing import List, Optional

import strawberry
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.data.models.focus import Focus, FocusOutputItem, FocusState


@strawberry.enum
class Category(Enum):
    CAREER = "career"
    PERSONAL_DEVELOPMENT = "personal_development"
    HEALTH = "health"
    MENTAL_HEALTH = "mental_health"
    FINANCE = "finance"
    EDUCATION = "education"
    RELATIONSHIPS = "relationships"
    HOME = "home"
    SHOPPING = "shopping"
    INTERESTS = "interests"
    ADVENTURE = "adventure"
    TECHNOLOGY = "technology"
    SPIRITUALITY = "spirituality"
    SOCIAL = "social"
    PRODUCTIVITY = "productivity"
    CREATIVITY = "creativity"
    CULTURE = "culture"
    LEGAL = "legal"
    EVENTS = "events"
    PROJECTS = "projects"


@strawberry.enum
class Priority(Enum):
    HIGH = 1  # Critical and time-sensitive tasks
    MEDIUM = 2  # Important tasks
    NORMAL = 3  # Medium-priority tasks
    LOW = 4  # Low-priority tasks
    OPTIONAL = 5  # Optional tasks


@strawberry.enum
class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@strawberry.enum
class FocusItemType(Enum):
    EVENT = "event"
    TASK = "task"
    GOAL = "goal"
    REMINDER = "reminder"
    NOTE = "note"
    FEELING = "FEELING"
    REQUEST = "REQUEST"


@strawberry.enum
class FocusItemTaskSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EPIC = "epic"


@strawberry.input
class DeleteFocusItemInput:
    id: int


@strawberry.type
class DeleteFocusItemOutput:
    success: bool


async def delete_focus_item(info: strawberry.Info, input: DeleteFocusItemInput) -> DeleteFocusItemOutput:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")
    note = session.query(Focus).filter(Focus.id == input.id).first()
    if not note:
        return DeleteFocusItemOutput(success=False)

    session.delete(note)
    session.commit()
    return DeleteFocusItemOutput(success=True)
