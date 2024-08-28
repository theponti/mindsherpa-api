from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter
from fastapi.requests import Request
from pydantic.main import BaseModel

from src.data.models.chat import Chat, ChatState, Message
from src.data.models.user import User
from src.resolvers.chat_resolvers import MessageOutput, message_to_gql

chat_router = APIRouter()


class ChatOutput(BaseModel):
    id: UUID
    title: str
    created_at: datetime


@chat_router.get("/active")
async def get_active_chat(request: Request) -> ChatOutput | None:
    session = request.state.session
    user: User = request.state.user
    profile_id = request.state.profile.id

    if not user:
        raise Exception("Unauthorized")

    chat = (
        session.query(Chat)
        .filter(Chat.profile_id == profile_id)
        .filter(Chat.state == ChatState.ACTIVE.value)
        .first()
    )

    if chat is None:
        raise ValueError("Chat not found")

    return ChatOutput(**chat.__dict__)


class EndChatPayload(BaseModel):
    chat_id: UUID


@chat_router.post("/end")
async def end_chat(request: Request, input: EndChatPayload) -> ChatOutput | None:
    session = request.state.session
    user: User = request.state.user

    if not user:
        raise Exception("Unauthorized")

    chat = session.query(Chat).filter(Chat.id == input.chat_id).first()

    if chat is None:
        raise ValueError("Chat not found")

    chat.state = ChatState.ENDED.value
    session.add(chat)

    new_chat = Chat(
        title="New Chat",
        profile_id=chat.profile_id,
    )
    session.add(new_chat)
    session.commit()

    return ChatOutput(**chat.__dict__)


@chat_router.get("/{chat_id}")
async def get_chat(request: Request, chat_id: UUID) -> List[MessageOutput] | None:
    session = request.state.session
    user: User = request.state.user

    if not user:
        raise Exception("Unauthorized")

    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    messages = session.query(Message).filter(Message.chat_id == chat_id).all()
    if chat is None:
        raise ValueError("Chat not found")

    return [message_to_gql(message) for message in messages]
