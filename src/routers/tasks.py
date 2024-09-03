from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from src.data.models.focus import complete_focus, get_focus_by_id
from src.utils.context import SessionDep
from src.utils.logger import logger

task_router = APIRouter()


@task_router.put("/complete/{task_id}", status_code=status.HTTP_200_OK)
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
