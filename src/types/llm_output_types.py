from enum import Enum
from typing import List, Optional, Union

from langchain.pydantic_v1 import BaseModel, Field


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


class LLMFocusItem(BaseModel):
    type: ItemType = Field(description="Event, task, goal, reminder, note, feeling, request, question")
    task_size: TaskSize = Field(description="Small, medium, large, epic")
    text: str = Field(description="The description of the item")
    category: Category = Field(
        description="Shopping, grocery shopping, fashion, beauty, and personal style. Also includes items related to buying and selling.",
    )
    priority: int = Field(ge=1, le=5, description="Important, medium, low, optional")
    sentiment: Sentiment = Field(description="Positive, neutral, negative")
    due_date: Optional[str] = Field(None, description="The optional due date for the task")


class LLMFocusOutput(BaseModel):
    items: List[LLMFocusItem]
