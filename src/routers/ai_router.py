import traceback
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import StreamingResponse

from src.services import chroma_service
from src.services.file_service import get_file_contents
from src.services.openai_service import openai_async_client
from src.services.pinecone_service import euclidean_index, pc
from src.services.user_intent.user_intent_service import (
    GeneratedIntentsResponse,
    generate_intent_result,
    get_user_intent,
)
from src.utils.config import settings
from src.utils.logger import logger

ai_router = APIRouter()


def depends_on_development():
    if settings.ENVIRONMENT != "local":
        raise ValueError("This endpoint is only available in local development")
    return True


@ai_router.post("/chat")
async def chat(message: str = Form(...), dev_env=Depends(depends_on_development)):
    response = await openai_async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
        stream=False,
    )

    return response.choices[0].message.content


@ai_router.post("/chat/stream")
async def stream_chat(message: str = Form(...), dev_env=Depends(depends_on_development)):
    async def generate():
        stream = await openai_async_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                logger.info(f" -- CHUNK -- {content} ")
                yield content

    return StreamingResponse(generate(), media_type="text/event-stream")


@ai_router.post("/sherpa/intent")
def sherpa_user_intent(
    request: Request,
    input: str = Form(...),
    profile_id: uuid.UUID = Form(...),
    dev_env=Depends(depends_on_development),
):
    content = input
    if request.query_params.get("test"):
        content = get_file_contents("src/prompts/test_user_input.md")

    try:
        intents = get_user_intent(content, profile_id=profile_id)
        return intents
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@ai_router.post("/sherpa/intent/agent")
def sherpa_user_intent_agent(
    request: Request,
    input: str = Form(...),
    profile_id: uuid.UUID = Form(...),
    dev_env=Depends(depends_on_development),
) -> GeneratedIntentsResponse:
    content = input
    if request.query_params.get("test"):
        content = get_file_contents("src/prompts/test_user_input.md")

    try:
        intent = get_user_intent(content, profile_id=profile_id)
        result = generate_intent_result(intent)

        return result
    except Exception:  # pylint: disable=broad-except
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@ai_router.post("/sherpa/vector_search")
def sherpa_vector_search(
    request: Request,
    query: str = Form(...),
    threshold: float = Form(None),
    profile_id: uuid.UUID = Form(...),
    dev_env=Depends(depends_on_development),
):
    return chroma_service.vector_store.similarity_search_with_relevance_scores(
        query=query,
        filter={"profile_id": str(profile_id)},
        score_threshold=threshold,
    )


@ai_router.post("/sherpa/vector_search/pinecone")
def sherpa_vector_search_pinecone(
    request: Request,
    query: str = Form(...),
    threshold: float = Form(None),
    profile_id: uuid.UUID = Form(...),
    dev_env=Depends(depends_on_development),
):
    embedding = pc.inference.embed(
        model="multilingual-e5-large", inputs=[query], parameters={"input_type": "query"}
    )

    results = euclidean_index.query(
        namespace="ns1", vector=embedding[0].values, top_k=3, include_values=False, include_metadata=True
    )

    return {
        # "embedding": embedding[0].values,
        "results": [
            {"id": result["id"], "text": result["metadata"]["text"], "score": result["score"]}
            for result in results["matches"]
        ],
    }
