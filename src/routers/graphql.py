from fastapi import Request
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Any, AsyncGenerator
from src.data.db import SessionLocal


from src.resolvers.user_resolvers import get_current_user
from src.schemas.query import Query
from src.schemas.mutation import Mutation


async def get_context(request: Request) -> AsyncGenerator[dict[str, Any], None]:
    session = SessionLocal()
    auth_header = request.headers.get("Authorization")
    current_user = None
    profile = None

    if auth_header:
        token = auth_header.split(" ")[1]
        current_user, profile = get_current_user(session, token)

    try:
        if current_user and profile:
            print(
                "user",
                {
                    "user": current_user,
                    "profile": profile,
                },
            )
            yield {
                "request": request,
                "user": current_user,
                "profile": profile,
                "session": session,
            }
        else:
            yield {"request": request, "session": session}
    finally:
        session.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(schema=schema, context_getter=get_context)
