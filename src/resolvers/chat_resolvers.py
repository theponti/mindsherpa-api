from typing import Annotated, List, Required
import strawberry
from sqlalchemy.orm import Session

from src.data.models import Focus, Chat, ChatState
from src.data.data_access import get_sherpa_response, insert_message
from src.data.models import Chat as ChatModel, Message as MessageModel
from src.schemas.types import Chat as ChatType, Message
from src.utils.logger import logger
from src.services.focus import get_focus_by_profile_id
from src.services.sherpa import get_focus_items_from_text


def chat_to_gql(chat: ChatModel) -> ChatType:
    try:
        return ChatType(
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


@strawberry.type
class ChatSummaryOutputItem:
    text: str

@strawberry.type
class ChatMessagesResponse:
    messages: List[Message]
    summary: List[ChatSummaryOutputItem]
    
async def chat_messages(info: strawberry.Info, chat_id: str) -> ChatMessagesResponse:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session = info.context.get("session")
    profile_id = info.context.get("profile").id
    messages = session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()
    chat_summary = get_chat_summary(messages=messages, profile_id=profile_id, session=session)
    
    logger.info("Chat summary", {"summary": chat_summary})
    return ChatMessagesResponse(
        messages=[message_to_gql(message) for message in messages],
        summary=[ChatSummaryOutputItem(text=c["text"]) for c in chat_summary]
    )



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

async def end_chat(info: strawberry.Info, chat_id: str) -> dict:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session = info.context.get("session")
    chat: ChatModel = session.query(ChatModel).filter(ChatModel.id == chat_id).first()

    if chat is None:
        raise ValueError("Chat not found")

    chat.state = ChatState.ENDED
    session.add(chat)
    
    chat_history: List[MessageModel] = session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()
    chat_summary = get_chat_summary(session=session, messages=chat_history, profile_id=chat.profile_id)
    if not chat_summary:
        return { "error": "The chat could not have a summary generated." }
    
    session.commit()
    return chat_summary


def get_chat_summary(messages: List[MessageModel], profile_id: Annotated[str, Required], session: Session) -> List[Focus]:
    existing_focus_items = get_focus_by_profile_id(profile_id=profile_id, session=session)
    transcript = """
    Analyze the chat transcript. Do not include any existing items in the focus list.

    ### Existing Items
    {existing_items}

    ### Chat Transcript
    {chat_history}
    """.format(
        existing_items="\n".join([f"{item.type.capitalize()}: {item.text}" for item in existing_focus_items]),
        chat_history="\n".join([f"{message.role.capitalize()}: {message.message}" for message in messages])
    )
    return get_focus_items_from_text(text=transcript)

