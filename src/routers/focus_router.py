from typing import Optional

import pytz
from fastapi import APIRouter, Query, status
from fastapi.exceptions import HTTPException

from src.data.models.focus import (
    Focus,
    FocusState,
    complete_focus,
    get_focus_by_id,
)
from src.utils.context import CurrentProfile, SessionDep
from src.utils.date_tools import get_end_of_day, get_start_of_day
from src.utils.logger import logger

focus_router = APIRouter()


@focus_router.get("")
async def get_focus_items(
    profile: CurrentProfile,
    db: SessionDep,
    category: Optional[str] = None,
    timezone: str = Query(default="UTC", description="Timezone to use for date filtering"),
    start_date: Optional[str] = Query(default=None, description="Start date for date filtering"),
    end_date: Optional[str] = Query(default=None, description="End date for date filtering"),
):
    query = db.query(Focus).filter(
        Focus.profile_id == profile.id,
        Focus.state.notin_(
            [
                FocusState.completed.value,
            ]
        ),
    )

    # Apply category filter if provided
    if category:
        query = query.filter(Focus.category == category)

    # Get start and end of today in the client's timezone
    client_tz = pytz.timezone(timezone)
    start_of_today = get_start_of_day(client_tz)
    end_of_today = get_end_of_day(client_tz)

    # Convert to UTC for database query
    start_of_today_utc = start_of_today.astimezone(pytz.UTC)
    end_of_today_utc = end_of_today.astimezone(pytz.UTC)

    # Apply due date filter
    query = query.filter(Focus.due_date >= start_of_today_utc).filter(Focus.due_date <= end_of_today_utc)

    # Apply ordering
    query = query.order_by(Focus.due_date.asc())

    # Execute query
    focus_items = query.all()

    return {"items": focus_items}


@focus_router.put("/complete/{task_id}", status_code=status.HTTP_200_OK)
async def complete_task(db: SessionDep, task_id: int):
    focus_item = get_focus_by_id(db, task_id)
    if not focus_item:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        focus_item = complete_focus(db, focus_item.id)
        return focus_item.to_json()
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Error updating task")


@focus_router.delete("/{id}")
async def delete_focus_item_route(id: int, db: SessionDep, profile: CurrentProfile) -> bool:
    note = db.query(Focus).filter(Focus.id == id).first()
    if not note:
        return False

    db.delete(note)
    db.commit()
    return True
