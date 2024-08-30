from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from pydantic import BaseModel

from src.utils.config import settings

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

REFRESH_TOKEN_EXPIRE_DAYS = 30

JWT_SECRET = settings.SECRET_KEY


class AccessTokenSubject(BaseModel):
    id: str
    email: str
    name: str


class AccessTokenPayload(BaseModel):
    sub: AccessTokenSubject
    iat: int
    exp: int


class TokenService:
    @staticmethod
    def create_access_token(
        subject: AccessTokenSubject,
        expires_delta: Annotated[timedelta, Optional] = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    ) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": subject.model_dump_json()}
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: AccessTokenSubject):
        return TokenService.create_access_token(
            subject=data,
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

    @staticmethod
    def verify_apple_token(id_token: str, nonce: str) -> dict:
        # Implement Apple ID token verification here
        # This should validate the token with Apple's public key and verify the nonce
        # Return the decoded token payload if valid, raise an exception if not
        # For brevity, we're assuming the token is valid in this example
        return {"sub": "example_apple_id", "email": "user@example.com"}

    @staticmethod
    def decode_access_token(token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return AccessTokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
