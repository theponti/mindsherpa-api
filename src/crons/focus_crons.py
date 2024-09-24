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
        collection = chroma_service.get_collection("focus")
        if not collection:
            return

        result = collection.get(ids=["None"])
        documents = result["documents"]
        if documents:
            if len(documents) > 0:
                logger.info("No None IDs to delete from Chroma.")
                return

            logger.info(f"Deleting None IDs from Chroma: {len(documents)}")
            collection.delete(ids=["None"])
            logger.info(f"{len(documents)} None IDs deleted from Chroma.")
    except Exception as e:
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

        logger.info(f"Adding {len(focus_items)} focus items to Chroma")
        docs = chroma_service.vector_store.get(ids=[str(focus_item.id) for focus_item in focus_items])
        if len(docs["documents"]) == 0:
            chroma_service.clear_focus_items_from_vector_store()
            for focus_item in focus_items:
                keyword_str = ",".join(get_query_keywords(focus_item.text))
                chroma_service.vector_store.add_documents(
                    documents=[
                        Document(
                            page_content=f"{focus_item.text} \n\n {keyword_str}",
                            metadata={"keywords": keyword_str},
                        )
                    ],
                    ids=[str(focus_item.id)],
                )
                logger.info(f"Added {focus_item.id} to Chroma")
            session.query(Focus).filter(Focus.id.in_([focus_item.id for focus_item in focus_items])).update(
                {"in_vector_store": True}
            )
            session.commit()
            return

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
