import os
from fastapi import UploadFile
import strawberry
from sqlalchemy.orm import Session
from strawberry.file_uploads import Upload
import tempfile

from src.data.models import Note, Focus
from src.services.media import TranscribeAudioResponse
from src.services.openai_service import openai_client
from src.services.sherpa import process_user_input
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

    focus_items = process_user_input(user_input=input.content)
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


async def upload_voice_note(info: strawberry.Info, audio_file: Upload) -> UploadVoiceNoteResponse:
    current_user = info.context.get("user")
    if not current_user:
        raise Exception("Unauthorized")
    
    # 👇 Get transcription from OpenAI Whisper
    transcription_result = await upload_voice_note_v2(audio_file)

    if not transcription_result['success']:
        raise Exception(transcription_result['message'])

    logger.info(f"Transcription: {transcription_result['transcription']}")
    return UploadVoiceNoteResponse(text=transcription_result['transcription'], error=None)

async def upload_voice_note_v2(audio_file: Upload):
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary file with a .m4a extension (common for voice memos)
            temp_file_path = os.path.join(temp_dir, "temp_audio.m4a")
            
            
            # Save the uploaded file
            with open(temp_file_path, "wb") as dst:
                content = await audio_file.read()
                dst.write(content)
            
            # Print file information for debugging
            print(f"File saved as: {temp_file_path}")
            print(f"File size: {os.path.getsize(temp_file_path)} bytes")
            
            # Verify file content
            with open(temp_file_path, "rb") as f:
                content = f.read()
                print(f"File content (first 100 bytes): {content[:100]}")
            
            # Call the OpenAI API for transcription
            with open(temp_file_path, "rb") as audio_file:
                transcription = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
        # Process the transcription as needed
        # For example, you might want to save it to a database
        # ...

        return {"success": True, "message": "Audio transcribed successfully", "transcription": transcription}
    except Exception as e:
        error_message = str(e)
        print(f"Error transcribing audio: {error_message}")
        
        # Add more detailed error information
        if "invalid_request_error" in error_message:
            return {"success": False, "message": f"Invalid file format. Please ensure you're uploading a supported audio file. Error: {error_message}"}
        elif "file_size" in error_message.lower():
            return {"success": False, "message": f"File size error. Please ensure your audio file is within the size limit. Error: {error_message}"}
        else:
            return {"success": False, "message": f"An unexpected error occurred: {error_message}"}