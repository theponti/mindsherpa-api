from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse

from src.data.db import Session
from src.utils.logger import logger
from src.services.sherpa import generate_user_context
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


@ai_router.get("/test")
def test():
    test_user_input = get_file_contents("src/prompts/test_user_input.md")
    analysis = generate_user_context(test_user_input, session=Session())
    return {"analysis": analysis}
