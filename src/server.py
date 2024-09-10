from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.routers.ai_router import ai_router
from src.routers.chat import chat_router
from src.routers.graphql import graphql_router
from src.routers.notes import notes_router
from src.routers.tasks import task_router
from src.routers.user_intent import UserIntentRouter
from src.routers.user_router import user_router

# Create FastAPI app
app = FastAPI()

# Allow CORS for all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ai_router)
app.include_router(graphql_router, prefix="/graphql")
app.include_router(notes_router, prefix="/notes")
app.include_router(task_router, prefix="/tasks")
app.include_router(chat_router, prefix="/chat")
app.include_router(UserIntentRouter)
app.include_router(user_router, prefix="/user")


# Root
@app.get("/")
async def root():
    return {"message": "Hello World"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Mindsherpa API",
        version="0.0.1",
        summary="Mindsherpa API",
        description="Mindsherpa API",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
