from fastapi import APIRouter, Depends, UploadFile

from src.utils.ai_models import groq_whisper_large_v3
from src.services.groq_service import groq_client
from src.services.openai_service import openai_client
from src.schema import User, get_current_user


media_router = APIRouter(prefix="/media")


@media_router.post("/audio/transcribe")
def transcribe_audio(
    audio_file: UploadFile,
    model: str = "openai-whisper-1",
    current_user: User = Depends(get_current_user),
):
    """
    Transcribes audio using either OpenAI's whisper or Groq's Whisper API.
    NOTE : OPenAI's transcription is faster as Groq uses whisper large v3 model which is not required at the moment
    """
    file = audio_file.file.read()

    if model == groq_whisper_large_v3:
        transcription = groq_client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3",
            prompt="",
            response_format="json",
            language="en",
            temperature=0.0,
        )

    elif model == "openai-whisper-1":
        # OPENAI Transcription
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1", file=file
        )

    else:
        print("Choose an appropriate transcription model")
        return None

    results = transcription.text

    return results
