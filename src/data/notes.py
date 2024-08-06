from typing import List
from sqlalchemy.orm import Session

from src.data.models import Note


def get_user_notes(session: Session, profile_id: str) -> List[Note]:
    notes = session.query(Note).filter(Note.profile_id == profile_id).all()

    return notes
