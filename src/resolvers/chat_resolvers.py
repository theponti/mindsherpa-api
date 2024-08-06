from typing import List
import strawberry
from enum import Enum
import json

from src.data.data_access import get_sherpa_response, insert_message
from src.data.models import Chat as ChatModel, Message as MessageModel
from src.schemas.types import Chat, Message
from src.services.file_service import get_file_contents
from src.services.groq_service import groq_client
from src.utils.ai_models import open_source_models
from src.utils.logger import logger
from src.utils.generation_statistics import GenerationStatistics


def chat_to_gql(chat: ChatModel) -> Chat:
    return Chat(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
    )


def message_to_gql(message: MessageModel) -> Message:
    return Message(
        id=message.id,
        chat_id=message.chat_id,
        profile_id=message.profile_id,
        role=message.role,
        message=message.message,
        created_at=message.created_at,
    )


class AvailablePrompts(Enum):
    v1 = "user_input_formatter_v1.md"
    v2 = "user_input_formatter_v2.md"


def get_prompt(prompt: AvailablePrompts):
    return get_file_contents(f"src/prompts/{prompt.value}")


def analyze_user_input(transcript: str, model: str = "llama3-70b-8192"):
    system_prompt = get_prompt(AvailablePrompts.v2)

    if model in open_source_models:

        try:
            completion = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript},
                ],
                temperature=0.3,
                max_tokens=8000,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None,
            )

            usage = completion.usage
            # print("------ USAGE ---", usage)

        except Exception as e:
            logger.error(f" ********* API error ********: {e} ***** ")
            return None, {"error": str(e)}

        try:
            if usage:
                statistics_to_return = GenerationStatistics(
                    input_time=int(usage.prompt_time) if usage.prompt_time else 0,
                    output_time=(
                        int(usage.completion_time) if usage.completion_time else 0
                    ),
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens,
                    total_time=int(usage.total_time) if usage.total_time else 0,
                    model_name=model,
                )
                logger.info("focus_stats", statistics_to_return.get_stats())

                return (
                    json.loads(completion.choices[0].message.content)
                    if completion.choices[0].message.content
                    else None
                )
        except Exception as e:
            logger.error(f" ********* STATISTICS GENERATION error ******* : {e} ")
            return None, {"error": str(e)}


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
