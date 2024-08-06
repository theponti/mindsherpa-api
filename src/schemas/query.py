import json
from typing import List
import strawberry

from src.data.data_access import get_user_context
from src.data.notes import get_user_notes
from src.resolvers.chat_resolvers import analyze_user_input, chats, chat_messages
from src.resolvers.focus import Focus, convert_dict_to_focus
from src.resolvers.user_resolvers import GetProfileOutput, get_profile
from src.schemas.types import Chat, Message, NoteOutput, User
from src.utils.logger import logger


@strawberry.type
class Query:
    chats: List[Chat] = strawberry.field(resolver=chats)
    chat_messages: List[Message] = strawberry.field(resolver=chat_messages)
    profile: GetProfileOutput = strawberry.field(resolver=get_profile)

    @strawberry.field
    async def notes(self, info: strawberry.Info) -> List[NoteOutput]:
        current_user = info.context.get("user")

        if not current_user:
            raise Exception("Unauthorized")

        profile_id = info.context.get("profile").id
        notes = get_user_notes(info.context.get("session"), profile_id)
        note_dicts = [note.__dict__ for note in notes]
        return [
            NoteOutput(
                id=note["id"],
                content=note["content"],
                created_at=note["created_at"],
            )
            for note in note_dicts
        ]

    @strawberry.field
    async def current_user(self, info: strawberry.Info) -> User:
        current_user = info.context.get("user")

        if not current_user:
            raise Exception("Unauthorized")

        return User(id=current_user.id, email=current_user.email)

    @strawberry.field
    async def focus(self, info: strawberry.Info) -> Focus:
        """
        Returns notes structure content as well as total tokens and total time for generation.
        """
        current_user = info.context.get("user")

        if not current_user:
            raise Exception("Unauthorized")

        try:
            profile_id = info.context.get("profile").id
            history = get_user_context(info.context.get("session"), profile_id)
            analysis = analyze_user_input(
                """
            ### User Context:
            {user_context}

            ### Chat History:
            {chat_history}
            """.format(
                    user_context=history.note_history, chat_history=history.chat_history
                )
            )

            return convert_dict_to_focus(analysis)
        except Exception as e:
            logger.error(f" ********* ERROR IN USER PROMPT ********: {e} ***** ")
            raise Exception("Error retrieving user focus")
