import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma

from src.services.openai_service import openai_embeddings
from src.utils.config import settings

chroma_client = None

if settings.ENVIRONMENT != "test" and not settings.CI:
    chroma_client = chromadb.HttpClient(
        host=settings.CHROMA_SERVER_HOST,
        port=settings.CHROMA_SERVER_HTTP_PORT,
        settings=Settings(
            chroma_server_host=settings.CHROMA_SERVER_HOST,
            chroma_server_http_port=settings.CHROMA_SERVER_HTTP_PORT,
            chroma_client_auth_provider=settings.CHROMA_SERVER_AUTHN_PROVIDER,
            chroma_client_auth_credentials=settings.CHROMA_SERVER_AUTHN_CREDENTIALS,
            chroma_auth_token_transport_header=settings.CHROMA_AUTH_TOKEN_TRANSPORT_HEADER,
        ),
    )

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
