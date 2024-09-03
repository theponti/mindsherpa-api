import strawberry


@strawberry.type
class NoteOutput:
    id: str
    content: str
    created_at: str
