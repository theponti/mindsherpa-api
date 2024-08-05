from fastapi import HTTPException
from src.services.supabase import supabase_client
from src.schemas.types import User


def get_current_user(token: str) -> User:
    response = supabase_client.auth.get_user(token)

    if response is None:
        raise HTTPException(
            status_code=403, detail="Invalid authentication credentials"
        )

    return User(id=response.user.id, email=response.user.email)
