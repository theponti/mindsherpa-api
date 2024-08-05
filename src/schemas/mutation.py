import io
import strawberry
from strawberry.file_uploads import Upload
from typing import List

from src.schemas.types import Message
from src.services.sherpa_service import insert_message, get_sherpa_response
from src.services.media import transcribe_audio, TranscribeAudioResponse
from src.utils.logger import logger


@strawberry.type
class UploadVoiceNoteResponse(TranscribeAudioResponse):
    pass


@strawberry.type
class Mutation:
    @strawberry.field
    async def upload_voice_note(
        self, info: strawberry.Info, audio_file: Upload, chat_id: int
    ) -> UploadVoiceNoteResponse:
        current_user = info.context.get("current_user")
        if not current_user:
            raise Exception("Unauthorized")

        transcription = transcribe_audio(io.BytesIO(audio_file), model="openai")
        if transcription.error or not transcription.text:
            raise Exception("Transcription failed")

        logger.info(f"Transcription: {transcription.text}")
        return UploadVoiceNoteResponse(text=transcription.text, error=None)

    @strawberry.field
    async def send_chat_message(
        self, info: strawberry.Info, chat_id: int, message: str
    ) -> List[Message]:
        current_user = info.context.get("current_user")
        if not current_user:
            raise Exception("Unauthorized")

        # Insert new message into the database
        user_message = insert_message(chat_id, message, current_user.id, "user")

        # Retrieve message from ChatGPT
        sherpa_response = get_sherpa_response(message, chat_id, current_user.id)
        if sherpa_response is None:
            raise Exception("No response from the model")

        # Save system response to the database
        system_message = insert_message(
            chat_id=chat_id,
            user_id=current_user.id,
            role="assistant",
            message=sherpa_response,
        )

        return [
            user_message,
            system_message,
        ]
