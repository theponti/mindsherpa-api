import json
from fastapi import APIRouter, Form, UploadFile, Depends
from fastapi.responses import StreamingResponse
import groq
import os
from openai import AsyncOpenAI, OpenAI

from src.logger import logger
from src.helpers.generation_statistics import GenerationStatistics
from src.schema import User, get_current_user
from src.services.file_service import get_file_contents

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

openai_client = OpenAI(api_key=OPENAI_API_KEY)
openai_async_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
groq_client = groq.Groq()

llama3_70b_8192 = "llama3-70b-8192"
llama3_8b_8192 = "llama3-8b-8192"
mixtral_8x7b_32768 = "mixtral-8x7b-32768"
gemma_7b_it = "gemma-7b-it"
gemma2_9b_it = "gemma2-9b-it"
groq_whisper_large_v3 = "groq-whisper-large-v3"

open_source_models = [
    llama3_70b_8192,
    llama3_8b_8192,
    mixtral_8x7b_32768,
    gemma_7b_it,
]


content_model_options = [model for model in open_source_models]
content_model_options.append(gemma2_9b_it)

router = APIRouter()


@router.post("/transcribe_audio")
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


@router.post("/chat/stream")
async def stream_chat(message: str = Form(...)):
    async def generate():
        stream = await openai_async_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                logger.info(f" -- CHUNK -- {chunk.choices[0].delta.content} ")
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/event-stream")


def get_user_prompt(transcript: str):
    json_example = json.dumps(
        {
            "Today's Tasks": [
                {
                    "content": "Finish the project report",
                    "datetime": "2024-05-15T15:30:00",
                    "type": "task",
                },
                {
                    "content": "Buy groceries",
                    "datetime": "2024-05-15T15:30:00",
                    "type": "task",
                },
                {
                    "content": "Call the plumber to fix the sink",
                    "datetime": "2024-05-15T15:30:00",
                    "type": "task",
                },
                {
                    "content": "Leave for the airport by 3:30 PM to ensure enough time for check-in and security",
                    "datetime": "2024-05-15T15:30:00",
                    "type": "task",
                },
            ],
            "Future Tasks": [
                {
                    "content": "Schedule my dentist appointment for next month",
                    "datetime": "2024-06-15T15:30:00",
                    "type": "task",
                },
                {
                    "content": "Plan a birthday party for my sister in two weeks",
                    "datetime": "2024-06-15T15:30:00",
                    "type": "task",
                },
            ],
            "Feelings": [
                {
                    "content": "I am feeling a bit tired probably because I overworked yesterday but yeah I need to go back to work anyhow",
                    "datetime": "2024-05-15T15:30:00",
                    "type": "feeling",
                },
            ],
        },
        indent=2,
    )
    user_prompt = get_file_contents("src/prompts/sherpa_user_input_formatter.md")
    return user_prompt.format(json_example=json_example, user_input=transcript)


@router.post("/generate_notes_structure")
def generate_notes_structure(transcript: str, model: str = "llama3-70b-8192"):
    """
    Returns notes structure content as well as total tokens and total time for generation.
    """
    system_prompt = get_file_contents("src/prompts/sherpa_base.md")
    user_prompt = get_file_contents("src/prompts/sherpa_user_input_formatter.md")
    if not transcript.strip():
        return None, {"error": "No tasks provided in the transcript"}

    try:
        user_prompt = get_user_prompt(transcript)
    except Exception as e:
        logger.error(f" ********* ERROR IN USER PROMPT ********: {e} ***** ")
        return None, {"error": str(e)}

    if model in open_source_models:

        try:
            completion = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"{user_prompt}\n\n### User Input:\n\n{transcript}",
                        # This should be the actual paragraph from which tasks need to be extracted
                    },
                ],
                temperature=0.3,
                max_tokens=8000,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None,
            )

            usage = completion.usage
            # print("------ USAGE ---", usage)

        except Exception as e:
            logger.error(f" ********* API error ********: {e} ***** ")
            return None, {"error": str(e)}

        try:
            if usage:
                statistics_to_return = GenerationStatistics(
                    input_time=int(usage.prompt_time) if usage.prompt_time else 0,
                    output_time=(
                        int(usage.completion_time) if usage.completion_time else 0
                    ),
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens,
                    total_time=int(usage.total_time) if usage.total_time else 0,
                    model_name=model,
                )
                logger.info(f" -- STATS -- {statistics_to_return} ")
                # print("-- Content --", completion.choices[0].message.content)
                return (
                    json.loads(completion.choices[0].message.content)
                    if completion.choices[0].message.content
                    else None
                )
        except Exception as e:
            logger.error(f" ********* STATISTICS GENERATION error ******* : {e} ")
            return None, {"error": str(e)}
