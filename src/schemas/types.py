import enum
import strawberry


@strawberry.type
class AuthPayload:
    user_id: int
    access_token: str
    refresh_token: str


@strawberry.enum
class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


@strawberry.type
class Profile:
    id: int
    full_name: str | None
    user_id: str


@strawberry.type
class Chat:
    id: str
    title: str
    created_at: str


@strawberry.type
class Message:
    id: str
    message: str
    role: MessageRole
    chat_id: str
    profile_id: str
    created_at: str


@strawberry.type
class ChatMessageInput:
    chat_id: int
    message: str


@strawberry.type
class NoteOutput:
    id: str
    content: str
    created_at: str


@strawberry.type
class CreateNote:
    id: str
    content: str
    created_at: str


@strawberry.type
class User:
    id: str
    email: str | None


@strawberry.input
class UpdateProfileInput:
    full_name: str
    user_id: str


@strawberry.type
class UpdateProfilePayload:
    profile: Profile


@strawberry.input
class CreateUserInput:
    email: str


@strawberry.type
class CreateUserPayload:
    user: User
    profile: Profile
