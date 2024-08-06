from datetime import datetime, timedelta
from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from strawberry.types import Info
import jwt
import os
import strawberry
import uuid


from src.data.models import User, Profile
from src.services.supabase import supabase_client
from src.schemas.types import CreateUserInput, CreateUserPayload, UpdateProfileInput

JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")


JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


def get_current_user(session: Session, token: str) -> tuple[User, Profile]:
    response = supabase_client.auth.get_user(token)

    if response is None:
        raise HTTPException(
            status_code=403, detail="Invalid authentication credentials"
        )

    user_id = response.user.id
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            email=response.user.email,
        )
        session.add(user)
        session.commit()

    profile = session.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        profile = Profile(id=uuid.uuid4(), provider="apple", user_id=user.id)
        session.add(profile)
        session.commit()

    return User(id=response.user.id, email=response.user.email), profile


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_apple_token(id_token: str, nonce: str) -> dict:
    # Implement Apple ID token verification here
    # This should validate the token with Apple's public key and verify the nonce
    # Return the decoded token payload if valid, raise an exception if not
    # For brevity, we're assuming the token is valid in this example
    return {"sub": "example_apple_id", "email": "user@example.com"}


@strawberry.type
class AuthPayload:
    user_id: int
    access_token: str
    refresh_token: str


async def save_apple_user(info: Info, id_token: str, nonce: str) -> AuthPayload:
    # Verify the Apple ID token
    try:
        apple_payload = verify_apple_token(id_token, nonce)
    except InvalidTokenError:
        raise ValueError("Invalid Apple ID token")

    apple_id = apple_payload["sub"]
    email = apple_payload.get("email")

    # Get the database session from the context
    session: Session = info.context["session"]

    # Check if the user already exists
    user = session.query(User).filter(User.apple_id == apple_id).first()

    if user is None:
        # Create a new user
        user = User(apple_id=apple_id, email=email)
        session.add(user)
        session.commit()
    elif email and user.email != email:
        # Update the email if it has changed
        user.email = email
        session.commit()

    # Create access and refresh tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return AuthPayload(
        user_id=user.id, access_token=access_token, refresh_token=refresh_token
    )


async def refresh_token(info: Info, refresh_token: str) -> AuthPayload:
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (InvalidTokenError, ValueError):
        raise ValueError("Invalid refresh token")

    session: Session = info.context["session"]
    user = session.query(User).filter(User.id == user_id).first()

    if user is None:
        raise ValueError("User not found")

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return AuthPayload(
        user_id=user.id, access_token=access_token, refresh_token=new_refresh_token
    )


async def create_user_and_profile(
    info: Info, input: CreateUserInput
) -> CreateUserPayload:
    session: Session = info.context["session"]

    user = User(email=input.email)
    session.add(user)
    session.commit()

    profile = Profile(user_id=user.id, provider="apple")
    session.add(profile)
    session.commit()

    # access_token = create_access_token({"sub": str(user.id)})
    # refresh_token = create_refresh_token({"sub": str(user.id)})

    return CreateUserPayload(user=user, profile=profile)


@strawberry.type
class GetProfileOutput:
    id: str
    full_name: str
    user_id: str


async def get_profile(info: Info) -> GetProfileOutput:
    profile: Profile | None = info.context.get("profile")

    if not info.context.get("user") or not profile:
        raise ValueError("Not authenticated")

    return GetProfileOutput(
        id=str(profile.id),
        full_name=str(profile.full_name),
        user_id=str(profile.user_id),
    )


async def update_profile(info: Info, input: UpdateProfileInput) -> Profile:
    session: Session = info.context["session"]
    if not info.context.get("user"):
        raise ValueError("Not authenticated")

    profile = (
        session.query(Profile)
        .filter(Profile.user_id == info.context["user"].id)
        .first()
    )

    if not profile:
        raise ValueError("Profile does not exist")

    if input.full_name:
        setattr(profile, "full_name", input.full_name)

    session.commit()

    return profile


# async def sign_out(info: Info) -> bool:
#     # Get the current user from the context
#     user_id = info.context.get("user_id")
#     if not user_id:
#         raise ValueError("Not authenticated")

#     session: Session = info.context["session"]

#     # Revoke all refresh tokens for the user
#     session.query(RefreshToken).filter(
#         RefreshToken.user_id == user_id,
#         RefreshToken.revoked.is_(None)
#     ).update({"revoked": datetime.utcnow()})

#     session.commit()

#     # Notify subscribers about the account change
#     await broadcast.publish(channel="user_changes", message=str(user_id))

#     return True

# @strawberry.mutation
# async def revoke_token(info: Info, refresh_token: str) -> bool:
#     try:
#         # Verify the token
#         payload = verify_jwt_token(refresh_token)
#         user_id = int(payload["sub"])
#     except (jwt.InvalidTokenError, ValueError):
#         raise ValueError("Invalid refresh token")

#     session: Session = info.context["session"]

#     # Find and revoke the token
#     token = session.query(RefreshToken).filter(
#         RefreshToken.user_id == user_id,
#         RefreshToken.token == refresh_token,
#         RefreshToken.revoked.is_(None)
#     ).first()

#     if token:
#         token.revoked = datetime.utcnow()
#         session.commit()

#         # Notify subscribers about the account change
#         await broadcast.publish(channel="user_changes", message=str(user_id))

#         return True
#     else:
#         return False


# # Setup function to initialize the broadcast client
# async def init_broadcast():
#     await broadcast.connect()

# # Cleanup function to close the broadcast client
# async def cleanup_broadcast():
#     await broadcast.disconnect()
