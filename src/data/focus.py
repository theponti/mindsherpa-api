import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.data.db import SessionLocal
from src.data.models.focus import Focus, FocusItemBase, FocusItemBaseV2, FocusState


def create_focus_items(
    focus_items: List[FocusItemBaseV2] | List[FocusItemBase], profile_id: uuid.UUID, session: Session
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


def search_focus_items(
    keyword: str,
    due_on: Optional[datetime],
    due_after: Optional[datetime],
    due_before: Optional[datetime],
    status: Optional[FocusState],
) -> List[Focus]:
    session = SessionLocal()
    try:
        query = session.query(Focus).filter(
            Focus.text.contains(keyword)
            & (
                (Focus.due_date == due_on)
                if due_on is not None
                else ((Focus.due_date >= due_after) if due_after is not None else True)
            )
            & (Focus.due_date <= due_before if due_before is not None else True)
        )

        if status == "active" or status == "backlog":
            query = query.filter(Focus.state.in_([FocusState.backlog.value, FocusState.active.value]))
        elif status:
            query = query.filter(Focus.state == status.value)

        query = query.all()
        return query
    except Exception as e:
        print(f"Error searching focus items: {e}")
        return []
