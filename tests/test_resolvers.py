import pytest
from sqlalchemy.orm import Session

from src.data.db import get_db
from src.data.models.user import User as UserModel
from test_setup import test_client


def create_test_user(db: Session, name: str, email: str):
    user = UserModel(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="module")
def db_session():
    db = next(get_db())
    yield db
    db.close()


def test_get_users(test_client, db_session):
    # Create test users
    create_test_user(db_session, "John Doe", "john@example.com")
    create_test_user(db_session, "Jane Doe", "jane@example.com")

    query = """
    query {
        users {
            id
            name
            email
        }
    }
    """
    response = test_client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert len(data["data"]["users"]) == 2


def test_get_user(test_client, db_session):
    # Create a test user
    user = create_test_user(db_session, "John Doe", "john@example.com")

    query = f"""
    query {{
        user(id: {user.id}) {{
            id
            name
            email
        }}
    }}
    """
    response = test_client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["user"]["id"] == user.id
    assert data["data"]["user"]["name"] == user.name
    assert data["data"]["user"]["email"] == user.email
