from typing import Any, AsyncGenerator

import strawberry
from strawberry.fastapi import GraphQLRouter

from src.schemas.mutation import Mutation
from src.schemas.query import Query
from src.utils.context import CurrentProfile, CurrentUser, SessionDep


async def get_context(
    db: SessionDep, user: CurrentUser, profile: CurrentProfile
) -> AsyncGenerator[dict[str, Any], None]:
    yield {
        "user": user,
        "profile": profile,
        "session": db,
    }


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(schema=schema, context_getter=get_context)
