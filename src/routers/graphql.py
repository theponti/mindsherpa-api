# GraphQL endpoint
from fastapi import Request
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Any, AsyncGenerator

from src.schema import Query
from src.services.supabase import get_current_user


async def get_context(request: Request) -> AsyncGenerator[dict[str, Any], None]:
    auth_header = request.headers.get("Authorization")
    current_user = None
    if auth_header:
        token = auth_header.split(" ")[1]
        current_user = await get_current_user(token)
    yield {"request": request, "current_user": current_user}


schema = strawberry.Schema(query=Query)

graphql_router = GraphQLRouter(schema=schema, context_getter=get_context)
