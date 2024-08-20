from typing import List

from sqlalchemy.orm import Session

from src.data.models.focus import Focus
from src.data.models.note import Note
from src.services.sherpa import process_user_input

def create_focus_from_text(text: str, profile_id: str, session: Session) -> List[Focus]:
    try:
        focus_items = process_user_input(user_input=text)
        if focus_items:
            created_items = [
                Focus(
                    text=item.text,
                    type=item.type,
                    task_size=item.task_size,
                    category=item.category,
                    priority=item.priority,
                    sentiment=item.sentiment,
                    due_date=item.due_date,
                    profile_id=profile_id,
                )
                for item in focus_items.items
            ]
            session.bulk_save_objects(created_items, return_defaults=True)
            session.commit()
            return created_items
        return []
    except Exception as e:
        print(f"Error creating focus items: {e}")
        return []

def create_note(session: Session, content: str, profile_id: str) -> Note | None:
    try:
        note = Note(content=content, profile_id=profile_id)
        session.add(note)
        session.commit()
        return note
    except Exception as e:
        print(f"Error creating note: {e}")
        return None

def get_user_notes(session: Session, profile_id: str) -> List[Note]:
    return session.query(Note).filter(Note.profile_id == profile_id).all()