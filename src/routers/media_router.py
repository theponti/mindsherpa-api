import io
from fastapi import APIRouter, Depends, UploadFile

from src.utils.ai_models import audio_models
from src.services.auth import get_current_user
from src.services.groq_service import groq_client
from src.services.media import transcribe_audio
from src.services.openai_service import openai_client
from src.services.sherpa_service import analyze_user_input
from src.schemas.query import User


media_router = APIRouter()


@media_router.post("/audio/transcribe")
def transcription_route(
    audio_file: UploadFile,
    model: str = "openai",
    current_user: User = Depends(get_current_user),
):
    """
    Transcribes audio using either OpenAI's whisper or Groq's Whisper API.
    NOTE : OPenAI's transcription is faster as Groq uses whisper large v3 model which is not required at the moment
    """
    file = audio_file.file.read()
    buffer = io.BytesIO(file)
    transcription = transcribe_audio(buffer, model)
    buffer.name = "audio.m4a"

    if model == "groq":
        transcription = groq_client.audio.transcriptions.create(
            file=buffer,
            model=audio_models[model],
            prompt="",
            response_format="json",
            language="en",
            temperature=0.0,
        )

    elif model == "openai":

        transcription = openai_client.audio.transcriptions.create(
            model=audio_models[model], file=buffer
        )

    else:
        return {"error": "Choose an appropriate transcription model"}

    results = transcription.text
    analysis = analyze_user_input(results)
    return {"text": results, "analysis": analysis}
