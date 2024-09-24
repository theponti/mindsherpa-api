import traceback

from langchain_core.documents import Document

from src.data.db import SessionLocal
from src.data.focus_repository import get_focus_item_by_id
from src.data.models.focus import Focus
from src.services import chroma_service
from src.services.keywords.keywords_service import get_query_keywords
from src.utils.logger import logger


def delete_none_ids_from_chroma():
    try:
        print("Deleting None IDs from Chroma")
        result = chroma_service.focus_collection.get(ids=["None"])
        documents = result["documents"]
        print("Got documents")
        if documents:
            if len(documents) > 0:
                logger.info("No None IDs to delete from Chroma.")
                return

            logger.info(f"Deleting None IDs from Chroma: {len(documents)}")
            chroma_service.focus_collection.delete(ids=["None"])
            logger.info(f"{len(documents)} None IDs deleted from Chroma.")
    except Exception as e:
        print("Problem")
        traceback.print_exc()
        logger.error(f"Error deleting None IDs from Chroma: {e}")


def refresh_focus_from_chroma():
    session = SessionLocal()
    print("Refreshing Focus from Chroma")
    try:
        focus_items = session.query(Focus).filter(Focus.in_vector_store.is_(False)).all()
        if not focus_items:
            logger.info("No focus items to refresh from the vector store.")
            return

        print(f"Focus items: {len(focus_items)}")
        docs = chroma_service.vector_store.get(ids=[str(focus_item.id) for focus_item in focus_items])
        print(f"Docs: {len(docs['documents'])}")
        logger.info(f"Docs: {len(docs['documents'])}")
        completed_ids = []
        for doc, doc_id, metadata in zip(docs["documents"], docs["ids"], docs["metadatas"]):
            keywords = get_query_keywords(doc)
            keyword_str = ",".join(keywords)
            focus_item = get_focus_item_by_id(focus_items=focus_items, id=doc_id)
            page_content = focus_item.text
            chroma_service.vector_store.update_document(
                document_id=doc_id,
                document=Document(metadata=metadata, page_content=f"{page_content} \n\n {keyword_str}"),
            )
            completed_ids.append(doc_id)
            logger.info(f"Updated {doc_id} with keywords: {keyword_str}")

        session.query(Focus).filter(Focus.id.in_(completed_ids)).update({"in_vector_store": True})
        session.commit()
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error refreshing focus items from vector store: {e}")
