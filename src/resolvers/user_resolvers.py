import uuid

import strawberry
from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from strawberry.types import Info

from src.data.models.user import (
    Profile,
    User,
    create_profile,
    create_user,
    get_profile_by_user_id,
    get_user_by_user_id,
)
from src.schemas.types import (
    AuthPayload,
    CreateUserInput,
    CreateUserPayload,
    UpdateProfileInput,
)
from src.services.supabase import supabase_client
from src.utils.security import AccessTokenSubject, TokenService


def get_user_by_token(session: Session, token: str) -> User:
    try:
        response = supabase_client.auth.get_user(token)
        if response is None:
            raise HTTPException(status_code=403, detail="Invalid authentication credentials")

        user_id = response.user.id
        user = get_user_by_user_id(session, uuid.UUID(user_id))
        return user
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


async def save_apple_user(info: Info, id_token: str, nonce: str) -> AuthPayload:
    try:
        apple_payload = TokenService.verify_apple_token(id_token, nonce)
    except InvalidTokenError:
        raise ValueError("Invalid Apple ID token")

    apple_id = apple_payload["sub"]
    email = apple_payload.get("email")

    session: Session = info.context["session"]
    user = session.query(User).filter(User.apple_id == apple_id).first()

    if user is None:
        user = User(apple_id=apple_id, email=email)
        session.add(user)
        session.commit()
    elif email and user.email != email:
        user.email = email
        session.commit()

    access_token_subject = AccessTokenSubject(
        id=str(user.id),
        email=user.email,
        name=user.name,
    )
    # Create access and refresh tokens
    access_token = TokenService.create_access_token(subject=access_token_subject)
    refresh_token = TokenService.create_refresh_token(access_token_subject)

    return AuthPayload(user_id=user.id, access_token=access_token, refresh_token=refresh_token)


async def create_user_and_profile(info: Info, input: CreateUserInput) -> CreateUserPayload:
    session: Session = info.context["session"]

    user = User(email=input.email)
    session.add(user)
    session.commit()

    profile = Profile(user_id=user.id, provider="apple")
    session.add(profile)
    session.commit()

    access_token_subject = AccessTokenSubject(
        id=str(user.id),
        email=user.email,
        name=user.name,
    )
    access_token = TokenService.create_access_token(subject=access_token_subject)
    refresh_token = TokenService.create_refresh_token(access_token_subject)

    return CreateUserPayload(
        user=user, profile=profile, access_token=access_token, refresh_token=refresh_token
    )


@strawberry.type
class GetProfileOutput:
    id: str
    full_name: str
    user_id: str


async def get_profile(info: Info) -> GetProfileOutput:
    profile: Profile | None = info.context.get("profile")

    if not info.context.get("user") or not profile:
        raise ValueError("Unauthorized")

    return GetProfileOutput(
        id=str(profile.id),
        full_name=str(profile.full_name),
        user_id=str(profile.user_id),
    )


async def update_profile(info: Info, input: UpdateProfileInput) -> Profile:
    session: Session = info.context["session"]
    if not info.context.get("user"):
        raise ValueError("Unauthorized")

    profile = session.query(Profile).filter(Profile.user_id == info.context["user"].id).first()

    if not profile:
        raise ValueError("Profile does not exist")

    if input.full_name:
        setattr(profile, "full_name", input.full_name)

    session.commit()

    return profile


async def refresh_token(info: Info, refresh_token: str) -> AuthPayload:
    payload = TokenService.decode_access_token(refresh_token)

    session: Session = info.context["session"]
    user = session.query(User).filter(User.id == payload.sub.id).first()

    if user is None:
        raise ValueError("User not found")

    subject = AccessTokenSubject(id=str(user.id), email=user.email, name=user.name)
    access_token = TokenService.create_access_token(subject=subject)
    new_refresh_token = TokenService.create_refresh_token(subject)

    return AuthPayload(user_id=user.id, access_token=access_token, refresh_token=new_refresh_token)
