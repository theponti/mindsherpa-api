import traceback
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Request

from src.services import chroma_service
from src.services.file_service import get_file_contents
from src.services.keywords.keywords_service import get_query_keywords
from src.services.user_intent.user_intent_service import (
    GeneratedIntentsResponse,
    generate_intent_result,
    get_user_intent,
)
from src.utils.config import settings

admin_router = APIRouter()


def depends_on_development():
    if settings.ENVIRONMENT != "local":
        raise ValueError("This endpoint is only available in local development")
    return True


@admin_router.post("/sherpa/keyword-generator")
def sherpa_keyword_generator(
    request: Request,
    task_description: str = Form(...),
    dev_env=Depends(depends_on_development),
):
    return get_query_keywords(task_description)


@admin_router.post("/sherpa/intent")
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
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@admin_router.post("/sherpa/intent/formatted")
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


@admin_router.get("/sherpa/vector_search/{id}")
def get_vector_document_by_id(
    request: Request,
    dev_env=Depends(depends_on_development),
):
    return chroma_service.vector_store.get(ids=[request.path_params["id"]])


@admin_router.post("/sherpa/vector_search")
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
