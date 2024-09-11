import base64
import os
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.data.focus import create_focus_items
from src.data.models.focus import Focus, FocusItem, FocusItemBase, FocusState
from src.data.notes import create_note
from src.services.openai_service import openai_client
from src.services.sherpa import process_user_input
from src.utils.context import CurrentProfile, SessionDep
from src.utils.logger import logger

notes_router = APIRouter()


class FocusOutput(BaseModel):
    items: List[FocusItem]


@notes_router.get("/focus")
async def get_focus_items(profile: CurrentProfile, db: SessionDep, category: Optional[str] = None):
    """
    Returns notes structure content as well as total tokens and total time for generation.
    """
    profile_id = profile.id

    query = db.query(Focus).filter(
        Focus.profile_id == profile_id, Focus.state.notin_([FocusState.completed.value])
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


class CreateFocusItemsPayload(BaseModel):
    content: str


class CreateFocusItemsResponse(BaseModel):
    items: List[Dict[str, Any]]


@notes_router.post("/text")
async def create_focus_items_from_text_route(profile: CurrentProfile, input: CreateFocusItemsPayload):
    try:
        focus_items = process_user_input(user_input=input.content)
        return focus_items
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(e)
        logger.error(f"Error creating focus items: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


class AudioUpload(BaseModel):
    filename: str
    audio_data: str


@notes_router.post("/voice")
async def upload_voice_note(audio: AudioUpload, db: SessionDep, profile: CurrentProfile):
    profile_id = profile.id

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, "temp_audio.m4a")
            # Decode the base64 audio data
            audio_bytes = base64.b64decode(audio.audio_data)

            with open(temp_file_path, "wb") as dst:
                dst.write(audio_bytes)

            with open(temp_file_path, "rb") as audio_file:
                transcription = openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, response_format="text"
                )

        formatted_transcription = str(transcription)
        note = create_note(db, formatted_transcription, profile_id)
        if not note:
            return False

        focus_items = process_user_input(user_input=formatted_transcription)

        return CreateNoteOutput(
            id=note.id,
            content=note.content,
            created_at=note.created_at,
            focus_items=focus_items.items,
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error transcribing audio: {error_message}")

        if "invalid_request_error" in error_message:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Please ensure you're uploading a supported audio file. Error: {error_message}",
            )
        elif "file_size" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail=f"File size error. Please ensure your audio file is within the size limit. Error: {error_message}",
            )
        else:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {error_message}")


class CreateFocusItemInput(BaseModel):
    items: List[FocusItemBase]


@notes_router.post("/focus")
async def create_focus_item_route(
    input: CreateFocusItemInput, db: SessionDep, profile: CurrentProfile
) -> List[FocusItem] | bool:
    created_items = create_focus_items(
        focus_items=input.items,
        profile_id=profile.id,
        session=db,
    )

    return [
        FocusItem(
            id=item.id,
            text=item.text,
            type=item.type,
            task_size=item.task_size,
            category=item.category,
            priority=item.priority,
            profile_id=item.profile_id,
            sentiment=item.sentiment,
            state=item.state,
            due_date=item.due_date,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in created_items
    ]


@notes_router.delete("/focus/{id}")
async def delete_focus_item_route(id: int, db: SessionDep, profile: CurrentProfile) -> bool:
    note = db.query(Focus).filter(Focus.id == id).first()
    if not note:
        return False

    db.delete(note)
    db.commit()
    return True
