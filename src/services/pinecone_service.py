import time

from pinecone import Pinecone

from src.data.db import SessionLocal
from src.data.models.focus import Focus
from src.utils.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

euclidean_index_name = "mindsherpa-dev-eclidean"
index_name = "mindsherpa-focus"

euclidean_index = pc.Index(euclidean_index_name)
focus_index = pc.Index(index_name)


def upsert_focus_to_pinecone():
    session = SessionLocal()
    focus_items = session.query(Focus).filter(Focus.in_vector_store.is_(False)).all()

    data = [{"id": str(focus_item.id), "text": focus_item.text} for focus_item in focus_items]

    if len(data) == 0:
        return

    inputs = [d["text"] for d in data]
    embeddings = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=inputs,
        parameters={"input_type": "passage", "truncate": "END"},
    )

    # Wait for the index to be ready
    while not pc.describe_index(euclidean_index_name).status["ready"]:
        time.sleep(1)

    vectors = []
    for d, e in zip(data, embeddings):
        vectors.append({"id": d["id"], "values": e["values"], "metadata": {"text": d["text"]}})

    euclidean_index.upsert(vectors=vectors, namespace="ns1")

    for focus_item in focus_items:
        focus_item.in_vector_store = True

    session.add_all(focus_items)
    session.commit()
    session.flush()
    session.close()
