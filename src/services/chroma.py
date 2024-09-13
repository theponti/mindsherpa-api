import chromadb
from langchain_chroma import Chroma

from src.services.openai_service import openai_embeddings
from src.utils.config import settings

chroma_client = chromadb.HttpClient(host=settings.CHROMA_PUBLIC_URL)

vector_store = Chroma(
    client=chroma_client,
    collection_name="focus",
    embedding_function=openai_embeddings,
)
