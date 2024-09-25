import traceback
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status

from src.services import chroma_service
from src.services.file_service import get_file_contents
from src.services.keywords.keywords_service import get_query_keywords
from src.services.user_intent.user_intent_service import (
    generate_intent_result,
    get_user_intent,
)
from src.utils.config import settings

admin_router = APIRouter()


def admin_route(request: Request):
    if settings.ENVIRONMENT != "local":
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        auth_token = auth_header.split(" ")[1]
        if settings.ADMIN_TOKEN != auth_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return True


@admin_router.post("/keyword-generator")
def sherpa_keyword_generator(
    request: Request,
    task_description: str = Form(...),
    admin=Depends(admin_route),
):
    return get_query_keywords(task_description)


@admin_router.post("/intent")
def sherpa_user_intent(
    request: Request,
    input: str = Form(...),
    formatted: bool = Form(False),
    profile_id: uuid.UUID = Form(...),
    admin=Depends(admin_route),
):
    content = input
    if request.query_params.get("test"):
        content = get_file_contents("src/prompts/test_user_input.md")

    try:
        intents = get_user_intent(content, profile_id=profile_id)

        if formatted:
            result = generate_intent_result(intents)
            return result

        return intents
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@admin_router.post("/vector_search/collections", dependencies=[Depends(admin_route)])
def get_vector_collections(
    admin=Depends(admin_route),
    id: str = Form(None),
):
    collection = chroma_service.chroma_client.get_collection(name="focus")
    if not collection:
        return HTTPException(status_code=404, detail="Collection not found")

    return collection.get(ids=[id])


@admin_router.post("/vector_search")
def sherpa_vector_search(
    request: Request,
    query: str = Form(...),
    threshold: float = Form(None),
    profile_id: uuid.UUID = Form(...),
    admin=Depends(admin_route),
):
    return chroma_service.vector_store.similarity_search_with_relevance_scores(
        query=query,
        filter={"profile_id": str(profile_id)},
        score_threshold=threshold,
    )


@admin_router.get("/vector_search/{id}")
def get_vector_document_by_id(
    request: Request,
    admin=Depends(admin_route),
):
    return chroma_service.vector_store.get(ids=[request.path_params["id"]])
