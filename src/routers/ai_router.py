from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse

from src.services.file_service import get_file_contents
from src.services.openai_service import openai_async_client
from src.services.sherpa import process_user_input
from src.types.llm_output_types import LLMFocusOutput
from src.utils.config import settings
from src.utils.logger import logger

ai_router = APIRouter()


def depends_on_development():
    if settings.ENVIRONMENT != "local":
        raise ValueError("This endpoint is only available in local development")
    return True


@ai_router.post("/chat", response_model=LLMFocusOutput)
async def chat(message: str = Form(...), dev_env=Depends(depends_on_development)) -> LLMFocusOutput:
    llm_response = process_user_input(message)
    return llm_response


@ai_router.post("/chat/stream")
async def stream_chat(message: str = Form(...), dev_env=Depends(depends_on_development)):
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


@ai_router.post("/sherpa/focus")
def sherpa_focus_item(input: str = Form(...), dev_env=Depends(depends_on_development)):
    completion = process_user_input(input)
    return completion


@ai_router.get("/test")
def test(dev_env=Depends(depends_on_development)):
    test_user_input = get_file_contents("src/prompts/test_user_input.md")
    completion = process_user_input(test_user_input)
    return {"analysis": completion}
