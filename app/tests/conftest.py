# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from mongomock_motor import AsyncMongoMockClient

@pytest.fixture
def client():
    mock_client = AsyncMongoMockClient()
    db = mock_client["test_bankdb"]
    app.state.db = db

    async def override_get_database():
        return db

    from app.config import get_database
    app.dependency_overrides[get_database] = override_get_database

    with TestClient(app) as test_client:
        yield test_client