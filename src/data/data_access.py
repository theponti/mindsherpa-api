from dataclasses import dataclass
from sqlalchemy.orm import Session
from typing import List

from src.data.models import Message
from src.data.notes import get_user_notes
from src.services.openai_service import openai_client


def get_full_chat_history(session: Session, profile_id: str) -> List[Message]:
    messages = session.query(Message).filter(Message.profile_id == profile_id).all()
    return messages


def get_chat_history(session: Session, chat_id: str) -> List[Message]:
    messages = session.query(Message).filter(Message.chat_id == chat_id).all()
    return messages


def insert_message(
    session: Session, chat_id: str, message: str, profile_id: str, role: str
) -> Message:
    new_message = Message(
        message=message, chat_id=chat_id, profile_id=profile_id, role=role
    )
    session.add(new_message)
    session.commit()

    return new_message


def get_sherpa_response(
    session: Session, message: str, chat_id, profile_id
) -> str | None:
    system_prompt = """
    You are the user's expert-level personal assistant and best friend.

    You have full history of the user's chat with you and their Context, which is a list of notes they have taken.
    These notes include their goals, tasks, and any other important information they have shared with you.

    The user is going to provide with their entire chat history with you, along with their latest message and \n

    You must respond to the user's message based on the chat history.

    ## Rules:
    - Do not say who you are or that you are an AI.
    - Your response should be in a friendly, upbeat and conversational tone.
    - Your response should be helpful and relevant to the user's latest message and their Context.
    - Your goal is to help the user live a more productive and fulfilling life by incorporating their goals and tasks into your responses.
       - For example, if the user mentions a goal of exercising more, you could suggest a workout routine.
       - Your responses should use positive reinforcement to encourage the user to achieve their goals.
    - Your response should use all of the User Context and the entire Chat History to provide context to your response.
    - Your response should use that knowledge about the user to answer the user's latest message.

    ## User Context
    {user_context}

    ## Chat History
    {chat_history}
    """

    chat_history = get_chat_history(session, chat_id)
    user_context = get_user_notes(session, profile_id)
    chat_history_contents = [message.message for message in chat_history]
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


@dataclass(frozen=True)
class GetUserContextOutput:
    chat_history: List[str]
    note_history: List[str]


def get_user_context(session: Session, profile_id: str) -> GetUserContextOutput:
    chat_history = get_full_chat_history(session, profile_id=profile_id)
    user_context = get_user_notes(session, profile_id)
    chat_history_contents = [str(message.message) for message in chat_history]
    user_context_contents = [str(note.content) for note in user_context]
    return GetUserContextOutput(chat_history_contents, user_context_contents)
