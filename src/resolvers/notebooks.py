from typing import List

from src.schemas.types import Note
from src.services.supabase import supabase_client
from src.utils.logger import logger


def get_notebooks():
    return []


def get_user_notes(user_id: str) -> List[Note]:
    logger.info(f"Getting notes for user {user_id}", {"user_id": user_id})
    response = (
        supabase_client.from_("notes").select("*").eq("user_id", user_id).execute()
    )
    logger.info(f"Got notes for user {user_id}", {"notes": response.data})
    return [Note(**note) for note in response.data]
