import enum
import strawberry


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
    profile_id: str
    created_at: str


@strawberry.type
class Message:
    id: int
    message: str
    role: MessageRole
    chat_id: int
    profile_id: str
    created_at: str


@strawberry.type
class ChatMessageInput:
    chat_id: int
    message: str


@strawberry.type
class ChatMessageOutput:
    content: str


@strawberry.type
class Notebook:
    title: str
    id: str
    created_at: str
    updated_at: str
    user_id: str


@strawberry.type
class Note:
    content: str
    id: str
    created_at: str
    user_id: str


@strawberry.type
class User:
    id: str
    email: str | None
