# app/tests/test_auth_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

def test_login_endpoint_exists():
    client = TestClient(app)
    response = client.post("/auth/login")
    assert response.status_code in [200, 422]  # 422 = validation error (OK)

def test_register_endpoint_exists():
    client = TestClient(app)
    response = client.post("/auth/register")
    assert response.status_code in [200, 422, 401]  # 401 = auth required