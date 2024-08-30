import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic.main import BaseModel

from src.data.models.chat import Chat, ChatState, Message
from src.resolvers.chat_resolvers import MessageOutput, message_to_gql
from src.utils.context import CurrentProfile, CurrentUser, SessionDep

chat_router = APIRouter()


class ChatOutput(BaseModel):
    id: UUID
    title: str
    created_at: datetime


@chat_router.get("/active")
async def get_active_chat(
    db: SessionDep,
    profile: CurrentProfile,
) -> ChatOutput | None:
    try:
        chat = (
            db.query(Chat)
            .filter(Chat.profile_id == profile.id)
            .filter(Chat.state == ChatState.ACTIVE.value)
            .order_by(Chat.created_at.desc())
            .first()
        )

        if chat is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        return ChatOutput(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
        )
    except (Exception, HTTPException) as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            logging.error(f"Error in get_active_chat: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")


class EndChatPayload(BaseModel):
    chat_id: UUID


@chat_router.post("/end")
async def end_chat(db: SessionDep, user: CurrentUser, input: EndChatPayload) -> ChatOutput | None:
    if not user:
        raise Exception("Unauthorized")

    chat = db.query(Chat).filter(Chat.id == input.chat_id).first()

    if chat is None:
        raise ValueError("Chat not found")

    chat.state = ChatState.ENDED.value
    db.add(chat)

    new_chat = Chat(
        title="New Chat",
        profile_id=chat.profile_id,
    )
    db.add(new_chat)
    db.commit()

    return ChatOutput(
        id=new_chat.id,
        title=new_chat.title,
        created_at=new_chat.created_at,
    )


@chat_router.get("/{chat_id}")
async def get_chat(db: SessionDep, user: CurrentUser, chat_id: UUID) -> list[MessageOutput] | None:
    if not user:
        raise Exception("Unauthorized")

    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    if chat is None:
        raise ValueError("Chat not found")

    return [message_to_gql(message) for message in messages]
