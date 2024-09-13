import logging
import uuid
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from pydantic.main import BaseModel

from src.data.chat_repository import insert_message
from src.data.models.chat import Chat, ChatState, Message, MessageOutput, MessageRole
from src.services.chat_service import get_chat_response
from src.utils.context import CurrentProfile, CurrentUser, SessionDep

chat_router = APIRouter()


class ChatOutput(BaseModel):
    id: UUID
    title: str
    created_at: datetime


def get_active_chat(db: SessionDep, profile_id: uuid.UUID) -> Chat | None:
    return (
        db.query(Chat)
        .filter(Chat.profile_id == profile_id)
        .filter(Chat.state == ChatState.ACTIVE.value)
        .order_by(Chat.created_at.desc())
        .first()
    )


@chat_router.get("/active")
async def get_active_chat_route(
    db: SessionDep,
    profile: CurrentProfile,
) -> ChatOutput | None:
    try:
        chat = get_active_chat(db, profile)

        if chat is None:
            chat = Chat(
                title="New Chat",
                profile_id=profile.id,
            )
            db.add(chat)
            db.commit()
            db.flush()

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
    chat = db.query(Chat).filter(Chat.id == input.chat_id).first()
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

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
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    messages = db.query(Message).filter(Message.chat_id == chat_id).all()

    return [message.message_to_gql() for message in messages]


class ChatMessageInput(BaseModel):
    message: str


@chat_router.post("/{chat_id}/messages")
async def send_chat_message(
    db: SessionDep, profile: CurrentProfile, input: ChatMessageInput, request: Request
) -> List[MessageOutput]:
    chat_id = UUID(request.path_params["chat_id"])
    user = profile.user

    # Insert new message into the database
    user_message = insert_message(
        db, chat_id=chat_id, profile_id=profile.id, message=input.message, role="user"
    )

    # Retrieve message from ChatGPT
    sherpa_response = get_chat_response(db, input.message, profile.id, user=user)
    if sherpa_response is None:
        raise Exception("No response from the model")

    # Save system response to the database
    system_message = insert_message(
        db,
        chat_id=chat_id,
        profile_id=profile.id,
        role=MessageRole.ASSISTANT.value,
        message=sherpa_response.message,
    )

    return [
        user_message,
        system_message,
    ]
