import json
from typing import Annotated

import jwt
from fastapi import HTTPException, Request, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.data.db import SessionLocal
from src.data.models.user import Profile, User
from src.resolvers.user_resolvers import get_user_by_token
from src.utils import security
from src.utils.config import settings
from src.utils.logger import logger


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]
# TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(db: SessionDep, request: Request) -> User:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]

    # If the environment is not test, we can retrieve the user from Supabase.
    if settings.ENVIRONMENT != "test":
        user = get_user_by_token(db, token)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        return user

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.JWT_ALGORITHM])
        sub = json.loads(payload["sub"])
        email = sub["email"]
    except (jwt.InvalidTokenError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
        )

    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        elif not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
    except (Exception, HTTPException) as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            logger.error(f"Error getting user: {str(e)}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unauthorized: {str(e)}")


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user


def get_profile(db: SessionDep, user: CurrentUser) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


CurrentProfile = Annotated[Profile, Depends(get_profile)]
