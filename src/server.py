from fastapi import FastAPI, status
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from src.crons import scheduler
from src.crons.add_focus_to_chroma import add_focus_to_vector_store_job
from src.routers.ai_router import ai_router
from src.routers.chat_router import chat_router
from src.routers.sherpa_router import sherpa_router
from src.routers.tasks import task_router
from src.routers.user_router import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the scheduler in a separate thread to avoid blocking the main thread
    print("Starting scheduler")
    scheduler.start()
    scheduler.add_job(add_focus_to_vector_store_job, "interval", minutes=1)
    # scheduler_thread = threading.Thread(target=start_scheduler)
    # scheduler_thread.start()
    yield
    scheduler.shutdown()


# Create FastAPI app
app = FastAPI(lifespan=lifespan)

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
app.include_router(sherpa_router, prefix="/notes")
app.include_router(task_router, prefix="/tasks")
app.include_router(chat_router, prefix="/chat")
app.include_router(user_router, prefix="/user")


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request, exc):
    content = {
        "detail": exc.errors(),
    }
    print(content)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):
    content = {
        "detail": exc.errors(),
    }
    print(content)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content)


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
