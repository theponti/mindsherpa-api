import enum
from typing import List
from fastapi import HTTPException
import strawberry
from strawberry.file_uploads import Upload

from src.services.openai_service import openai_client
from src.services.supabase import supabase_client
from src.resolvers.notebooks import get_notebooks, get_user_notes
from src.schemas.types import Chat, Message, Note, Notebook, User
from src.utils.logger import logger


@strawberry.type
class Query:
    notebooks: List[Notebook] = strawberry.field(resolver=get_notebooks)
    notes: List[Note] = strawberry.field(resolver=get_user_notes)

    @strawberry.field
    async def current_user(self, info: strawberry.Info) -> User:
        current_user = info.context.get("current_user")

        if not current_user:
            raise Exception("Unauthorized")

        return User(id=current_user.id, email=current_user.email)

    @strawberry.field
    async def chats(self, info: strawberry.Info) -> List[Chat]:
        result = (
            supabase_client.from_("chats")
            .select("*")
            .eq("user_id", info.context.get("current_user").id)
            .execute()
        )
        return [Chat(**chat) for chat in result.data]


@strawberry.type
class Mutation:
    @strawberry.field
    async def upload_voice_note(
        self, info: strawberry.Info, audio_file: Upload, chat_id: int
    ) -> bool:
        current_user = info.context.get("current_user")
        if not current_user:
            raise Exception("Unauthorized")
        return True

    @strawberry.field
    async def send_chat_message(
        self, info: strawberry.Info, chat_id: int, message: str
    ) -> List[Message]:
        current_user = info.context.get("current_user")
        if not current_user:
            raise Exception("Unauthorized")

        # Insert new message into the database
        user_message = insert_message(chat_id, message, current_user.id, "user")

        # Retrieve message from ChatGPT
        sherpa_response = get_sherpa_response(message, chat_id, current_user.id)
        if sherpa_response is None:
            raise Exception("No response from the model")

        # Save system response to the database
        system_message = insert_message(
            chat_id=chat_id,
            user_id=current_user.id,
            role="assistant",
            message=sherpa_response,
        )

        return [
            user_message,
            system_message,
        ]


def get_current_user(token: str) -> User:
    response = supabase_client.auth.get_user(token)

    if response is None:
        raise HTTPException(
            status_code=403, detail="Invalid authentication credentials"
        )

    return User(id=response.user.id, email=response.user.email)


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
