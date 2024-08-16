from fastapi import Request
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Any, AsyncGenerator

from src.schemas.query import Query
from src.schemas.mutation import Mutation

async def get_context(request: Request) -> AsyncGenerator[dict[str, Any], None]:
    yield {
        "request": request,
        "user": request.state.user,
        "profile": request.state.profile,
        "session": request.state.session,
    }


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(schema=schema, context_getter=get_context)
