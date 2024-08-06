import io
import profile
import strawberry
from strawberry.file_uploads import Upload
from typing import List
from src.data.models import Note

from src.resolvers.user_resolvers import (
    AuthPayload,
    CreateUserPayload,
    create_user_and_profile,
    refresh_token,
    save_apple_user,
    update_profile,
)
from src.resolvers.chat_resolvers import send_chat_message
from src.schemas.types import Message, UpdateProfilePayload, CreateNote
from src.services.media import transcribe_audio, TranscribeAudioResponse
from src.utils.logger import logger


@strawberry.type
class UploadVoiceNoteResponse(TranscribeAudioResponse):
    pass


@strawberry.input
class CreateNoteInput:
    content: str


@strawberry.type
class Mutation:
    create_user: CreateUserPayload = strawberry.field(resolver=create_user_and_profile)
    save_apple_user: AuthPayload = strawberry.field(resolver=save_apple_user)
    refresh_token: AuthPayload = strawberry.field(resolver=refresh_token)
    update_profile: UpdateProfilePayload = strawberry.field(resolver=update_profile)
    send_chat_message: List[Message] = strawberry.field(resolver=send_chat_message)

    @strawberry.field
    async def create_note(
        self, info: strawberry.Info, input: CreateNoteInput
    ) -> CreateNote:
        current_user = info.context.get("user")
        if not current_user:
            raise Exception("Unauthorized")

        session = info.context.get("session")
        profile_id = info.context.get("profile").id
        note = Note(content=input.content, profile_id=profile_id)
        session.add(note)
        session.commit()

        note_dict = note.__dict__
        return CreateNote(
            id=note_dict["id"],
            content=note_dict["content"],
            created_at=note_dict["created_at"],
        )

    @strawberry.field
    async def upload_voice_note(
        self, info: strawberry.Info, audio_file: Upload, chat_id: int
    ) -> UploadVoiceNoteResponse:
        current_user = info.context.get("user")
        if not current_user:
            raise Exception("Unauthorized")

        transcription = transcribe_audio(io.BytesIO(audio_file), model="openai")
        if transcription.error or not transcription.text:
            raise Exception("Transcription failed")

        logger.info(f"Transcription: {transcription.text}")
        return UploadVoiceNoteResponse(text=transcription.text, error=None)


# @strawberry.type
# class Subscription:
#     @strawberry.subscription
#     async def user_account_changed(self, info: Info) -> str:
#         # Get the current user from the context
#         user_id = info.context.get("user_id")
#         if not user_id:
#             raise ValueError("Not authenticated")

#         async with broadcast.subscribe(channel="user_changes") as subscriber:
#             async for event in subscriber:
#                 if event.message == str(user_id):
#                     yield event.message
