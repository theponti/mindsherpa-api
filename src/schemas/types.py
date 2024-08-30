import uuid

import strawberry


@strawberry.type
class AuthPayload:
    user_id: uuid.UUID
    access_token: str
    refresh_token: str


@strawberry.type
class Profile:
    id: int
    full_name: str | None
    user_id: str


@strawberry.type
class NoteOutput:
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
    access_token: str
    refresh_token: str
