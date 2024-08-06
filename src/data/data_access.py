from sqlalchemy.orm import Session
from typing import List

from src.data.models import Message
from src.data.notes import get_user_notes
from src.services.openai_service import openai_client


def get_chat_history(session: Session, chat_id: int) -> List[Message]:
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
