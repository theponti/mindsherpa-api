from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer


from dotenv import load_dotenv

load_dotenv()

from src.groq import router as ai_router
from src.routers.graphql import graphql_router

app = FastAPI()

# Allow CORS for all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(ai_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(graphql_router, prefix="/graphql")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
