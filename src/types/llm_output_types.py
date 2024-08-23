from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field


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


class LLMFocusItem(BaseModel):
    type: ItemType
    task_size: TaskSize
    text: str
    category: Category
    priority: int = Field(ge=1, le=5)
    sentiment: Sentiment
    due_date: Optional[str]


class LLMFocusOutput(BaseModel):
    items: List[LLMFocusItem]
