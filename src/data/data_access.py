from dataclasses import dataclass
from sqlalchemy.orm import Session
from typing import List

from src.data.models import Message
from src.data.notes import get_user_notes


def get_full_chat_history(session: Session, profile_id: str) -> List[Message]:
    messages = session.query(Message).filter(Message.profile_id == profile_id).all()
    return messages


def get_chat_history(session: Session, chat_id: str) -> List[Message]:
    messages = session.query(Message).filter(Message.chat_id == chat_id).all()
    return messages


def insert_message(
    session: Session, chat_id: str, message: str, profile_id: str, role: str
) -> Message:
    new_message = Message(
        message=message, chat_id=chat_id, profile_id=profile_id, role=role
    )
    session.add(new_message)
    session.commit()

    return new_message


@dataclass(frozen=True)
class UserContext:
    chat_history: List[str]
    note_history: List[str]


def get_user_context(session: Session, profile_id: str) -> UserContext:
    chat_history = get_full_chat_history(session, profile_id=profile_id)
    user_context = get_user_notes(session, profile_id)
    chat_history_contents = [str(message.message) for message in chat_history]
    user_context_contents = [str(note.content) for note in user_context]
    return UserContext(chat_history_contents, user_context_contents)
