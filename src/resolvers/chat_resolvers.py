import enum
import uuid
from typing import List

import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from src.data.data_access import insert_message
from src.data.models.chat import Chat, ChatState
from src.data.models.chat import Message as MessageModel
from src.services.sherpa import get_chat_summary, get_sherpa_response
from src.types.llm_output_types import LLMFocusOutput
from src.utils.logger import logger


@strawberry.type
class ChatOutput:
    id: str
    title: str
    created_at: str


@strawberry.enum
class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


@strawberry.type
class MessageOutput:
    id: str
    message: str
    role: MessageRole
    chat_id: str
    profile_id: str
    created_at: str


def chat_to_gql(chats: List[Chat]) -> List[ChatOutput]:
    try:
        return [
            ChatOutput(
                **{
                    field: getattr(chat, field)
                    for field in ["id", "title", "created_at"]
                }
            )
            for chat in chats
        ]
    except AttributeError as e:
        logger.error(f"Error converting ChatModel to Chat: {e}")
        raise ValueError("Invalid ChatModel data")


def message_to_gql(message: MessageModel) -> MessageOutput:
    try:
        return MessageOutput(
            **{
                field: getattr(message, field)
                for field in MessageOutput.__dataclass_fields__
            }
        )
    except AttributeError as e:
        logger.error(f"Error converting MessageModel to Message: {e}")
        raise ValueError("Invalid MessageModel data")


async def chats(info: strawberry.Info) -> List[ChatOutput]:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session = info.context.get("session")
    profile_id = info.context.get("profile").id
    chats = session.query(Chat).filter(Chat.profile_id == profile_id).all()

    if len(chats) == 0:
        # Create a new chat if none exists
        new_chat = Chat(
            title="New Chat",
            profile_id=profile_id,
        )
        session.add(new_chat)
        session.commit()

        return chat_to_gql([new_chat])

    return chat_to_gql(chats)


@strawberry.type
class ChatSummaryOutputItem:
    text: str


@strawberry.type
class ChatMessagesResponse:
    messages: List[MessageOutput]


async def chat_summary(info: Info, chat_id: str) -> List[ChatSummaryOutputItem] | None:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")
    profile_id = info.context.get("profile").id
    messages = session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()
    chat_summary = get_chat_summary(
        messages=messages, profile_id=profile_id, session=session
    )
    if not chat_summary:
        logger.error("Chat summary could not be generated.")
        return None

    return [ChatSummaryOutputItem(text=c.text) for c in chat_summary.items]


async def chat_messages(info: Info, chat_id: str) -> ChatMessagesResponse:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")

    messages = session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()

    return ChatMessagesResponse(
        messages=[message_to_gql(message) for message in messages],
    )


async def send_chat_message(
    info: Info, chat_id: str, message: str
) -> List[MessageOutput]:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    profile_id: uuid.UUID = info.context.get("profile").id
    session: Session = info.context.get("session")

    # Insert new message into the database
    user_message = insert_message(
        session, chat_id=chat_id, profile_id=profile_id, message=message, role="user"
    )

    # Retrieve message from ChatGPT
    sherpa_response = get_sherpa_response(session, message, chat_id, profile_id)
    if sherpa_response is None:
        raise Exception("No response from the model")

    # Save system response to the database
    system_message = insert_message(
        session,
        chat_id=chat_id,
        profile_id=profile_id,
        role=MessageRole.ASSISTANT.value,
        message=sherpa_response.message,
    )

    return [
        user_message,
        system_message,
    ]


async def end_chat(info: Info, chat_id: str) -> LLMFocusOutput | None:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")
    chat = session.query(Chat).filter(Chat.id == chat_id).first()

    if chat is None:
        raise ValueError("Chat not found")

    chat.state = ChatState.ENDED
    session.add(chat)

    chat_history: List[MessageModel] = (
        session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()
    )
    chat_summary = get_chat_summary(
        session=session, messages=chat_history, profile_id=chat.profile_id
    )
    if not chat_summary:
        logger.error("Chat summary could not be generated.")
        return None

    session.commit()
    return chat_summary
