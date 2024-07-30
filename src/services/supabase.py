import os
from fastapi import HTTPException
from supabase import create_client, Client

SUPABASE_URL: str = os.environ.get("SUPABASE_URL") or ""
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY") or ""

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def get_current_user(token: str):
    response = supabase_client.auth.get_user(token)

    if response is None:
        raise HTTPException(
            status_code=403, detail="Invalid authentication credentials"
        )

    return response.user
