from enum import Enum
import json
from typing import List

from src.schemas.types import Message
from src.services.file_service import get_file_contents
from src.services.groq_service import groq_client
from src.services.notebooks import get_user_notes
from src.services.openai_service import openai_client
from src.services.supabase import supabase_client
from src.utils.ai_models import open_source_models
from src.utils.logger import logger
from src.utils.generation_statistics import GenerationStatistics


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


def insert_message(chat_id: int, message: str, user_id: str, role: str) -> Message:
    response = (
        supabase_client.from_("messages")
        .insert(
            {"content": message, "chat_id": chat_id, "user_id": user_id, "role": role}
        )
        .execute()
    )
    return Message(**response.data[0])


def get_chat_history(chat_id: int) -> List[Message]:
    response = (
        supabase_client.from_("messages").select("*").eq("chat_id", chat_id).execute()
    )

    return [Message(**message) for message in response.data]


def get_sherpa_response(message: str, chat_id, user_id) -> str | None:
    system_prompt = """
    You are the user's expert-level personal assistant and best friend.

    You have full history of the user's chat with you and their Context, which is a list of notes they have taken.
    These notes include their goals, tasks, and any other important information they have shared with you.

    The user is going to provide with their entire chat history with you, along with their latest message and \n

    You must respond to the user's message based on the chat history.

    ## Rules:
    - Do not say who you are or that you are an AI.
    - Do not speak in paragraphs.
    - Respond with the least amount of words possible, but use full sentences.
    - Include emojis in your responses where applicable.
    - Your response should be in a friendly, upbeat and conversational tone.
    - Your response should use all of the User Context and the entire Chat History to provide context to your response.
    - Your response should use that knowledge about the user to answer the user's latest message.

    ## User Context
    {user_context}

    ## Chat History
    {chat_history}
    """

    chat_history = get_chat_history(chat_id)
    user_context = get_user_notes(user_id)
    chat_history_contents = [message.content for message in chat_history]
    user_context_contents = [note.content for note in user_context]

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt.format(
                    chat_history=chat_history_contents,
                    user_context=user_context_contents,
                ),
            },
            {"role": "user", "content": message},
        ],
        stream=False,
    )
    content = response.choices[0].message.content
    return content
