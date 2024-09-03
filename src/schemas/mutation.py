from typing import List

import strawberry

from src.resolvers.chat_resolvers import MessageOutput, send_chat_message
from src.resolvers.user_resolvers import (
    AuthPayload,
    UpdateProfilePayload,
    save_apple_user,
    update_profile,
)


@strawberry.type
class Mutation:
    send_chat_message: List[MessageOutput] = strawberry.field(resolver=send_chat_message)

    # Users
    save_apple_user: AuthPayload = strawberry.field(resolver=save_apple_user)
    update_profile: UpdateProfilePayload = strawberry.field(resolver=update_profile)
