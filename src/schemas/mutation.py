from typing import List

import strawberry

from src.resolvers.chat_resolvers import MessageOutput, send_chat_message
from src.resolvers.focus import DeleteFocusItemOutput, delete_focus_item
from src.resolvers.user_resolvers import (
    AuthPayload,
    CreateUserPayload,
    create_user_and_profile,
    save_apple_user,
    update_profile,
)
from src.schemas.types import UpdateProfilePayload


@strawberry.type
class Mutation:
    send_chat_message: List[MessageOutput] = strawberry.field(resolver=send_chat_message)

    # Focus Items
    delete_focus_item: DeleteFocusItemOutput = strawberry.field(resolver=delete_focus_item)

    # Users
    create_user: CreateUserPayload = strawberry.field(resolver=create_user_and_profile)
    save_apple_user: AuthPayload = strawberry.field(resolver=save_apple_user)
    update_profile: UpdateProfilePayload = strawberry.field(resolver=update_profile)
