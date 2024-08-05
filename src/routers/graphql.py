# GraphQL endpoint
from functools import cached_property
from fastapi import Request
import strawberry
from strawberry.fastapi import GraphQLRouter, BaseContext
from typing import Any, AsyncGenerator


from src.schemas.query import Query
from src.schemas.mutation import Mutation
from src.schemas.types import User
from src.services.auth import get_current_user


class Context(BaseContext):
    @cached_property
    def user(self) -> User | None:
        if not self.request:
            return None

        authorization = self.request.headers.get("Authorization", None)
        if not authorization:
            return None
        token = authorization.split(" ")[1]
        return get_current_user(token)


async def get_context(request: Request) -> AsyncGenerator[dict[str, Any], None]:
    auth_header = request.headers.get("Authorization")
    current_user = None

    if auth_header:
        token = auth_header.split(" ")[1]
        current_user = get_current_user(token)

    yield {"request": request, "current_user": current_user}


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(schema=schema, context_getter=get_context)
