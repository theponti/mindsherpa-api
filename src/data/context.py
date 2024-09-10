from dataclasses import dataclass
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from src.data.chat import get_user_chat_messages
from src.data.models.focus import get_focus_by_profile_id


@dataclass(frozen=True)
class UserContext:
    chat_history: List[str]
    focus_items: List[str]


def get_user_context(session: Session, profile_id: UUID) -> UserContext:
    chat_history = get_user_chat_messages(session, profile_id=profile_id)
    focus_items = get_focus_by_profile_id(profile_id=profile_id, session=session)
    chat_history_contents = [str(message.message) for message in chat_history]

    return UserContext(
        chat_history=chat_history_contents,
        focus_items=[f"{str(item.text)} - State: {str(item.state)}" for item in focus_items],
    )
