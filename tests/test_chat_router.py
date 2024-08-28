from uuid import uuid4

import pytest

from src.data.models.chat import Chat, ChatState, Message
from src.data.models.user import Profile, User
from src.resolvers.tokens import create_access_token

# Remove the TestClient setup, as it's now in the fixture

access_token = create_access_token({"sub": "1234567890", "name": "Test User", "email": "test@example.com"})
AUTH_HEADERS = {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def user(db_session):
    user = User(id=uuid4(), email="test@example.com")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def profile(db_session, user):
    profile = Profile(id=uuid4(), user_id=user.id, provider="google")
    db_session.add(profile)
    db_session.commit()
    return profile


def test_get_active_chat(client, user, profile, db_session):
    chat = Chat(profile_id=profile.id, state=ChatState.ACTIVE.value)
    db_session.add(chat)
    db_session.commit()

    response = client.get("/chat/active", headers={"Au": str(user.id)})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_active_chat_not_found(client, user, profile):
    response = client.get("/chat/active", headers=AUTH_HEADERS)
    assert response.status_code == 404
    assert "Chat not found" in response.json()["detail"]


def test_end_chat(client, user, profile, db_session):
    chat = Chat(profile_id=profile.id, state=ChatState.ACTIVE.value)
    db_session.add(chat)
    db_session.commit()

    response = client.post("/chat/end", json={"chat_id": str(chat.id)}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    db_session.refresh(chat)
    assert chat.state == ChatState.ENDED.value


def test_end_chat_not_found(client, user):
    non_existent_chat_id = uuid4()
    response = client.post("/chat/end", json={"chat_id": str(non_existent_chat_id)}, headers=AUTH_HEADERS)
    assert response.status_code == 404
    assert "Chat not found" in response.json()["detail"]


def test_get_chat(client, user, profile, db_session):
    chat = Chat(profile_id=profile.id)
    db_session.add(chat)
    for _ in range(3):
        message = Message(chat_id=chat.id, message="Test message")
        db_session.add(message)
    db_session.commit()

    response = client.get(f"/chat/{chat.id}", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3


def test_get_chat_not_found(client, user):
    non_existent_chat_id = uuid4()
    response = client.get(f"/chat/{non_existent_chat_id}", headers=AUTH_HEADERS)
    assert response.status_code == 404
    assert "Chat not found" in response.json()["detail"]


def test_unauthorized_access(client):
    endpoints = ["/chat/active", "/chat/end", f"/chat/{uuid4()}"]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["detail"]
