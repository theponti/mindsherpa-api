from fastapi import APIRouter, Request, status
from fastapi.exceptions import HTTPException
from fastapi.params import Path
from sqlalchemy.orm.session import Session

from src.data.db import get_db_dependency
from src.data.models.focus import Focus, FocusState, complete_focus, get_focus_by_id
from src.utils.logger import logger


task_router = APIRouter()


@task_router.put("/complete/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(request: Request, task_id: int):
    session: Session = request.state.session
    focus_item = get_focus_by_id(session, task_id)
    if not focus_item:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        focus_item = complete_focus(session, focus_item.id)
        return focus_item.to_json()
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Error updating task")
