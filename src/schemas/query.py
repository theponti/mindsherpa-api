from typing import List
import strawberry
from src.data.db import Session


from src.data.models import Chat as ChatModel
from src.services.notebooks import get_notebooks, get_user_notes
from src.schemas.types import Chat, Note, Notebook, User


async def chats(self, info: strawberry.Info) -> List[Chat]:
    session = Session()
    chats = (
        session.query(ChatModel)
        .filter(ChatModel.user_id == info.context.get("current_user").id)
        .all()
    )
    return [Chat(**chat.__dict__) for chat in chats]


async def current_user(self, info: strawberry.Info) -> User:
    current_user = info.context.get("current_user")

    if not current_user:
        raise Exception("Unauthorized")

    return User(id=current_user.id, email=current_user.email)


@strawberry.type
class Query:
    chats: List[Chat] = strawberry.field(resolver=chats)
    current_user: User = strawberry.field(resolver=current_user)
    notebooks: List[Notebook] = strawberry.field(resolver=get_notebooks)
    notes: List[Note] = strawberry.field(resolver=get_user_notes)
