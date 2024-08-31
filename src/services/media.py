import io
from dataclasses import dataclass
from typing import Optional

from src.services.groq_service import groq_client
from src.services.openai_service import openai_client
from src.utils.ai_models import audio_models


@dataclass
class TranscribeAudioResponse:
    text: Optional[str]
    error: Optional[str]


def transcribe_audio(audio_buffer: io.BytesIO, model: str) -> TranscribeAudioResponse:
    """
    Transcribes audio using either OpenAI's whisper or Groq's Whisper API.
    NOTE : OPenAI's transcription is faster as Groq uses whisper large v3 model which is not required at the moment
    """
    audio_buffer.name = "audio.m4a"

    if model == "groq":
        transcription = groq_client.audio.transcriptions.create(
            file=audio_buffer,
            model=audio_models[model],
            prompt="",
            response_format="json",
            language="en",
            temperature=0.0,
        )

    elif model == "openai":
        transcription = openai_client.audio.transcriptions.create(
            model=audio_models[model], file=audio_buffer
        )

    else:
        return TranscribeAudioResponse(error="Choose an appropriate transcription model", text=None)

    results = transcription.text

    return TranscribeAudioResponse(text=results, error=None)
