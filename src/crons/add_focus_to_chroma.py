import traceback

from src.data.db import SessionLocal
from src.data.focus_repository import add_focus_items_to_vector_store
from src.data.models.focus import Focus


def add_focus_to_vector_store_job():
    session = SessionLocal()

    try:
        # Fetch all focus items that are not in the vector store yet
        focus_items = session.query(Focus).filter(Focus.in_vector_store.is_(False)).all()

        if not focus_items:
            print("No new focus items to add to the vector store.")
            return

        focus_items = add_focus_items_to_vector_store(focus_items=focus_items)
        if not focus_items:
            return

        session.add_all(focus_items)
        session.flush()
        session.commit()
    except Exception as e:
        traceback.print_exc()
        print(f"Error adding focus items to vector store: {e}")
    finally:
        session.close()
