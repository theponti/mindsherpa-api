# Pydantic model for syncing with the SQLAlchemy UserInputItem model
from pydantic import BaseModel
from datetime import date
from enum import Enum

class ItemType(str, Enum):
    event = 'event'
    task = 'task'
    goal = 'goal'
    reminder = 'reminder'
    note = 'note'
    feeling = 'feeling'
    request = 'request'

class ItemState(str, Enum):
    backlog = 'backlog'
    not_completed = 'not_completed'
    completed = 'completed'

class TaskSize(str, Enum):
    small = 'small'
    medium = 'medium'
    large = 'large'
    epic = 'epic'

class Category(str, Enum):
    career = 'career'
    personal_development = 'personal_development'
    health = 'health'
    mental_health = 'mental_health'
    finance = 'finance'
    education = 'education'
    relationships = 'relationships'
    home = 'home'
    interests = 'interests'
    adventure = 'adventure'
    technology = 'technology'
    spirituality = 'spirituality'
    social = 'social'
    productivity = 'productivity'
    creativity = 'creativity'
    culture = 'culture'
    legal = 'legal'
    events = 'events'
    projects = 'projects'

class Sentiment(str, Enum):
    positive = 'positive'
    neutral = 'neutral'
    negative = 'negative'

class UserInputItemSchema(BaseModel):
    id: int
    type: ItemType
    state: ItemState
    task_size: TaskSize
    text: str
    category: Category
    priority: int
    sentiment: Sentiment
    due_date: date

    class Config:
        orm_mode = True  # Allows compatibility with SQLAlchemy models