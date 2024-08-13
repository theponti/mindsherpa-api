import strawberry
from typing import List

from src.resolvers.user_resolvers import (
    AuthPayload,
    CreateUserPayload,
    create_user_and_profile,
    save_apple_user,
    update_profile,
)
from src.resolvers.chat_resolvers import send_chat_message
from src.resolvers.focus import (
    delete_focus_item,
    DeleteFocusItemOutput
)
from src.resolvers.note_resolvers import (
    create_note, 
    CreateNoteOutput,
    upload_voice_note, 
    UploadVoiceNoteResponse
)
from src.schemas.types import Message, UpdateProfilePayload


@strawberry.type
class Mutation:
    send_chat_message: List[Message] = strawberry.field(resolver=send_chat_message)

    # Notes
    create_note: CreateNoteOutput = strawberry.field(resolver=create_note)
    upload_voice_note: UploadVoiceNoteResponse = strawberry.field(resolver=upload_voice_note)
    
    # Focus Items
    delete_focus_item: DeleteFocusItemOutput = strawberry.field(resolver=delete_focus_item)
                                                                  
    # Users
    create_user: CreateUserPayload = strawberry.field(resolver=create_user_and_profile)
    save_apple_user: AuthPayload = strawberry.field(resolver=save_apple_user)
    update_profile: UpdateProfilePayload = strawberry.field(resolver=update_profile)