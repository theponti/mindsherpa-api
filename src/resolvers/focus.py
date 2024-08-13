from enum import Enum
from typing import List, Optional
from sqlalchemy.orm import Session
import strawberry

from src.data.data_access import get_user_context
from src.data.models.focus import Focus
from src.services.sherpa import generate_user_context
from src.utils.logger import logger


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
    id: int
    text: str
    type: str
    task_size: str
    category: str
    priority: str
    sentiment: str
    due_date: Optional[str]


@strawberry.type
class FocusOutput:
    items: List[FocusOutputItem]


def convert_to_sherpa_items(items: List[Focus]) -> List[FocusOutputItem]:
    return [
        FocusOutputItem(
            id=data.id,
            type=data.type,
            task_size=data.task_size,
            text=data.text,
            category=data.category,
            priority=data.priority,
            sentiment=data.sentiment,
            due_date=data.due_date,
        )
        for data in items
    ]

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
    category: Optional[Category] = None

async def get_focus_items(info: strawberry.Info, filter: Optional[GetFocusFilter] = None) -> FocusOutput:
        """
        Returns notes structure content as well as total tokens and total time for generation.
        """
        current_user = info.context.get("user")
        if not current_user:
            raise Exception("Unauthorized")

        session: Session = info.context.get("session")
        profile_id = info.context.get("profile").id
        
        if filter and filter.category:
            stored_focus = session.query(Focus).filter_by(profile_id=profile_id, category=filter.category.value).all()
        else:
            stored_focus = session.query(Focus).filter_by(profile_id=profile_id).all()
        if stored_focus:
            return FocusOutput(items=convert_to_sherpa_items(stored_focus))

        try:
            transcript_base = """
            ### User Context:
            {user_context}

            ### Chat History:
            {chat_history}
            """
            profile_id = info.context.get("profile").id
            history = get_user_context(info.context.get("session"), profile_id)
            analysis = generate_user_context(
                profile_id=profile_id,
                session=info.context.get("session"),
                transcript=transcript_base.format(
                    user_context=history.note_history, chat_history=history.chat_history
                ),
            )

            if not analysis:
                return FocusOutput(items=[])

            return FocusOutput(items=convert_to_sherpa_items(analysis))
        except Exception as e:
            logger.error(f" ********* ERROR IN USER PROMPT ********: {e} ***** ")
            raise Exception("Error retrieving user focus")
