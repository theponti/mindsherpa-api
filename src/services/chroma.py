import os

import chromadb
from chromadb import Collection

CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")

if not CHROMA_HOST or not CHROMA_PORT:
    raise ValueError("CHROMA_HOST and CHROMA_PORT environment variables are not set")

try:
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
except Exception as e:
    print(f"Error connecting to chromadb: {e}")
    chroma_client = None


def get_image_collection() -> Collection | None:
    if chroma_client is None:
        return None
    return chroma_client.get_or_create_collection("images")
