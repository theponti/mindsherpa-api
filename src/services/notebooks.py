from typing import List
from src.data.db import Session

from src.data.models import Note as NoteModel
from src.schemas.types import Note
from src.utils.logger import logger


def get_notebooks():
    return []


def get_user_notes(user_id: str) -> List[Note]:
    logger.info("notes_search_start", {"user_id": user_id})
    session = Session()
    notes = session.query(NoteModel).filter(NoteModel.user_id == user_id).all()
    note_dicts = [note.__dict__ for note in notes]
    logger.info("notes_search_end", {"user_id": user_id})
    return [Note(**note) for note in note_dicts]
