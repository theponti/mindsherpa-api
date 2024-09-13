import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma

from src.services.openai_service import openai_embeddings
from src.utils.config import settings

chroma_client = None

if settings.ENVIRONMENT != "test" and not settings.CI:
    chroma_client = chromadb.Client(
        settings=Settings(
            chroma_client_auth_provider=settings.CHROMA_SERVER_AUTHN_PROVIDER,
            chroma_client_auth_credentials=settings.CHROMA_SERVER_AUTHN_CREDENTIALS,
        ),
    )

    chroma_client.heartbeat()  # this should work with or without authentication - it is a public endpoint
    chroma_client.get_version()  # this should work with or without authentication - it is a public endpoint
    chroma_client.list_collections()  # this is a protected endpoint and requires authentication


if chroma_client:
    vector_store = Chroma(
        client=chroma_client,
        collection_name="focus",
        embedding_function=openai_embeddings,
    )
else:
    vector_store = Chroma(
        collection_name="focus",
        embedding_function=openai_embeddings,
        persist_directory=".chroma",
    )
