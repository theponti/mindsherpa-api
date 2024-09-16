import traceback
import uuid
from datetime import datetime
from typing import List, Optional

from langchain_core.documents import Document
from sqlalchemy.orm import Session

from src.data.db import SessionLocal
from src.data.models.focus import Focus, FocusItemBase, FocusItemBaseV2, FocusState
from src.services import chroma

# Crons

NON_TASK_TYPES = ["chat", "feeling", "request", "question"]


def add_focus_items_to_vector_store(focus_items: List[Focus]) -> List[Focus] | None:
    if not focus_items or len(focus_items) == 0:
        return None

    try:
        print(f"Adding {len(focus_items)} focus items to vector store...")
        documents = [Document(page_content=item.text, metadata=item.to_json()) for item in focus_items]
        uuids = [str(uuid.uuid4()) for _ in range(len(documents))]
        ids = chroma.vector_store.add_documents(documents=documents, ids=uuids)

        for item in focus_items:
            item.in_vector_store = True

        print(f"Added focus {len(ids)} items to vector store:", ids)
        return focus_items
    except Exception as e:
        traceback.print_exc()
        print(f"Error adding documents to Chroma: {e}")
        return None


def create_focus_items(
    focus_items: List[FocusItemBaseV2] | List[FocusItemBase], profile_id: uuid.UUID, session: Session
) -> List[Focus]:
    filtered_items = [item for item in focus_items if item.type not in NON_TASK_TYPES]
    if len(filtered_items) == 0:
        return []

    try:
        created_items = [
            Focus(
                text=item.text,
                type=item.type,
                task_size=item.task_size,
                category=item.category,
                priority=item.priority,
                sentiment=item.sentiment,
                due_date=item.due_date,
                profile_id=profile_id,
            )
            for item in focus_items
        ]

        created_items_vector = add_focus_items_to_vector_store(focus_items=created_items)
        if created_items_vector:
            session.add_all(created_items_vector)
            session.flush()
            session.commit()
            return created_items_vector

        session.add_all(created_items)
        session.flush()
        session.commit()
        return created_items
    except Exception as e:
        print(f"Error creating focus items: {e}")
        return []


def search_focus_items(
    keyword: str,
    due_on: Optional[datetime],
    due_after: Optional[datetime],
    due_before: Optional[datetime],
    status: Optional[FocusState],
    profile_id: uuid.UUID,
) -> List[Focus]:
    session = SessionLocal()
    ids = []

    if len(keyword) > 0:
        results = chroma.vector_store.similarity_search(query=keyword, filter={"profile_id": str(profile_id)})
        ids = [res.metadata["id"] for res in results]

    try:
        query = session.query(Focus)

        if len(ids) > 0:
            query = query.filter(Focus.id.in_(ids))

        if due_on:
            query = query.filter(Focus.due_date == due_on)
        else:
            # `due_after` and `due_before` can be used together because
            # the user may want to search for tasks that are due between two dates
            if due_after is not None:
                query = query.filter(Focus.due_date >= due_after)

            if due_before is not None:
                query = query.filter(Focus.due_date <= due_before)

        if status == "active" or status == FocusState.backlog.value:
            query = query.filter(Focus.state.in_([FocusState.backlog.value, FocusState.active.value]))
        elif status:
            query = query.filter(Focus.state == status.value)

        focus_items = query.all()

        return focus_items
    except Exception as e:
        print(f"Error searching focus items: {e}")
        return []
