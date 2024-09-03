import json
import uuid

import jwt
import strawberry
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from strawberry.types import Info

from src.data.models.user import (
    Profile,
    User,
    create_profile,
    create_user,
    get_user_by_user_id,
)
from src.services.supabase import supabase_client
from src.utils import security
from src.utils.config import settings
from src.utils.logger import logger
from src.utils.security import AccessTokenSubject, TokenService


@strawberry.type
class UserOutput:
    id: str
    email: str | None


@strawberry.type
class ProfileOutput:
    id: int
    full_name: str | None
    user_id: str


@strawberry.type
class AuthPayload:
    user_id: uuid.UUID
    access_token: str
    refresh_token: str


@strawberry.input
class UpdateProfileInput:
    full_name: str
    user_id: str


@strawberry.type
class UpdateProfilePayload:
    profile: ProfileOutput


def get_user_by_token(session: Session, token: str) -> User:
    try:
        if settings.ENVIRONMENT == "test":
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.JWT_ALGORITHM])
            sub = json.loads(payload["sub"])
            email = sub["email"]
            user = session.query(User).filter(User.email == email).first()
        else:
            response = supabase_client.auth.get_user(token)
            if response is None or response.user is None:
                raise HTTPException(status_code=403, detail="Invalid authentication credentials")
            user_id = response.user.id
            user = get_user_by_user_id(session, uuid.UUID(user_id))
            # If the user has Supabase auth but not a local user, create a local user and profile
            if not user and response.user.email is not None:
                user = create_user(session, user_id=user_id, email=response.user.email)
                profile = create_profile(session, user_id=user.id, provider="apple")

        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        elif not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        return user
    except (Exception, HTTPException, jwt.InvalidTokenError, ValidationError) as e:
        if isinstance(e, HTTPException):
            raise e
        elif isinstance(e, jwt.InvalidTokenError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials",
            )
        elif isinstance(e, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid authentication credentials: {str(e)}",
            )
        elif isinstance(e, IndexError):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        else:
            logger.error(f"Error getting user: {str(e)}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unauthorized: {str(e)}")


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


async def current_user(info: strawberry.Info) -> UserOutput:
    current_user = info.context.get("user")

    if not current_user:
        raise Exception("Unauthorized")

    return UserOutput(id=current_user.id, email=current_user.email)
