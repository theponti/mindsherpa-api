import uuid

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from src.data.models.user import Profile, User
from src.utils.context import CurrentProfile, SessionDep
from src.utils.security import AccessTokenSubject, TokenService

user_router = APIRouter()


class CreateUserPayload(BaseModel):
    email: str
    user_id: uuid.UUID
    profile_id: uuid.UUID
    access_token: str
    refresh_token: str


class CreateUserInput(BaseModel):
    email: str


class ProfileOutput(BaseModel):
    id: str
    full_name: str
    user_id: str


@user_router.get("/profile")
async def get_profile(profile: CurrentProfile) -> ProfileOutput:
    return ProfileOutput(
        id=str(profile.id),
        full_name=str(profile.full_name),
        user_id=str(profile.user_id),
    )


class UpdateProfileInput(BaseModel):
    full_name: str


@user_router.put("/profile")
async def update_profile(profile: CurrentProfile, db: SessionDep, input: UpdateProfileInput) -> ProfileOutput:
    profile = db.query(Profile).filter(Profile.user_id == profile.user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile does not exist")

    if input.full_name:
        setattr(profile, "full_name", input.full_name)

    db.commit()

    return ProfileOutput(
        id=str(profile.id),
        full_name=str(profile.full_name),
        user_id=str(profile.user_id),
    )


@user_router.post("/create")
def create_user_and_profile(db: SessionDep, input: CreateUserInput) -> CreateUserPayload:
    user = db.query(User).filter(User.email == input.email).first()
    if user:
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    else:
        user = User(email=input.email)
        db.add(user)
        db.commit()

        profile = Profile(user_id=user.id, provider="apple")
        db.add(profile)
        db.commit()

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile does not exist")

    access_token_subject = AccessTokenSubject(
        id=str(user.id),
        email=user.email,
        name=user.name,
    )
    access_token = TokenService.create_access_token(subject=access_token_subject)
    refresh_token = TokenService.create_refresh_token(access_token_subject)

    return CreateUserPayload(
        email=user.email,
        user_id=user.id,
        profile_id=profile.id,
        access_token=access_token,
        refresh_token=refresh_token,
    )
