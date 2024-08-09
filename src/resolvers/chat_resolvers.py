from typing import List
import strawberry

from src.data.data_access import get_sherpa_response, insert_message
from src.data.models import Chat as ChatModel, Message as MessageModel
from src.schemas.types import Chat, Message
from src.utils.logger import logger


def chat_to_gql(chat: ChatModel) -> Chat:
    try:
        return Chat(
            **{field: getattr(chat, field) for field in ["id", "title", "created_at"]}
        )
    except AttributeError as e:
        logger.error(f"Error converting ChatModel to Chat: {e}")
        raise ValueError("Invalid ChatModel data")


def message_to_gql(message: MessageModel) -> Message:
    try:
        return Message(
            **{
                field: getattr(message, field)
                for field in [
                    "id",
                    "chat_id",
                    "profile_id",
                    "role",
                    "message",
                    "created_at",
                ]
            }
        )
    except AttributeError as e:
        logger.error(f"Error converting MessageModel to Message: {e}")
        raise ValueError("Invalid MessageModel data")


async def chats(info: strawberry.Info) -> List[Chat]:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session = info.context.get("session")
    profile_id = info.context.get("profile").id
    chats = session.query(ChatModel).filter(ChatModel.profile_id == profile_id).all()

    if len(chats) == 0:
        # Create a new chat if none exists
        new_chat = ChatModel(
            title="New Chat",
            profile_id=profile_id,
        )
        session.add(new_chat)
        session.commit()

        return [chat_to_gql(new_chat)]

    return [chat_to_gql(chat) for chat in chats]


async def chat_messages(info: strawberry.Info, chat_id: str) -> List[Message]:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session = info.context.get("session")
    messages = session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()

    return [message_to_gql(message) for message in messages]


async def send_chat_message(
    info: strawberry.Info, chat_id: str, message: str
) -> List[Message]:

    if not info.context.get("user"):
        raise Exception("Unauthorized")

    profile_id = info.context.get("profile").id
    session = info.context.get("session")

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
        role="assistant",
        message=sherpa_response,
    )

    return [
        user_message,
        system_message,
    ]


# User sends text to Sherpa
# Sherpa summarizes the text and sends it back to the user
# User can respond and sherpa will continuously revise summary
# Users can prioritize summary or save for later
