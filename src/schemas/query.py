from typing import List
import strawberry

from src.resolvers.chat_resolvers import chats, chat_messages
from src.resolvers.user_resolvers import GetProfileOutput, get_profile
from src.data.notes import get_user_notes
from src.schemas.types import Chat, Message, NoteOutput, User


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
