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


@strawberry.type
class FocusOutput:
    items: List[FocusOutputItem]


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


@strawberry.input
class GetFocusFilter:
    category: str


def get_end_of_today():
    today = datetime.now().date()
    end_of_today = datetime.combine(today, time(23, 59, 59))
    return end_of_today


async def get_focus_items(info: strawberry.Info, filter: Optional[GetFocusFilter] = None) -> FocusOutput:
    """
    Returns notes structure content as well as total tokens and total time for generation.
    """
    current_user = info.context.get("user")
    if not current_user:
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")
    profile_id = info.context.get("profile").id

    query = session.query(Focus).filter(
        Focus.profile_id == profile_id, Focus.state.notin_([FocusState.completed.value])
    )

    # Apply category filter if provided
    if filter and filter.category:
        query = query.filter(Focus.category == filter.category)

    # Apply due date filter
    query = query.filter(or_(Focus.due_date <= get_end_of_today(), Focus.due_date == None))

    # Apply ordering
    query = query.order_by(Focus.due_date.desc())

    # Execute query
    focus_items = query.all()

    return FocusOutput(items=[item.to_output_item() for item in focus_items])
