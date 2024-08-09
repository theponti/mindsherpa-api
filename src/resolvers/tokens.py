import jwt
import os
from datetime import UTC, datetime, timedelta

from strawberry import Info
from sqlalchemy.orm import Session

from src.data.models.user import User
from src.schemas.types import AuthPayload

JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET or JWT_SECRET is None:
    raise ValueError("JWT_SECRET environment variable is not set")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    if not JWT_SECRET:
        raise ValueError("JWT_SECRET environment variable is not set")
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_apple_token(id_token: str, nonce: str) -> dict:
    # Implement Apple ID token verification here
    # This should validate the token with Apple's public key and verify the nonce
    # Return the decoded token payload if valid, raise an exception if not
    # For brevity, we're assuming the token is valid in this example
    return {"sub": "example_apple_id", "email": "user@example.com"}


class RefreshTokenService:
    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        if not JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is not set")
        return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    async def refresh_token(info: Info, refresh_token: str) -> AuthPayload:
        if not JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is not set")

        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = int(payload["sub"])
        except (jwt.InvalidTokenError, ValueError):
            raise ValueError("Invalid refresh token")

        session: Session = info.context["session"]
        user = session.query(User).filter(User.id == user_id).first()

        if user is None:
            raise ValueError("User not found")

        access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = RefreshTokenService.create_refresh_token(
            {"sub": str(user.id)}
        )

        return AuthPayload(
            user_id=user.id, access_token=access_token, refresh_token=new_refresh_token
        )
