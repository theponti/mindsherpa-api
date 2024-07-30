import typing
import strawberry

from src.resolvers.notebooks import get_notebooks, get_notes


@strawberry.type
class Notebook:
    title: str
    id: str
    created_at: str
    updated_at: str
    user_id: str


@strawberry.type
class Note:
    title: str
    id: str
    created_at: str
    updated_at: str
    user_id: str
    notebook_id: str


@strawberry.type
class User:
    id: str
    email: str | None


@strawberry.type
class Query:
    notebooks: typing.List[Notebook] = strawberry.field(resolver=get_notebooks)
    notes: typing.List[Note] = strawberry.field(resolver=get_notes)

    @strawberry.field
    async def protected_route(self, info: strawberry.Info) -> User:
        current_user = info.context.get("current_user")

        if not current_user:
            raise Exception("Unauthorized")

        return User(id=current_user.id, email=current_user.email)
