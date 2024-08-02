from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from src.services.sherpa_service import analyze_user_input

from src.utils.logger import logger
from src.services.file_service import get_file_contents
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


@ai_router.post("/focus")
def focus(transcript: str, model: str = "llama3-70b-8192"):
    """
    Returns notes structure content as well as total tokens and total time for generation.
    """
    if not transcript.strip():
        return None, {"error": "No tasks provided in the transcript"}

    try:
        analysis = analyze_user_input(transcript)
        return {"analysis": analysis}
    except Exception as e:
        logger.error(f" ********* ERROR IN USER PROMPT ********: {e} ***** ")
        return None, {"error": str(e)}


@ai_router.get("/test")
def test():
    test_user_input = get_file_contents("src/prompts/test_user_input.md")
    analysis = analyze_user_input(test_user_input)
    return {"analysis": analysis}
