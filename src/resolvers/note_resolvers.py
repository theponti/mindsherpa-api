import io
import strawberry
from sqlalchemy.orm import Session
from strawberry.file_uploads import Upload

from src.data.models import Note, Focus
from src.services.media import transcribe_audio, TranscribeAudioResponse
from src.services.sherpa import get_focus_items_from_text
from src.utils.logger import logger

@strawberry.input
class CreateNoteInput:
    content: str

@strawberry.type
class CreateNoteOutput:
    id: str
    content: str
    created_at: str

async def create_note(info: strawberry.Info, input: CreateNoteInput) -> CreateNoteOutput:
    if not info.context.get("user"):
        raise Exception("Unauthorized")

    session: Session = info.context.get("session")
    profile_id = info.context.get("profile").id

    note = Note(content=input.content, profile_id=profile_id)
    session.add(note)
    session.commit()

    focus_items = get_focus_items_from_text(text=input.content)
    if not focus_items:
        return False

    created_items = [
        Focus(
            text=item["text"],
            type=item["type"],
            task_size=item["task_size"],
            category=item["category"],
            priority=item["priority"],
            sentiment=item["sentiment"],
            due_date=item["due_date"],
            profile_id=profile_id,
        )
        for item in focus_items
    ]
    session.bulk_save_objects(created_items)
    session.commit()

    return CreateNoteOutput(id=note.id, content=note.content, created_at=note.created_at)


@strawberry.type
class UploadVoiceNoteResponse(TranscribeAudioResponse):
    pass

async def upload_voice_note(
        self, info: strawberry.Info, audio_file: Upload, chat_id: int
    ) -> UploadVoiceNoteResponse:
        current_user = info.context.get("user")
        if not current_user:
            raise Exception("Unauthorized")

        transcription = transcribe_audio(io.BytesIO(audio_file), model="openai")
        if transcription.error or not transcription.text:
            raise Exception("Transcription failed")

        logger.info(f"Transcription: {transcription.text}")
        return UploadVoiceNoteResponse(text=transcription.text, error=None)


