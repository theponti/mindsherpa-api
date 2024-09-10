from typing import Annotated

from fastapi import APIRouter, Form

from src.routers.user_intent.user_intent_service import get_user_intent

user_intent_router = APIRouter(prefix="/api/user_intent")


@user_intent_router.post("/")
def get_user_intent_route(user_input: Annotated[str, Form()]):
    return get_user_intent(user_input)
