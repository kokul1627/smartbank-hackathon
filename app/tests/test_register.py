# app/tests/test_register.py
import pytest
from app.utils.password import hash_password  # ← CORRECT NAME

def test_register_customer_by_admin(client):
    db = client.app.state.db

    # Insert admin using sync-safe method
    from asyncio import get_event_loop
    loop = get_event_loop()
    loop.run_until_complete(db.users.insert_one({
        "name": "Admin",
        "email": "admin@bank.com",
        "password": hash_password("Admin123!"),  # ← CORRECT FUNCTION
        "role": "admin"
    }))

    # Login
    login = client.post("/auth/login", json={
        "email": "admin@bank.com",
        "password": "Admin123!"
    })
    assert login.status_code == 200, f"Login failed: {login.json()}"
    token = login.json()["access_token"]

    # Register customer
    response = client.post("/auth/register", json={
        "name": "Ravi",
        "email": "admin@bank.com",
        "password": "Admin123!",
        "role": "customer"
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201, f"Register failed: {response.json()}"
    data = response.json()["user"]
    assert data["email"] == "admin@bank.com"
    assert data["role"] == "customer"