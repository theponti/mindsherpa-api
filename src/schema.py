import enum
import typing
from fastapi import HTTPException, UploadFile
import strawberry

from src.services.supabase import supabase_client
from src.resolvers.notebooks import get_notebooks, get_notes


@strawberry.enum
class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


@strawberry.type
class Profile:
    id: int
    name: str | None
    avatar_url: str | None
    user_id: str


@strawberry.type
class Chat:
    id: int
    title: str
    created_at: str
    user_id: str


@strawberry.type
class Message:
    id: int
    content: str
    created_at: str
    user_id: str
    chat_id: int
    role: MessageRole


@strawberry.type
class Notebook:
    title: str
    id: str
    created_at: str
    updated_at: str
    user_id: str


@strawberry.type
class Note:
    title: str
    id: str
    created_at: str
    updated_at: str
    user_id: str
    notebook_id: str


@strawberry.type
class User:
    id: str
    email: str | None


@strawberry.type
class Query:
    notebooks: typing.List[Notebook] = strawberry.field(resolver=get_notebooks)
    notes: typing.List[Note] = strawberry.field(resolver=get_notes)

    @strawberry.field
    async def current_user(self, info: strawberry.Info) -> User:
        current_user = info.context.get("current_user")

        if not current_user:
            raise Exception("Unauthorized")

        return User(id=current_user.id, email=current_user.email)

    @strawberry.field
    async def chats(self, info: strawberry.Info) -> typing.List[Chat]:
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
        self, info: strawberry.Info, audio_file: UploadFile, chat_id: int
    ) -> bool:
        current_user = info.context.get("current_user")
        if not current_user:
            raise Exception("Unauthorized")
        return True


def get_current_user(token: str) -> User:
    response = supabase_client.auth.get_user(token)

    if response is None:
        raise HTTPException(
            status_code=403, detail="Invalid authentication credentials"
        )

    return User(id=response.user.id, email=response.user.email)
