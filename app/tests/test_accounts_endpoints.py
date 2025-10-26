# app/tests/test_accounts_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

def test_accounts_get():
    client = TestClient(app)
    response = client.get("/accounts/")
    assert response.status_code in [200, 401]  # 401 = no token

def test_create_account():
    client = TestClient(app)
    response = client.post("/accounts/")
    assert response.status_code in [200, 401, 422]