import uuid
from typing import List

from sqlalchemy.orm import Session

from src.data.models.focus import Focus, FocusItemBase


def create_focus_items(
    focus_items: List[FocusItemBase], profile_id: uuid.UUID, session: Session
) -> List[Focus]:
    try:
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
            for item in focus_items
        ]
        session.add_all(created_items)
        session.flush()
        session.commit()
        return created_items
    except Exception as e:
        print(f"Error creating focus items: {e}")
        return []
