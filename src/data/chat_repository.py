from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from src.data.models.chat import Message


def get_user_chat_messages(session: Session, profile_id: UUID) -> List[Message]:
    messages = (
        session.query(Message)
        .filter(Message.profile_id == profile_id)
        .order_by(Message.created_at.desc())
        .all()
    )

    return messages


def get_chat_history(session: Session, chat_id: UUID) -> List[Message]:
    messages = session.query(Message).filter(Message.chat_id == chat_id).all()
    return messages


def insert_message(session: Session, chat_id: UUID, message: str, profile_id: UUID, role: str) -> Message:
    new_message = Message(message=message, chat_id=chat_id, profile_id=profile_id, role=role)
    session.add(new_message)
    session.commit()

    return new_message
