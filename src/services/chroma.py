import chromadb
from chromadb import Collection

from src.utils.config import settings

try:
    chroma_client = chromadb.HttpClient(host=settings.CHROMA_PUBLIC_URL)
except Exception as e:
    print(f"Error connecting to chromadb: {e}")
    chroma_client = None


def get_image_collection() -> Collection | None:
    if chroma_client is None:
        return None
    return chroma_client.get_or_create_collection("images")
