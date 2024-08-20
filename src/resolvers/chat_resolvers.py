from typing import List
import uuid

from sqlalchemy.orm import Session
import strawberry
from strawberry.types import Info

from src.data.models.chat import Chat, ChatOutput, ChatState, Message as MessageModel
from src.data.data_access import insert_message
from src.schemas.types import Message
from src.types.llm_output_types import LLMFocusOutput
from src.utils.logger import logger
from src.services.sherpa import get_sherpa_response, get_chat_summary

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

        return [new_chat.to_gql()]

    return [chat.to_gql() for chat in chats]


@strawberry.type
class ChatSummaryOutputItem:
    text: str

@strawberry.type
class ChatMessagesResponse:
    messages: List[Message]
    summary: List[ChatSummaryOutputItem]
    
async def chat_messages(info: Info, chat_id: str) -> ChatMessagesResponse | None:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")
    profile_id = info.context.get("profile").id
    messages = session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()
    chat_summary = get_chat_summary(messages=messages, profile_id=profile_id, session=session)
    if not chat_summary:
        logger.error("Chat summary could not be generated.")
        return None
    
    return ChatMessagesResponse(
        messages=[message_to_gql(message) for message in messages],
        summary=[ChatSummaryOutputItem(text=c.text) for c in chat_summary.items]
    )



async def send_chat_message(
    info: Info, chat_id: str, message: str
) -> List[Message]:

    if not info.context.get("user"):
        raise Exception("Unauthorized")

    profile_id: uuid.UUID = info.context.get("profile").id
    session: Session = info.context.get("session")

    # Insert new message into the database
    user_message = insert_message(
        session, 
        chat_id=chat_id, 
        profile_id=profile_id, 
        message=message, 
        role="user"
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

async def end_chat(info: Info, chat_id: str) -> LLMFocusOutput | None:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")
    chat = session.query(Chat).filter(Chat.id == chat_id).first()

    if chat is None:
        raise ValueError("Chat not found")

    chat.state = ChatState.ENDED
    session.add(chat)
    
    chat_history: List[MessageModel] = session.query(MessageModel).filter(MessageModel.chat_id == chat_id).all()
    chat_summary = get_chat_summary(session=session, messages=chat_history, profile_id=chat.profile_id)
    if not chat_summary:
        logger.error("Chat summary could not be generated.")
        return None
    
    session.commit()
    return chat_summary


