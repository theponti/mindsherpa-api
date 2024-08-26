import base64
import datetime
import os
import tempfile
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.data.models.focus import FocusItem
from src.services.focus import create_focus_items, create_note
from src.services.openai_service import openai_client
from src.services.sherpa import process_user_input
from src.types.llm_output_types import LLMFocusItem
from src.utils.logger import logger

notes_router = APIRouter()


class CreateNoteInput(BaseModel):
    content: str


class CreateNoteOutput(BaseModel):
    id: UUID
    content: str
    created_at: datetime.datetime
    focus_items: List[LLMFocusItem]


@notes_router.post("/text")
async def create_text_note_route(
    input: CreateNoteInput, request: Request
) -> CreateNoteOutput | bool:
    profile_id = request.state.profile.id
    try:
        note = create_note(request.state.session, input.content, profile_id)
        if not note:
            return False

        focus_items = process_user_input(user_input=note.content)

        return CreateNoteOutput(
            id=note.id,
            content=note.content,
            created_at=note.created_at,
            focus_items=focus_items.items,
        )
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        return False


class AudioUpload(BaseModel):
    filename: str
    audio_data: str


@notes_router.post("/voice")
async def upload_voice_note(
    audio: AudioUpload, request: Request
) -> CreateNoteOutput | bool:
    profile_id = request.state.profile.id

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
        note = create_note(request.state.session, formatted_transcription, profile_id)
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
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {error_message}"
            )


class CreateFocusItemInput(BaseModel):
    items: List[LLMFocusItem]


@notes_router.post("/focus")
async def create_focus_item_route(
    request: Request, input: CreateFocusItemInput
) -> List[FocusItem] | bool:
    created_items = create_focus_items(
        focus_items=input.items,
        profile_id=request.state.profile.id,
        session=request.state.session,
    )

    return [FocusItem(**item.to_json()) for item in created_items]
