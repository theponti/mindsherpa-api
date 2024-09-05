from typing import List

import strawberry

from src.resolvers.chat_resolvers import MessageOutput, send_chat_message


@strawberry.type
class Mutation:
    send_chat_message: List[MessageOutput] = strawberry.field(resolver=send_chat_message)
