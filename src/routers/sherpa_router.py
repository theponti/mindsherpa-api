import base64
import os
import tempfile
from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, StringConstraints, ValidationError

from src.data.focus_repository import create_focus_items
from src.data.models.focus import Focus, FocusItem, FocusItemBaseV2, FocusState
from src.routers.user_intent.user_intent_service import (
    GeneratedIntentsResponse,
    generate_intent_result,
    get_user_intent,
)
from src.services.openai_service import openai_client
from src.utils.context import CurrentProfile, SessionDep
from src.utils.logger import logger

sherpa_router = APIRouter()


class FocusOutput(BaseModel):
    items: List[FocusItem]


@sherpa_router.get("/focus")
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


class CreateFocusItemsPayload(BaseModel):
    content: Annotated[str, StringConstraints(min_length=1)]


@sherpa_router.post("/text")
async def handle_text_input_route(
    profile: CurrentProfile, input: CreateFocusItemsPayload
) -> GeneratedIntentsResponse:
    try:
        intent = get_user_intent(input.content, profile_id=profile.id)
        result = generate_intent_result(intent)

        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(e)
        logger.error(f"Error creating focus items: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


class AudioUpload(BaseModel):
    filename: str
    """The name of the audio file to be uploaded."""
    audio_data: str
    """The base64 encoded audio data."""


@sherpa_router.post("/voice")
async def handle_audio_upload_route(audio: AudioUpload, profile: CurrentProfile) -> GeneratedIntentsResponse:
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

        intent = get_user_intent(str(transcription), profile_id=profile.id)
        result = generate_intent_result(intent)

        return result

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


class CreateFocusItemBaseV2(BaseModel):
    items: List[FocusItemBaseV2]


@sherpa_router.post("/focus")
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


@sherpa_router.delete("/focus/{id}")
async def delete_focus_item_route(id: int, db: SessionDep, profile: CurrentProfile) -> bool:
    note = db.query(Focus).filter(Focus.id == id).first()
    if not note:
        return False

    db.delete(note)
    db.commit()
    return True
