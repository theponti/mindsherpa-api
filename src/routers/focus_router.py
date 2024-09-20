from typing import List, Optional

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, ValidationError

from src.data.focus_repository import create_focus_items
from src.data.models.focus import (
    Focus,
    FocusItem,
    FocusItemBaseV2,
    FocusState,
    complete_focus,
    get_focus_by_id,
)
from src.utils.context import CurrentProfile, SessionDep
from src.utils.logger import logger

focus_router = APIRouter()


@focus_router.get("")
async def get_focus_items(profile: CurrentProfile, db: SessionDep, category: Optional[str] = None):
    """
    Returns notes structure content as well as total tokens and total time for generation.
    """
    profile_id = profile.id

    query = db.query(Focus).filter(
        Focus.profile_id == profile_id,
        Focus.state.notin_(
            [
                FocusState.completed.value,
            ]
        ),
    )

    # Apply category filter if provided
    if category:
        query = query.filter(Focus.category == category)

    # Apply due date filter
    # query = query.filter(or_(Focus.due_date <= get_end_of_today(), Focus.due_date.is_(None)))

    # Apply ordering
    query = query.order_by(Focus.due_date.desc())

    # Execute query
    focus_items = query.all()

    return {"items": focus_items}


class CreateFocusItemBaseV2(BaseModel):
    items: List[FocusItemBaseV2]


@focus_router.post("")
async def create_focus_item_route(
    input: CreateFocusItemBaseV2, db: SessionDep, profile: CurrentProfile
) -> List[FocusItem]:
    try:
        created_items = create_focus_items(
            focus_items=input.items,
            profile_id=profile.id,
            session=db,
        )

        return [item.to_model() for item in created_items]
    except Exception as e:
        if isinstance(e, ValidationError):
            print(e.errors())
            raise HTTPException(status_code=422, detail=e.errors())
        else:
            raise HTTPException(status_code=500, detail=str(e))


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
