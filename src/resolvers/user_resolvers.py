from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from strawberry.types import Info
import strawberry


from src.data.models import User, Profile
from src.resolvers.tokens import (
    RefreshTokenService,
    create_access_token,
    verify_apple_token,
)
from src.services.supabase import supabase_client
from src.schemas.types import (
    AuthPayload,
    CreateUserInput,
    CreateUserPayload,
    UpdateProfileInput,
)


def get_user_by_token(session: Session, token: str) -> tuple[User, Profile]:
    try:
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
            profile = Profile(provider="apple", user_id=user.id)
            session.add(profile)
            session.commit()

        return user, profile
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


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
    refresh_token = RefreshTokenService.create_refresh_token({"sub": str(user.id)})

    return AuthPayload(
        user_id=user.id, access_token=access_token, refresh_token=refresh_token
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

async def sign_up_with_email(
        self, info: strawberry.Info, email: str
    ) -> CreateUserPayload:
        if info.context.get("user"):
            raise ValueError("Already authenticated")

        if not email:
            raise ValueError("Email is required")

        session = info.context.get("session")
        user = User(email=email)
        session.add(user)
        session.commit()

        profile = Profile(user_id=user.id, provider="email")
        return CreateUserPayload(user=user, profile=profile)