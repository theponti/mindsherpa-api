from dataclasses import dataclass
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from src.data.chat import get_full_chat_history
from src.data.notes import get_user_notes


@dataclass(frozen=True)
class UserContext:
    chat_history: List[str]
    note_history: List[str]


def get_user_context(session: Session, profile_id: UUID) -> UserContext:
    chat_history = get_full_chat_history(session, profile_id=profile_id)
    user_context = get_user_notes(session, profile_id)
    chat_history_contents = [str(message.message) for message in chat_history]
    user_context_contents = [str(note.content) for note in user_context]
    return UserContext(chat_history_contents, user_context_contents)
