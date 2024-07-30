import json
from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse

from src.utils.ai_models import open_source_models
from src.utils.logger import logger
from src.utils.generation_statistics import GenerationStatistics
from src.services.file_service import get_file_contents
from src.services.groq_service import groq_client
from src.services.openai_service import openai_async_client

ai_router = APIRouter()


@ai_router.post("/chat")
async def chat(message: str = Form(...)):
    response = await openai_async_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
        stream=False,
    )
    return {"text": response.choices[0].message.content}


@ai_router.post("/chat/stream")
async def stream_chat(message: str = Form(...)):
    async def generate():
        stream = await openai_async_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                logger.info(f" -- CHUNK -- {content} ")
                yield content

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


@ai_router.post("/generate_notes_structure")
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
