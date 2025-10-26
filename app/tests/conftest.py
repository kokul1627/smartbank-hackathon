# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from mongomock_motor import AsyncMongoMockClient

@pytest.fixture
def client():
    mock_client = AsyncMongoMockClient()
    db = mock_client["test_bankdb"]
    app.state.db = db  # ← THIS IS THE KEY LINE

    async def override_get_db():
        return db

    from app.config import get_database
    app.dependency_overrides[get_database] = override_get_db

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
