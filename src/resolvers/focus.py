from enum import Enum
from typing import List
import strawberry

from src.data.models.focus import Focus


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
class FocusOutputItem:
    text: str
    type: FocusItemType
    task_size: FocusItemTaskSize
    category: Category  # Use the Category enum
    priority: Priority  # Use the Priority enum
    sentiment: Sentiment  # Use the Sentiment enum
    due_date: str  # Should be in YYYY-MM-DD format


@strawberry.type
class FocusOutput:
    items: List[FocusOutputItem]


def convert_to_sherpa_item(data: Focus) -> FocusOutputItem:
    return FocusOutputItem(
        type=FocusItemType[str(data.type)],
        task_size=FocusItemTaskSize[str(data.task_size)],
        text=str(data.text),
        category=Category(data.category),
        priority=Priority(data.priority),
        sentiment=Sentiment(data.sentiment),
        due_date=str(data.due_date),
    )
